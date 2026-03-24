# Python Standard Library
import io
import json
import re
import pandoc
from pathlib import Path
import subprocess
from typing import Generator
import xml.etree.ElementTree as ET

# Third-Party Libraries
import mwparserfromhell
import plumbum
import tqdm


# Constants
# ------------------------------------------------------------------------------
SIMPLE_WIKI = "simplewiki-latest-pages-articles"


# Helper Functions
# ------------------------------------------------------------------------------
def page_iterator() -> Generator[tuple[str, ET.Element], None, None]:
    for event, elt in ET.iterparse(SIMPLE_WIKI + ".xml"):
        assert event == "end"
        elt.tag = elt.tag.split("}")[-1]  # strip MediaWiki namespace
        if elt.tag == "page":
            yield event, elt


def json_to_text(json: dict[str], document_title=None) -> str:
    buffer = io.StringIO()
    if document_title is not None:
        buffer.write(f"{document_title}\n")
        buffer.write(80 * "=" + "\n\n")
    for title, value in json.items():
        buffer.write(f"{title}\n")
        buffer.write(80 * "-" + "\n\n")
        buffer.write(f"{value}\n\n")
    return buffer.getvalue()


# Main Script
# ------------------------------------------------------------------------------
def sanitize(title):
    safe_title = re.sub(r'[/\\:*?"<>|]', "_", title)
    return safe_title[:100]


def wiki_to_plain(wiki_text: str) -> str:
    wikicode = mwparserfromhell.parse(wiki_text)

    # Remove ref tags and their contents

    for tag in wikicode.filter_tags(
        matches=lambda t: t.tag.strip() in ("ref", "gallery", "math", "score")
    ):
        try:
            wikicode.remove(tag)
        except ValueError:
            pass

    # Remove all templates
    for tpl in wikicode.filter_templates():
        try:
            wikicode.remove(tpl)
        except ValueError:
            pass

    plain = wikicode.strip_code(normalize=True, collapse=True)

    # Headings: == Foo == -> Foo
    plain = re.sub(r"={2,}\s*(.+?)\s*={2,}", r"\1", plain)
    # List/indent markers at line start
    plain = re.sub(r"^[*#:;]+\s*", "", plain, flags=re.MULTILINE)
    # Table markup lines
    plain = re.sub(r"^\s*[|!{][|!}].*$", "", plain, flags=re.MULTILINE)
    plain = re.sub(r"^\s*\|-.*$", "", plain, flags=re.MULTILINE)
    # Leftover HTML comments
    plain = re.sub(r"<!--.*?-->", "", plain, flags=re.DOTALL)
    # Collapse blank lines (keep at most one)
    plain = re.sub(r"\n{3,}", "\n\n", plain)

    return plain.strip()


def markdown_to_plain(markdown):
    doc = pandoc.read(markdown)
    Trash = tuple([
        getattr(pandoc.types, name)
        for name in [
            "Figure",
            "Image",
            "Note",
            "Table",
        ]
    ])
    trash = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Trash):
            trash.append(path[-1])
        elif isinstance(elt, pandoc.types.Link):
            target = elt[2]
            if target[0].startswith("Category:"):
                trash.append(path[-1])
    for (holder, index) in reversed(trash):
        del holder[index]

    return pandoc.write(doc, format="plain")

# TODO: generate all mediawiki files first, then perform the conversion in 
#       parallel to get a ~8x boost.

def main() -> None:
    print("Computing the number of pages...")
    total = int(
        subprocess.check_output(["grep", "-c", "<page>", SIMPLE_WIKI + ".xml"])
        .decode()
        .strip()
    )
    Path("dump").mkdir(exist_ok=True)
    for i, (_, elt) in enumerate(tqdm.tqdm(page_iterator(), total=total)):
        #if i == 1000:
        #    break
        assert elt.tag == "page"
        title = elt.find("title").text
        wiki_text = elt.find(".//text").text
        if wiki_text:
            safe_title = sanitize(title)
            first_char = safe_title[0].upper()
            subdir = first_char if first_char.isalpha() else "_"
            subdir_path = Path("dump").joinpath(subdir)
            subdir_path.mkdir(exist_ok=True)
            output = subdir_path.joinpath(f"{safe_title}.mediawiki")
            output.write_text(wiki_text)
            result = subprocess.run(
                [
                    "pandoc",
                    "-f",
                    "mediawiki",
                    "-t",
                    "markdown",
                    "-o",
                    str(output.with_suffix(".md")),
                    str(output),
                ],
                stderr=subprocess.DEVNULL,
            )
            # output.unlink()
            if result.returncode == 0:
                markdown = open(output.with_suffix(".md"), "rt", encoding="utf-8").read()
                markdown = markdown.replace("{{-}}", "")
                try:
                    plain_text = markdown_to_plain(markdown)
                except plumbum.commands.processes.ProcessExecutionError:
                    print("error in pandoc")
                    plain_text = None
                if plain_text is not None:
                    output.with_suffix(".txt").write_text(plain_text)


        elt.clear()


def main_obsolete() -> None:
    pages = {}
    for _, elt in tqdm.tqdm(page_iterator()):
        assert elt.tag == "page"
        title = elt.find("title").text

        wiki_text = elt.find(".//text").text
        text = mwparserfromhell.parse(wiki_text)
        to_remove = [
            link
            for link in text.filter_wikilinks(
                recursive=False,  # 🐉
            )
            if link.title.lower().startswith(("file:", "image:"))
        ]
        for link in to_remove:
            text.remove(link)
        text = text.strip_code()

        pages[title] = text
        elt.clear()

    with open(SIMPLE_WIKI + "-sample" + ".json", "w") as sample_output:
        pages_sample = dict(list(pages.items())[:1000])
        json.dump(pages_sample, sample_output)
    with open(SIMPLE_WIKI + "-sample" + ".txt", "w") as sample_output:
        for title, text in pages_sample.items():
            sample_output.write(json_to_text(pages_sample, "Simple Wikipedia Sample"))

    with open(SIMPLE_WIKI + ".json", "w") as output:
        json.dump(pages, output)
    print(f"Saved {len(pages)} pages to {SIMPLE_WIKI + '.json'}")
    with open(SIMPLE_WIKI + ".txt", "w") as output:
        output.write(json_to_text(pages, "Simple Wikipedia"))


# Entry point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
