from common import output_parser, require_range
from . import catalog, providers

SOURCES = ("arxiv", "semantic_scholar", "tavily")


def search(query, sources, limit, year_from=None, mode="academic"):
    papers, failures = [], []
    for source in dict.fromkeys(sources):
        try:
            if source == "tavily":
                records = providers.tavily(query, limit, mode)
            else:
                records = getattr(providers, source)(query, limit)
            for row in records:
                year = str(row.get("year") or row.get("published") or "")[:4]
                if year_from and (not year.isdecimal() or int(year) < year_from):
                    continue
                papers.append({**row, "topic": query})
        except Exception as exc:
            failures.append({"source": source, "message": str(exc)})
    return catalog.unique_records(papers), failures


def command(*, author=False):
    parser = output_parser("Search literature by author" if author else "Search papers by topic or identifier")
    if author:
        parser.add_argument("--author", required=True)
    else:
        parser.add_argument("--query", required=True, help="Topic, arXiv query, or id:<arXiv ID>")
        parser.add_argument("--mode", choices=["academic", "general", "news"], default="academic")
        parser.add_argument("--sources", nargs="+", choices=SOURCES)
        parser.add_argument("--year-from", type=int)
    parser.add_argument("--limit", type=int, default=10, help="Results per source")
    args = parser.parse_args()
    limit = require_range(args.limit, 1, 100, "limit")
    if author:
        query, mode, sources = 'au:"' + args.author.replace('"', ' ').strip() + '"', "academic", ["arxiv"]
    else:
        query, mode = args.query.strip(), args.mode
        sources = args.sources or (["arxiv"] if mode == "academic" else ["tavily"])
    if not query or (author and not args.author.strip()):
        raise ValueError("Supply a nonempty search term")
    if mode != "academic" and set(sources) != {"tavily"}:
        raise ValueError("Web and news mode use Tavily")
    papers, failures = search(query, sources, limit, getattr(args, "year_from", None), mode)
    status = ("failed" if len(failures) == len(set(sources)) else
              "partial" if failures else "completed" if papers else "no_results")
    return catalog.save(args.out_dir, papers, status=status, failures=failures)
