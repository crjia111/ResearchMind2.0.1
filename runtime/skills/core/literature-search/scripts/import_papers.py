import hashlib
from pathlib import Path

from common import execute, output_parser, write_text
from document_text import extract
from literature.catalog import save


def run():
    parser = output_parser("Import PDF, DOCX, HTML, Markdown, or text into a paper catalog")
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    papers, failures = [], []
    for path in args.input:
        try:
            content = path.read_bytes()
            text = extract(content, path.suffix.lower())
            if not text.strip():
                raise ValueError("No extractable text")
            ident = hashlib.sha256(content).hexdigest()[:24]
            output = f"text/{ident}.txt"
            write_text(args.out_dir / output, text)
            papers.append({"paper_id": ident, "title": path.stem, "source": "upload",
                           "content_file": output, "evidence": "fulltext",
                           "abstract": text[:1000]})
        except Exception as exc:
            failures.append({"file": str(path), "message": str(exc)})
    status = "partial" if failures and papers else "failed" if failures else "completed"
    return save(args.out_dir, papers, status=status, failures=failures)


if __name__ == "__main__":
    raise SystemExit(execute(run))
