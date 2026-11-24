---
name: paper-analysis
description: 下载、提取和阅读指定论文，定位原文段落，或分析论文的方法、发现与局限。适用于单篇精读和批量论文证据提取。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 论文读取与分析

## 适合用它做什么

- 下载公开论文，提取单篇或多篇文件的可读文本。
- 从已有文本定位关键词或按字符分段阅读。需要解读时，围绕用户问题分析论文。

## 典型请求

- “提取这篇 PDF 的文字，定位作者谈实验局限的位置。”
- “比较这三篇论文的方法，并指出哪些结论有全文证据。”
- “从上次读到的字符位置继续读 1200 字。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 提供本地文档、公开下载 URL、已提取文本或论文清单。批量处理时可给论文 ID；必须取得全文时说明。
- 分析时提供问题和输出语言。默认按需准备本地模型。显式设 RM_CHAT_BACKEND=remote 后可使用兼容服务，配置 `OPENAI_API_KEY`、`MODEL_USE` 及可选的 `OPENAI_BASE_URL`。提取时自动安装对应解析库。

## 产出

- [download_paper.py](scripts/download_paper.py) 保存公开文档。[extract_text.py](scripts/extract_text.py) 输出文本和 `papers.json`；批量文本路径以各条记录的 `content_file` 为准。要求全文时用 `--require-fulltext`。
- [read_segment.py](scripts/read_segment.py) 返回文本和 `next_start`；[find_in_text.py](scripts/find_in_text.py) 返回字面匹配和偏移。[analyze_paper.py](scripts/analyze_paper.py) 生成 `analysis.md`、`analysis.csv` 和 `analysis.json`。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run extract-text --input ./paper.pdf --out-dir ./evidence
.\scripts\run.ps1 run read-segment --input ./evidence/paper.txt --start 0 --length 1200
.\scripts\run.ps1 run find-in-text --input ./evidence/paper.txt --term "limitations" --limit 5
.\scripts\run.ps1 run analyze-paper --papers ./evidence/papers.json --instruction "说明方法、发现和局限" --out-dir ./analysis
```

## 边界

- 分段偏移按 Unicode 字符计算。已有文本的定位与分段可离线执行。
- 核对 `evidence`、`truncated` 和逐篇失败。只有摘要、节选或截断文本时，结论限于实际取得的内容。引用关键数字前回到原文核对。
