# 清单操作

`search_papers.py` 和 `import_papers.py` 生成 `papers.json` 与 `papers.csv`。arXiv ID 保留类别前缀和版本号。

```bash
python scripts/import_papers.py --input ./paper.pdf ./notes.docx --out-dir ./local-papers
python scripts/select_papers.py --input ./literature/papers.json --paper-id 2601.11793v1 --selection ./selection.json
python scripts/select_papers.py --input ./literature/papers.json --selection ./selection.json
python scripts/select_papers.py --clear --selection ./selection.json
python scripts/clean_csv.py --input ./literature/papers.csv --output ./literature/cleaned.csv
```

`filter_papers.py --paper-id …` 读取已保存元数据，`--fields …` 控制字段。`search_papers.py --query id:2601.11793v1` 查询远程记录，`--year-from` 按已知年份过滤。`TAVILY_API_KEY` 用于 Tavily，`SEMANTIC_SCHOLAR_API_KEY` 可用于减少 Semantic Scholar 公共接口的限流。
