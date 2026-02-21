from textwrap import indent
import xml.etree.ElementTree as ET

# TODO: have a look at https://github.com/earwig/mwparserfromhell
#       to parse the wiki markup and get plain text instead.
#       Or, consider https://github.com/attardi/wikiextractor
#       Or use pandoc to handle mediawiki markup?

SIMPLE_WIKI_XML = "simplewiki-20260201-pages-articles-multistream.xml"
MEDIAWIKI_NS = "http://www.mediawiki.org/xml/export-0.11/"

def indent(text, prefix="  "):
    if text:
        return "\n".join(prefix + line for line in text.splitlines())

count = 0
for event, elt in ET.iterparse(SIMPLE_WIKI_XML):
    assert event == "end"
    elt.tag = elt.tag.split("}")[-1] # Strip the namespace
    if elt.tag == "page":
        title = elt.find("title").text
        text = elt.find(".//text").text
        print(title)
        print(indent(text))
        elt.clear()
        count += 1
print(count)