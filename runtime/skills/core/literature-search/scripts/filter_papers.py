from pathlib import Path

from common import execute, output_parser
from literature.catalog import read_catalog, save


def run():
    parser = output_parser("List, filter or inspect a saved catalog")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--topic")
    parser.add_argument("--paper-id")
    parser.add_argument("--fields", nargs="+")
    args = parser.parse_args()
    papers = [row for row in read_catalog(args.input)
              if (not args.topic or row.get("topic") == args.topic)
              and (not args.paper_id or row["paper_id"] == args.paper_id)]
    topics = sorted({row["topic"] for row in papers if row.get("topic")})
    for record in papers:
        if record.get("content_file"):
            record["content_file"] = str((args.input.resolve().parent / record["content_file"]).resolve())
    if args.fields:
        wanted = {"paper_id", *args.fields}
        papers = [{k: v for k, v in row.items() if k in wanted} for row in papers]
    return save(args.out_dir, papers, status="completed" if papers else "no_results", topics=topics)


if __name__ == "__main__":
    raise SystemExit(execute(run))
