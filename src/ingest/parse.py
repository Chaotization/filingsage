"""Parse a 10-K HTML document into sections (Items).

10-K HTML is messy and varies by filer. Strategy: strip HTML to plain text with
BeautifulSoup, then split on 'Item N.' headings with a tolerant regex. This gets
~90% of filings into usable sections; perfection is not required for retrieval.
"""
import re
from bs4 import BeautifulSoup

# Sections most useful for Q&A. Extend as you like.
KEEP_ITEMS = {
    "1": "Item 1. Business",
    "1A": "Item 1A. Risk Factors",
    "3": "Item 3. Legal Proceedings",
    "7": "Item 7. Management's Discussion and Analysis",
    "7A": "Item 7A. Market Risk",
    "8": "Item 8. Financial Statements",
}

ITEM_RE = re.compile(r"\bItem\s+(\d{1,2}A?)\s*[.:\u2014-]", re.IGNORECASE)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(" ")
    return re.sub(r"\s+", " ", text)


def split_sections(text: str) -> dict[str, str]:
    """Return {section_title: body} for the Items we keep.

    Filings usually contain each Item twice (table of contents, then body);
    we keep the longest occurrence per Item, which is the body.
    """
    matches = list(ITEM_RE.finditer(text))
    spans: dict[str, str] = {}
    for i, m in enumerate(matches):
        item = m.group(1).upper()
        if item not in KEEP_ITEMS:
            continue
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if len(body) > len(spans.get(item, "")):
            spans[item] = body
    # Drop tiny fragments (TOC rows that survived)
    return {KEEP_ITEMS[k]: v for k, v in spans.items() if len(v) > 1500}
