from common import execute, output_parser, write_json
from matter_model import arguments, calculator, read_cif
from relaxation import optimize


def run():
    parser = output_parser("Relax a CIF structure with MatterSim and ASE BFGS")
    arguments(parser)
    parser.add_argument("--fmax", type=float, default=0.03, help="Force threshold in eV/angstrom")
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--relax-cell", action="store_true")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    atoms = read_cif(args.input)
    atoms.calc = calculator(args.model_path, args.device)
    info = optimize(atoms, fmax=args.fmax, steps=args.max_steps, relax_cell=args.relax_cell,
                    logfile=str(args.out_dir / "relaxation.log"))
    output = args.out_dir / "relaxed.cif"
    atoms.write(output, format="cif")
    status = "completed" if info["converged"] else "partial"
    summary = {"status": status, **info, "input": str(args.input.resolve()),
               "structure": str(output.resolve()), "checkpoint": str(args.model_path.resolve()),
               "device": args.device}
    write_json(args.out_dir / "relaxation.json", summary)
    return summary


if __name__ == "__main__":
    raise SystemExit(execute(run))
