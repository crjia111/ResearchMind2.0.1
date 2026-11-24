from pathlib import Path

from common import execute, output_parser, require_range, write_json, write_text


def run():
    parser = output_parser("Generate candidate CIFs using CrystaLLM")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--num-samples", type=int, default=2)
    parser.add_argument("--max-new-tokens", type=int, default=1200)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--spacegroup")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--model-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "models/crystallm_v1_small",
                        help="Override the bundled model location")
    args = parser.parse_args()
    checkpoint = args.model_dir / "ckpt.pt"
    if not checkpoint.is_file():
        raise FileNotFoundError(f"CrystaLLM checkpoint missing: {checkpoint}")
    from pymatgen.core import Composition
    from crystal_cif import generated_structure
    from crystallm.inference import samples

    count = require_range(args.num_samples, 1, 100, "num-samples")
    tokens = require_range(args.max_new_tokens, 1, 20000, "max-new-tokens")
    top_k = require_range(args.top_k, 1, 1000, "top-k")
    formula = Composition(args.formula, strict=True)
    if not formula or any(value <= 0 for value in formula.values()):
        raise ValueError("Supply a valid chemical composition")
    accepted, rejected = [], []
    for index, text in enumerate(samples(checkpoint, formula, args.spacegroup, count, tokens,
                                         top_k, args.device, args.seed), 1):
        try:
            cif, structure = generated_structure(text, formula)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            rejected.append({"sample": index, "reason": str(exc)})
            continue
        name = f"candidates/{index:03d}.cif"
        write_text(args.out_dir / name, cif)
        accepted.append({"cif": name, "formula": structure.composition.reduced_formula,
                         "sites": len(structure), "volume_A3": structure.volume})
    status = "completed" if not rejected else "partial" if accepted else "failed"
    summary = {"status": status, "formula": formula.formula, "seed": args.seed,
               "max_new_tokens": tokens, "top_k": top_k, "requested_spacegroup": args.spacegroup,
               "device": args.device, "checkpoint": str(checkpoint.resolve()),
               "structures": accepted, "rejected": rejected}
    result = write_json(args.out_dir / "generation.json", summary)
    return {**summary, "data": str(result.resolve())}


if __name__ == "__main__":
    raise SystemExit(execute(run))
