import json
from pathlib import Path

from chat_model import complete
from citations import validate
from common import execute, output_parser, require_range, write_json, write_text
from evidence import obtain, records


def run():
    parser = output_parser("Write a research report grounded in an input paper catalog")
    parser.add_argument("--papers", type=Path, required=True)
    parser.add_argument("--paper-id", nargs="+")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--language", default="Chinese")
    parser.add_argument("--max-characters", type=int, default=12000, help="Total evidence budget")
    parser.add_argument("--max-tokens", type=int, default=1400)
    args = parser.parse_args()
    require_range(args.max_characters, 1, 200000, "max-characters")
    selected = records(args.papers, args.paper_id)
    if not selected:
        raise ValueError("Choose at least one paper")
    if args.max_characters < len(selected):
        raise ValueError("Evidence budget is smaller than the number of selected papers")
    width = args.max_characters // len(selected)
    items, warnings, failures = [], [], []
    for row in selected:
        try:
            text, level, source, warning = obtain(row, args.papers)
            items.append({"paper_id": row["paper_id"], "title": row.get("title"),
                          "url": row.get("url"), "evidence": level, "source": source,
                          "truncated": len(text) > width, "text": text[:width]})
            if warning:
                warnings.append({"paper_id": row["paper_id"], "message": warning})
        except Exception as exc:
            failures.append({"paper_id": row["paper_id"], "message": str(exc)})
    if not items:
        raise ValueError("No usable evidence: " + json.dumps(failures, ensure_ascii=False))
    citations = ", ".join("[" + row["paper_id"] + "]" for row in items)
    prompt = (f"Write a concise research report in {args.language} about {args.topic}. "
              f"Cite the evidence by using its exact bracketed paper IDs: {citations}. "
              "Use square brackets only for these IDs. State which evidence is abstract-only. Synthesize in your own words and keep the report under 300 words.\n"
              + json.dumps(items, ensure_ascii=False))
    text, inference = complete(prompt, args.max_tokens)
    known = {row["paper_id"] for row in items}
    used = validate(text, known, require_inline=len(known) > 1)
    citation_mode = "inline"
    if len(known) == 1:
        source = items[0]
        ident = source["paper_id"]
        label = source.get("url") or source.get("source") or ""
        text = f"Source: [{ident}] {label}\n\n{text}"
        used = [ident]
        citation_mode = "single_source_document"
    if inference.get("finish_reason") == "length":
        warnings.append({"message": "Model output reached its token limit"})
    report = write_text(args.out_dir / "report.md", text + "\n")
    status = "partial" if warnings or failures else "completed"
    result = {"status": status, "citations": used, "citation_mode": citation_mode,
              "evidence": [{key: value for key, value in row.items() if key != "text"} for row in items],
              "inference": inference, "warnings": warnings, "failures": failures,
              "report": str(report.resolve())}
    write_json(args.out_dir / "report.json", result)
    return result


if __name__ == "__main__":
    raise SystemExit(execute(run))
