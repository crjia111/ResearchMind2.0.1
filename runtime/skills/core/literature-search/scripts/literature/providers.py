"""Queries and metadata normalization for supported paper sources."""
import hashlib
import os
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

from http_client import request


def arxiv(query, limit):
    params = {"max_results": limit, "sortBy": "relevance"}
    if query.startswith("id:"):
        params["id_list"] = query[3:]
    else:
        params["search_query"] = query if ":" in query else f'all:{query.replace(chr(34), " ")}'
    root = ET.fromstring(request("https://export.arxiv.org/api/query?" + urlencode(params), raw=True))
    ns = "{http://www.w3.org/2005/Atom}"
    papers = []
    for item in root.findall(ns + "entry"):
        identifier = item.findtext(ns + "id").split("/abs/")[-1]
        title = " ".join(item.findtext(ns + "title", "").split())
        if identifier.startswith("http") or title == "Error":
            raise RuntimeError(item.findtext(ns + "summary", "arXiv returned an error"))
        papers.append({
            "paper_id": identifier, "title": title,
            "authors": [person.findtext(ns + "name") for person in item.findall(ns + "author")],
            "abstract": item.findtext(ns + "summary", "").strip(),
            "published": item.findtext(ns + "published"),
            "url": "https://arxiv.org/abs/" + identifier,
            "pdf_url": "https://arxiv.org/pdf/" + identifier, "source": "arxiv",
        })
    return papers


def semantic_scholar(query, limit):
    fields = "title,abstract,authors,year,url,externalIds,openAccessPdf"
    params = urlencode({"query": query, "limit": limit, "fields": fields})
    key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    payload = request("https://api.semanticscholar.org/graph/v1/paper/search?" + params,
                      headers={"x-api-key": key} if key else None)
    return [{
        "paper_id": row["paperId"], "title": row["title"], "abstract": row.get("abstract"),
        "authors": [person["name"] for person in row.get("authors", [])],
        "year": row.get("year"), "doi": (row.get("externalIds") or {}).get("DOI"),
        "url": row.get("url"), "pdf_url": (row.get("openAccessPdf") or {}).get("url"),
        "source": "semantic_scholar",
    } for row in payload.get("data", [])]


def tavily(query, limit, topic):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("Set TAVILY_API_KEY for Tavily search")
    payload = request("https://api.tavily.com/search",
                      {"query": query, "max_results": min(limit, 20),
                       "topic": "general" if topic == "academic" else topic},
                      {"Authorization": f"Bearer {key}"})
    return [{
        "paper_id": hashlib.sha256(row["url"].encode()).hexdigest()[:24],
        "title": row.get("title", ""), "abstract": row.get("content", ""),
        "url": row["url"], "published": row.get("published_date"), "source": "tavily",
        "evidence": "web_excerpt",
    } for row in payload.get("results", [])]
