import argparse
from pathlib import Path

from common import execute, write_bytes
from http_client import request


def run():
    parser = argparse.ArgumentParser(description="Download a public paper from an explicit URL")
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = request(args.url, raw=True)
    if args.output.suffix.lower() == ".pdf" and not data.startswith(b"%PDF-"):
        raise ValueError("The URL did not return a PDF")
    path = write_bytes(args.output, data)
    return {"status": "completed", "file": str(path.resolve()), "bytes": len(data)}


if __name__ == "__main__":
    raise SystemExit(execute(run))
