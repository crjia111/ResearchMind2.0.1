---
name: literature-search
description: 按主题、作者或 arXiv ID 查找论文，导入本地文献、筛选选集并导出 CSV。适用于文献发现和整理已有检索结果。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 文献检索与清单管理

## 适合用它做什么

- 按主题、关键词、作者或 arXiv ID 查找论文。按需要选择 arXiv、Semantic Scholar 或 Tavily。
- 导入本地论文，筛选已有清单、保存选集或导出 CSV。只需要拟定策略时，可单独生成检索计划。

## 典型请求

- “找 5 篇关于钙钛矿电荷有序的预印本，导出带链接的 CSV。”
- “查这位作者的材料论文，注意区分同名作者。”
- “把这些 PDF 导入清单，只保留我选中的论文。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 在线检索提供主题、作者或 ID，可补充年份、来源和条数。已有资料可直接提供本地文档或 `papers.json`。
- 提供输出目录；筛选时给主题或论文 ID。启动器按需准备 PDF/DOCX 解析库和本地计划模型；依赖由启动器准备。Tavily 需 `TAVILY_API_KEY`。使用远程模型生成计划时配置兼容模型服务的 `OPENAI_API_KEY`、`MODEL_USE` 及可选的 `OPENAI_BASE_URL`。

## 产出

- 检索或导入生成 `papers.json` 和 `papers.csv`。交付时保留标题、来源、链接和完整 ID，并说明各来源的命中或失败情况。
- 用 [search_papers.py](scripts/search_papers.py) 按主题检索，用 [search_by_author.py](scripts/search_by_author.py) 按作者检索。选集、导入和 CSV 操作见 [清单操作](references/catalog.md)。用 [plan_search.py](scripts/plan_search.py) 生成 `search-plan.md`。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run search-papers --query "all:perovskite" --sources arxiv --limit 5 --out-dir ./literature
.\scripts\run.ps1 run search-by-author --author "Shoucheng Zhang" --limit 3 --out-dir ./by-author
.\scripts\run.ps1 run export-csv --input ./literature/papers.json --output ./references.csv
```

## 边界

- 来源不可用、限流和真实的零命中要分别说明。Tavily 的网页或新闻结果按网页证据处理。
- 本地清单整理可离线执行。检索结果可能限于元数据或摘要，论文全文提取和结论分析由后续任务完成。
