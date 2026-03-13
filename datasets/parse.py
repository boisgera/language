# Python Standard Library
import io
import json
from typing import Generator
import xml.etree.ElementTree as ET

# Third-Party Libraries
import mwparserfromhell
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
def main() -> None:
    pages = {}
    for _, elt in tqdm.tqdm(page_iterator()):
        assert elt.tag == "page"
        title = elt.find("title").text

        wiki_text = elt.find(".//text").text
        text = mwparserfromhell.parse(wiki_text)
        to_remove = [
            link for link in text.filter_wikilinks(
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
