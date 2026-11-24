"""Load and validate a local ASE structure and an explicit MatterSim model."""
import argparse
from math import isfinite
from pathlib import Path


def arguments(parser):
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model-path", type=Path,
                        default=Path(__file__).resolve().parents[1] / "models/mattersim-v1.0.0-1M.pth",
                        help="Override the bundled model location")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")


def read_cif(path):
    from ase.io import read

    atoms = read(path, format="cif")
    if not len(atoms) or not atoms.pbc.all() or not isfinite(atoms.get_volume()) or atoms.get_volume() <= 0:
        raise ValueError("Expected a nonempty periodic CIF with a finite positive volume")
    if not all(isfinite(value) for row in atoms.positions for value in row):
        raise ValueError("Atomic coordinates must be finite")
    return atoms


def calculator(path, device):
    if not path.is_file():
        raise FileNotFoundError(f"MatterSim checkpoint missing: {path}")
    from mattersim.forcefield import MatterSimCalculator

    return MatterSimCalculator.from_checkpoint(str(path.resolve()), device=device, load_training_state=False)


def validate():
    parser = argparse.ArgumentParser(description="Parse a periodic CIF and report its composition")
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    atoms = read_cif(args.input)
    return {"status": "completed", "formula": atoms.get_chemical_formula(),
            "sites": len(atoms), "volume_A3": atoms.get_volume()}
