import argparse
from pathlib import Path

from common import execute, write_csv
from literature.catalog import read_catalog


def run():
    parser = argparse.ArgumentParser(description="Export a saved paper catalog as CSV")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fields", nargs="+")
    args = parser.parse_args()
    records = read_catalog(args.input)
    output = write_csv(args.output, records, args.fields)
    return {"status": "completed", "rows": len(records), "csv": str(output.resolve())}


if __name__ == "__main__":
    raise SystemExit(execute(run))
