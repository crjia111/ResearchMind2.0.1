"""Small file and CLI helpers bundled inside each independent skill."""
import argparse
import csv
from contextlib import nullcontext, redirect_stdout
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def output_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser


def require_range(value, low, high, name):
    if not low <= value <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return value


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_bytes(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path


def write_text(path, content):
    return write_bytes(path, content.encode("utf-8"))


def write_json(path, value):
    return write_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_csv(path, rows, fields=None):
    from io import StringIO

    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({
            field: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
            for field, value in row.items()
        })
    return write_text(path, buffer.getvalue())


def execute(task):
    try:
        logging = nullcontext() if any(arg in {"-h", "--help"} for arg in sys.argv[1:]) else redirect_stdout(sys.stderr)
        with logging:
            result = task()
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return {"partial": 3, "failed": 1}.get(result.get("status"), 0)
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=True))
        return 1
