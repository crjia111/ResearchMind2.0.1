from common import execute, output_parser, write_text
from chat_model import complete


def run():
    parser = output_parser("Generate a search strategy with a configured language model")
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-tokens", type=int, default=700)
    args = parser.parse_args()
    text, usage = complete("Propose search terms, source choices and inclusion criteria for: " + args.query,
                           args.max_tokens)
    path = write_text(args.out_dir / "search-plan.md", text + "\n")
    return {"status": "completed", "report": str(path.resolve()), "inference": usage}


if __name__ == "__main__":
    raise SystemExit(execute(run))
