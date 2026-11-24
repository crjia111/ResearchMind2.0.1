"""Read paper records and obtain text with explicit evidence labels."""
from pathlib import Path
from urllib.parse import urlsplit

from common import read_json
from document_text import extract, read_document
from http_client import request


def records(path, ids=None):
    catalog = read_json(path)
    rows = catalog.get("papers") if isinstance(catalog, dict) else catalog
    if not isinstance(rows, list) or any(
        not isinstance(row, dict) or not row.get("paper_id") for row in rows
    ):
        raise ValueError("Expected a paper catalog containing paper_id")
    if not ids:
        return rows
    by_id = {row["paper_id"]: row for row in rows}
    unknown = set(ids) - by_id.keys()
    if unknown:
        raise ValueError("Unknown paper IDs: " + ", ".join(sorted(unknown)))
    return [by_id[ident] for ident in dict.fromkeys(ids)]


def obtain(row, catalog_path, *, allow_summary=True):
    if row.get("content_file"):
        path = catalog_path.resolve().parent / row["content_file"]
        text = read_document(path).strip()
        if text:
            return text, row.get("evidence", "fulltext"), row.get("content_source") or str(path.resolve()), None
        raise ValueError(f"Empty document: {path}")
    warning = None
    if url := row.get("pdf_url"):
        try:
            content = request(url, raw=True)
            if not content.startswith(b"%PDF-"):
                raise ValueError(f"{urlsplit(url).hostname} did not return a PDF")
            text = extract(content, ".pdf").strip()
            if text:
                return text, "fulltext", url, None
            raise ValueError("PDF has no extractable text")
        except Exception as exc:
            if not allow_summary:
                raise
            warning = str(exc)
    if allow_summary and row.get("abstract"):
        return row["abstract"], row.get("evidence", "abstract"), row.get("url"), warning
    raise ValueError("No usable full text or allowed fallback for " + row["paper_id"])
