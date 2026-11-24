from pathlib import Path

from common import execute, output_parser, read_json, write_csv, write_json


def run():
    parser = output_parser("Predict 300 K conductivity using the AI4Kappa moduli and formulas")
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--model-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "models/kappa",
                        help="Override the bundled model location")
    parser.add_argument("--atom-init", type=Path, help="Defaults to atom_init.json inside --model-dir")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--method", choices=["kappa_p", "kappa_mtp", "both"], default="both")
    parser.add_argument("--temperature", type=float, default=300)
    args = parser.parse_args()
    if args.temperature != 300:
        raise ValueError("The released AI4Kappa model supports 300 K only")
    from pymatgen.core import Structure
    from kappa.conductivity import calculate
    from kappa.features import graph
    from kappa.modulus import CHECKPOINTS, predict

    paths = {name: args.model_dir / file for name, file in CHECKPOINTS.items()}
    feature_file = args.atom_init or args.model_dir / "atom_init.json"
    for path in [*paths.values(), feature_file]:
        if not path.is_file():
            raise FileNotFoundError(f"AI4Kappa model asset missing: {path}")
    features = read_json(feature_file)
    methods = ["kappa_p", "kappa_mtp"] if args.method == "both" else [args.method]
    rows, failures = [], []
    for path in args.input:
        try:
            structure = Structure.from_file(path)
            tensors = graph(structure, features, args.device)
            moduli = {key: predict(file, tensors, args.device) for key, file in paths.items()}
            rows.extend({
                "input": str(path.resolve()), "formula": structure.composition.reduced_formula,
                "temperature_K": 300, "method": method, **moduli,
                **calculate(structure, moduli["bulk_GPa"], moduli["shear_GPa"], method),
            } for method in methods)
        except Exception as exc:
            failures.append({"file": str(path), "message": str(exc)})
    status = "failed" if not rows else "partial" if failures else "completed"
    csv = write_csv(args.out_dir / "thermal_conductivity.csv", rows) if rows else None
    output = write_json(args.out_dir / "thermal_conductivity.json", {
        "status": status, "rows": rows, "failures": failures, "device": args.device,
        "checkpoints": {name: str(file.resolve()) for name, file in paths.items()},
    })
    return {"status": status, "results": rows, "failures": failures, "data": str(output.resolve()),
            "csv": str(csv.resolve()) if csv else None}


if __name__ == "__main__":
    raise SystemExit(execute(run))
