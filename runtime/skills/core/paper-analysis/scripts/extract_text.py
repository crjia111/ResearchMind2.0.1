import hashlib
from pathlib import Path

from common import execute, output_parser, write_json, write_text
from document_text import read_document
from evidence import obtain, records


def run():
    parser = output_parser("Extract a local document or batch of catalog papers")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--papers", type=Path)
    parser.add_argument("--paper-id", nargs="+")
    parser.add_argument("--require-fulltext", action="store_true")
    args = parser.parse_args()
    if args.input is not None:
        ident = hashlib.sha256(args.input.read_bytes()).hexdigest()[:24]
        text = read_document(args.input).strip()
        if not text:
            raise ValueError("No extractable text")
        path = write_text(args.out_dir / "paper.txt", text)
        rows = [{"paper_id": ident, "title": args.input.stem, "source": "upload",
                 "evidence": "fulltext", "content_file": path.name,
                 "content_source": str(args.input.resolve()), "characters": len(text)}]
        failures, warnings = [], []
    else:
        rows, failures, warnings = [], [], []
        for index, row in enumerate(records(args.papers, args.paper_id), 1):
            try:
                text, level, source, warning = obtain(row, args.papers,
                                                      allow_summary=not args.require_fulltext)
                if args.require_fulltext and level != "fulltext":
                    raise ValueError("Available saved content is not full text")
                name = f"text/{index:04d}.txt"
                write_text(args.out_dir / name, text)
                rows.append({**row, "content_file": name, "evidence": level,
                             "content_source": source, "characters": len(text)})
                if warning:
                    warnings.append({"paper_id": row["paper_id"], "message": warning})
            except Exception as exc:
                failures.append({"paper_id": row["paper_id"], "message": str(exc)})
    status = "failed" if not rows else "partial" if failures or warnings else "completed"
    path = write_json(args.out_dir / "papers.json", {"status": status, "papers": rows,
                                                    "failures": failures, "warnings": warnings})
    return {"status": status, "paper_count": len(rows), "data": str(path.resolve()),
            "failures": failures, "warnings": warnings}


if __name__ == "__main__":
    raise SystemExit(execute(run))
