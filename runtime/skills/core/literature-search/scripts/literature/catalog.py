from common import read_json, write_csv, write_json


def read_catalog(path):
    data = read_json(path)
    records = data.get("papers") if isinstance(data, dict) else data
    if not isinstance(records, list) or any(
        not isinstance(row, dict) or not row.get("paper_id") for row in records
    ):
        raise ValueError("Expected a paper list with paper_id on every record")
    return records


def unique_records(records):
    seen, result = set(), []
    for paper in records:
        keys = {str(paper[key]).casefold() for key in ("doi", "url", "paper_id") if paper.get(key)}
        if not seen.isdisjoint(keys):
            continue
        seen.update(keys)
        result.append(paper)
    return result


def save(out_dir, papers, *, status="completed", **extra):
    payload = {"status": status, "papers": papers, **extra}
    data = write_json(out_dir / "papers.json", payload)
    csv = write_csv(out_dir / "papers.csv", papers)
    return {"status": status, "paper_count": len(papers), "data": str(data.resolve()),
            "csv": str(csv.resolve()), **extra}
