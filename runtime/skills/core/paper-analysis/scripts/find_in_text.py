import argparse
from itertools import islice
from pathlib import Path
import re

from common import execute


def run():
    parser = argparse.ArgumentParser(description="Locate literal text and return matching excerpts")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--term", required=True)
    parser.add_argument("--context", type=int, default=180)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if not args.term or not 0 <= args.context <= 10000 or not 1 <= args.limit <= 1000:
        raise ValueError("Supply a term, context from 0–10000 and limit from 1–1000")
    text = args.input.read_text(encoding="utf-8-sig")
    matches = [
        {"start": match.start(), "end": match.end(),
         "excerpt": text[max(0, match.start() - args.context):match.end() + args.context]}
        for match in islice(re.finditer(re.escape(args.term), text, re.IGNORECASE), args.limit)
    ]
    return {"status": "completed" if matches else "no_results", "matches": matches}


if __name__ == "__main__":
    raise SystemExit(execute(run))
