import argparse
import csv
from pathlib import Path

from common import execute, write_csv


def run():
    parser = argparse.ArgumentParser(description="Remove blank rows and unresolved paper IDs from a CSV")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Without an output path, report counts only")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields:
        raise ValueError("CSV requires a header")
    result = [row for row in rows if any(str(value or "").strip() for value in row.values())
              and "unknown" not in str(row.get("ID", row.get("paper_id", ""))).lower()]
    if args.output:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Use a distinct output path to preserve your input")
        write_csv(args.output, result, fields)
    return {"status": "completed", "rows": len(rows), "valid": len(result),
            "removed": len(rows) - len(result)}


if __name__ == "__main__":
    raise SystemExit(execute(run))
