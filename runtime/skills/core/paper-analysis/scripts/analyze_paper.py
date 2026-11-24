import json
from pathlib import Path

from chat_model import complete
from common import execute, output_parser, require_range, write_csv, write_json, write_text
from evidence import obtain, records


def run():
    parser = output_parser("Analyze one or more papers using a configured language model")
    parser.add_argument("--papers", type=Path, required=True)
    parser.add_argument("--paper-id", nargs="+")
    parser.add_argument("--instruction", default="Summarize purpose, methods, findings, and limitations.")
    parser.add_argument("--language", default="Chinese")
    parser.add_argument("--max-characters", type=int, default=12000)
    parser.add_argument("--max-tokens", type=int, default=900)
    args = parser.parse_args()
    require_range(args.max_characters, 1, 100000, "max-characters")
    analyses, failures, warnings = [], [], []
    for row in records(args.papers, args.paper_id):
        try:
            text, level, source, warning = obtain(row, args.papers)
            item = {"paper_id": row["paper_id"], "title": row.get("title"),
                    "evidence": level, "source": source, "url": row.get("url"), "truncated": len(text) > args.max_characters}
            prompt = (f"Analyze the supplied paper evidence in {args.language}. State evidence limits. "
                      f"{args.instruction}\n" + json.dumps({**item, "text": text[:args.max_characters]},
                                                           ensure_ascii=False))
            value, inference = complete(prompt, args.max_tokens)
            analyses.append({**item, "analysis": value, "inference": inference})
            if warning or inference.get("finish_reason") == "length":
                warnings.append({"paper_id": row["paper_id"],
                                 "message": warning or "Model output reached its token limit"})
        except Exception as exc:
            failures.append({"paper_id": row["paper_id"], "message": str(exc)})
    status = "failed" if not analyses else "partial" if failures or warnings else "completed"
    if analyses:
        md = "\n\n".join(f"## {a['title'] or a['paper_id']}\n\n"
                           f"Evidence: {a['evidence']} · {a['paper_id']}\n\n{a['analysis']}"
                           for a in analyses)
        write_text(args.out_dir / "analysis.md", md + "\n")
        write_csv(args.out_dir / "analysis.csv", analyses)
    result = write_json(args.out_dir / "analysis.json", {"status": status, "analyses": analyses,
                                                        "failures": failures, "warnings": warnings})
    return {"status": status, "analyzed": len(analyses), "data": str(result.resolve()),
            "failures": failures, "warnings": warnings}


if __name__ == "__main__":
    raise SystemExit(execute(run))
