"""Extract text from input or retrieved documents."""
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path


class HtmlText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def extract(content, suffix):
    if suffix == ".pdf" or content.startswith(b"%PDF-"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    if suffix == ".docx":
        from docx import Document

        return "\n".join(p.text for p in Document(BytesIO(content)).paragraphs)
    value = content.decode("utf-8-sig")
    if suffix in {".html", ".htm"}:
        parser = HtmlText()
        parser.feed(value)
        return "\n".join(parser.parts)
    if suffix not in {".txt", ".md", ".csv"}:
        raise ValueError(f"Unsupported document type: {suffix}")
    return value


def read_document(path: Path):
    return extract(path.read_bytes(), path.suffix.lower())
