import argparse
from pathlib import Path

from common import execute


def run():
    parser = argparse.ArgumentParser(description="Parse and validate a CIF structure.")
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    from crystal_cif import inspect_cif

    structure = inspect_cif(args.input.read_text(encoding="utf-8-sig"))
    return {"status": "completed", "formula": structure.composition.reduced_formula,
            "sites": len(structure), "volume_A3": structure.volume}


if __name__ == "__main__":
    raise SystemExit(execute(run))
