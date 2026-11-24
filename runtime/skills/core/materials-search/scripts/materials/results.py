import math

from common import output_parser, require_range, write_json
from .query import PROVIDERS, collect

METRICS = {
    "mp": "energy_above_hull", "oqmd": "delta_e", "aflow": "enthalpy_formation_atom",
}


def rank_within_sources(records):
    # Energy above the hull and formation energies answer different questions.
    for record in records:
        field = METRICS.get(record["source"])
        value = record["metadata"].get(field) if field else None
        score = value if isinstance(value, (int, float)) and math.isfinite(value) else None
        record["ranking_metric"] = field
        record["ranking_value_eV_per_atom"] = score
    return sorted(records, key=lambda row: (
        row["source"], row["ranking_value_eV_per_atom"] is None,
        row["ranking_value_eV_per_atom"] or 0,
    ))


def command(*, recommend=False):
    parser = output_parser("Rank material records within each source" if recommend else "Query real material databases")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--sources", choices=PROVIDERS, nargs="+", default=["cod", "oqmd", "aflow"])
    parser.add_argument("--limit", type=int, default=3, help="Records per source")
    args = parser.parse_args()
    limit = require_range(args.limit, 1, 100, "limit")
    from pymatgen.core import Composition

    formula = Composition(args.formula, strict=True)
    if not formula or any(value <= 0 for value in formula.values()):
        raise ValueError("Provide a valid chemical composition")
    result = args.out_dir.resolve()
    records, failures, warnings = collect(formula, args.sources, limit, result / "structures")
    if recommend:
        records = rank_within_sources(records)
    status = ("failed" if len(failures) == len(set(args.sources)) else
              "partial" if failures or warnings else "completed" if records else "no_results")
    data = {"status": status, "formula": formula.reduced_formula, "records": records,
            "failures": failures, "warnings": warnings}
    name = "recommendations.json" if recommend else "materials.json"
    output = write_json(result / name, data)
    return {"status": status, "record_count": len(records), "data": str(output),
            "structures": sum("cif" in row for row in records),
            "failures": failures, "warnings": warnings}
