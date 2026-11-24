import argparse
from pathlib import Path

from common import execute, require_range
from embeddings import configuration
from evidence import obtain, records


def run():
    parser = argparse.ArgumentParser(description="Index paper text in a persistent local collection")
    parser.add_argument("--papers", type=Path, required=True)
    parser.add_argument("--paper-id", nargs="+")
    parser.add_argument("--index-dir", type=Path, required=True)
    parser.add_argument("--collection", default="research")
    parser.add_argument("--chunk-size", type=int, default=800)
    args = parser.parse_args()
    from knowledge_index import add_paper, collection

    require_range(args.chunk_size, 32, 4000, "chunk-size")

    rows = records(args.papers, args.paper_id)
    if not rows:
        raise ValueError("Select at least one paper")
    config = configuration()
    store = collection(args.index_dir, args.collection, config, args.chunk_size, create=True)
    chunks, succeeded, failures, warnings = 0, [], [], []
    for row in rows:
        try:
            text, level, source, warning = obtain(row, args.papers)
            chunks += add_paper(store, config, row, text, level, source, args.chunk_size)
            succeeded.append(row["paper_id"])
            if warning:
                warnings.append({"paper_id": row["paper_id"], "message": warning})
        except Exception as exc:
            failures.append({"paper_id": row["paper_id"], "message": str(exc)})
    status = "failed" if not succeeded else "partial" if failures or warnings else "completed"
    return {"status": status, "paper_ids": succeeded, "chunks": chunks, "failures": failures,
            "warnings": warnings, "index_dir": str(args.index_dir.resolve()),
            "collection": args.collection, "embedding_model": config[1]}


if __name__ == "__main__":
    raise SystemExit(execute(run))
