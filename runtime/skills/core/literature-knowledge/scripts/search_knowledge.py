import argparse
from pathlib import Path

from common import execute, require_range, write_json
from embeddings import configuration, embedded


def run():
    parser = argparse.ArgumentParser(description="Search a persistent collection for matching passages")
    parser.add_argument("--index-dir", type=Path, required=True)
    parser.add_argument("--collection", default="research")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--chunk-size", type=int, default=800)
    args = parser.parse_args()
    from knowledge_index import collection

    require_range(args.chunk_size, 32, 4000, "chunk-size")
    require_range(args.top_k, 1, 100, "top-k")
    if not args.query.strip():
        raise ValueError("Supply a search query")
    if not args.index_dir.is_dir():
        raise FileNotFoundError("Index directory missing. Run index_papers.py first.")
    config = configuration()
    store = collection(args.index_dir, args.collection, config, args.chunk_size)
    total = store.count()
    rows = []
    if total:
        output = store.query(query_embeddings=embedded(config, [args.query], query=True),
                             n_results=min(args.top_k, total))
        rows = [{**meta, "text": text, "distance": distance} for meta, text, distance in zip(
            output["metadatas"][0], output["documents"][0], output["distances"][0], strict=True)]
    result = {"status": "completed" if rows else "no_results", "matches": rows,
              "embedding_model": config[1]}
    if args.output:
        write_json(args.output, result)
    return result


if __name__ == "__main__":
    raise SystemExit(execute(run))
