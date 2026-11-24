import argparse
from pathlib import Path

from common import execute, read_json, write_json
from literature.catalog import read_catalog


def run():
    parser = argparse.ArgumentParser(description="Save, read, or clear the selected paper IDs")
    parser.add_argument("--selection", type=Path, required=True)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--paper-id", nargs="+", help="IDs to select")
    operation.add_argument("--clear", action="store_true")
    parser.add_argument("--input", type=Path, help="Paper catalog to validate or expand the selection")
    args = parser.parse_args()
    papers = read_catalog(args.input) if args.input else None
    if args.paper_id and papers is None:
        parser.error("--paper-id requires --input")
    if args.paper_id or args.clear:
        ids = list(dict.fromkeys(args.paper_id or []))
        if papers is not None:
            unknown = set(ids) - {row["paper_id"] for row in papers}
            if unknown:
                raise ValueError("Unknown paper IDs: " + ", ".join(sorted(unknown)))
        write_json(args.selection, {"paper_ids": ids})
    ids = read_json(args.selection)["paper_ids"] if args.selection.exists() else []
    return {"status": "completed", "paper_ids": ids,
            "papers": [row for row in papers or [] if row["paper_id"] in ids]}


if __name__ == "__main__":
    raise SystemExit(execute(run))
