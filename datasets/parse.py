# Python Standard Library
import re
import pandoc
from pathlib import Path
import subprocess
from typing import Generator
import xml.etree.ElementTree as ET

# Third-Party Libraries
import plumbum
import tqdm


# Constants
# ------------------------------------------------------------------------------
SIMPLE_WIKI = "simplewiki-latest-pages-articles"
NUM_PROCS = 8


# Helper Functions
# ------------------------------------------------------------------------------
def page_iterator() -> Generator[tuple[str, ET.Element], None, None]:
    for event, elt in ET.iterparse(SIMPLE_WIKI + ".xml"):
        assert event == "end"
        elt.tag = elt.tag.split("}")[-1]  # strip MediaWiki namespace
        if elt.tag == "page":
            yield event, elt


# Main Script
# ------------------------------------------------------------------------------
def sanitize(title):
    safe_title = re.sub(r'[/\\:*?"<>|]', "_", title)
    return safe_title[:100]


def mediawiki_to_plain_text(wiki_text):
    doc = pandoc.read(wiki_text, format="mediawiki")
    # doc = pandoc.read(markdown)
    Trash = tuple(
        [
            getattr(pandoc.types, name)
            for name in [
                "Figure",
                "Image",
                "Note",
                "Table",
            ]
        ]
    )
    trash = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Trash):
            trash.append(path[-1])
        elif isinstance(elt, pandoc.types.Link):
            target = elt[2]
            if target[0].startswith("Category:"):
                trash.append(path[-1])
    for holder, index in reversed(trash):
        del holder[index]

    return pandoc.write(doc, format="plain")


SUBDIRS = ["_"] + [chr(code) for code in range(ord("A"), ord("Z") + 1)]


def main() -> None:
    print("Computing the number of pages...")
    total = int(
        subprocess.check_output(["grep", "-c", "<page>", SIMPLE_WIKI + ".xml"])
        .decode()
        .strip()
    )
    Path("dump").mkdir(exist_ok=True)
    for subdir in SUBDIRS:
        subdir_path = Path("dump").joinpath(subdir)
        subdir_path.mkdir(exist_ok=True)
    for _, elt in tqdm.tqdm(page_iterator(), total=total):
        assert elt.tag == "page"
        title = elt.find("title").text
        wiki_text = elt.find(".//text").text
        if wiki_text:
            safe_title = sanitize(title)
            first_char = safe_title[0].upper()
            subdir = "_"
            if len(first_char) == 1 and "A" <= first_char <= "Z":
                subdir = first_char
            subdir_path = Path("dump").joinpath(subdir)
            output = subdir_path.joinpath(f"{safe_title}.mediawiki")
            output.write_text(wiki_text)
        elt.clear()
    for subdir in SUBDIRS:
        subdir = Path("dump") / subdir
        files = list(subdir.glob("*.mediawiki"))
        for file in tqdm.tqdm(files, desc=subdir, total=len(files)):
            wiki_text = file.open(encoding="utf-8").read()
            try:
                plain_text = mediawiki_to_plain_text(wiki_text)
            except plumbum.commands.processes.ProcessExecutionError:
                plain_text = None
            if plain_text is not None:
                file.with_suffix(".txt").write_text(plain_text)


# Entry point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
