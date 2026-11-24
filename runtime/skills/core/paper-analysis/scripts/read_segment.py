import argparse
from pathlib import Path

from common import execute


def run():
    parser = argparse.ArgumentParser(description="Read text by Unicode character offsets")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--length", type=int)
    args = parser.parse_args()
    text = args.input.read_text(encoding="utf-8-sig")
    if not 0 <= args.start <= len(text):
        raise ValueError("start must be inside the text or at its end")
    if args.length is not None and args.length <= 0:
        raise ValueError("length must be positive")
    end = len(text) if args.length is None else min(len(text), args.start + args.length)
    return {"status": "completed", "text": text[args.start:end], "start": args.start,
            "length": end - args.start, "next_start": end, "has_more": end < len(text),
            "total_length": len(text)}


if __name__ == "__main__":
    raise SystemExit(execute(run))
