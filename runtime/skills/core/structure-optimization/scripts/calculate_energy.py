import math

from common import execute, output_parser, write_json
from matter_model import arguments, calculator, read_cif


def run():
    parser = output_parser("Calculate energy and atomic forces with MatterSim")
    arguments(parser)
    args = parser.parse_args()
    atoms = read_cif(args.input)
    atoms.calc = calculator(args.model_path, args.device)
    energy = float(atoms.get_potential_energy())
    forces = atoms.get_forces().tolist()
    if not math.isfinite(energy) or any(not math.isfinite(x) for row in forces for x in row):
        raise ValueError("Potential produced a nonfinite energy or force")
    result = {"status": "completed", "formula": atoms.get_chemical_formula(),
              "sites": len(atoms), "energy_eV": energy, "energy_per_atom_eV": energy / len(atoms),
              "forces_eV_A": forces, "input": str(args.input.resolve()), "device": args.device,
              "checkpoint": str(args.model_path.resolve())}
    data = write_json(args.out_dir / "energy.json", result)
    return {"status": "completed", "energy_eV": energy, "sites": len(atoms),
            "data": str(data.resolve())}


if __name__ == "__main__":
    raise SystemExit(execute(run))
