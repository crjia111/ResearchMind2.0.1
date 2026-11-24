import math

from common import execute, output_parser, write_json
from matter_model import arguments, calculator, read_cif
from relaxation import optimize


def run():
    parser = output_parser("Compute phonon dispersion by finite displacements using MatterSim")
    arguments(parser)
    parser.add_argument("--supercell", type=int, nargs=3, default=[2, 2, 2])
    parser.add_argument("--amplitude", type=float, default=0.01, help="Displacement in angstrom")
    parser.add_argument("--relax-first", action="store_true")
    args = parser.parse_args()
    if any(not 1 <= n <= 10 for n in args.supercell):
        raise ValueError("Every supercell repeat must be from 1 to 10")
    if not math.isfinite(args.amplitude) or args.amplitude <= 0:
        raise ValueError("Displacement amplitude must be finite and positive")
    from phonon_displacements import evaluate
    from phonon_output import export

    atoms = read_cif(args.input)
    potential = calculator(args.model_path, args.device)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    relaxation = None
    if args.relax_first:
        atoms.calc = potential
        relaxation = optimize(atoms, fmax=0.03, steps=500, relax_cell=False,
                              logfile=str(args.out_dir / "relaxation.log"))
        atoms.write(args.out_dir / "relaxed.cif", format="cif")
        if not relaxation["converged"]:
            raise ValueError("Preliminary relaxation did not converge")
    phonon, count = evaluate(atoms, potential, args.supercell, args.amplitude)
    summary = {"status": "completed", "input": str(args.input.resolve()),
               "checkpoint": str(args.model_path.resolve()), "device": args.device,
               "relaxation": relaxation, "supercell": args.supercell,
               "amplitude_A": args.amplitude, "displacements": count, **export(phonon, args.out_dir)}
    write_json(args.out_dir / "phonon.json", summary)
    return summary


if __name__ == "__main__":
    raise SystemExit(execute(run))
