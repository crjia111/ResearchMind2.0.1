---
name: research-report
description: 根据用户指定的论文生成带出处的简明报告，核对引用 ID 和证据范围。适用于选定文献集的证据汇总与研究简报。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 基于文献生成研究报告

## 适合用它做什么

- 围绕一个明确问题汇总已选论文，组织各来源支持的结论及分歧。
- 给单篇论文写带来源的简报，或把多篇证据整理成有可追溯引用的报告。

## 典型请求

- “用这三篇论文写一份中文简报，标出每个主要结论来自哪篇。”
- “根据这篇论文写一页摘要，注明只能看到节选的部分。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 提供主题、输出语言和论文清单。清单包含 `papers` 数组，每条保留真实 `paper_id`、标题和已有链接。证据来自 `content_file`、公开 `pdf_url` 或 `abstract`。相对文件路径以清单所在目录为准。
- 需要限制论文范围时给 `--paper-id`，否则处理清单里的全部论文。默认按需准备本地模型。显式选择 `RM_CHAT_BACKEND=remote` 时配置兼容服务的 `OPENAI_API_KEY`、`MODEL_USE` 及可选的 `OPENAI_BASE_URL`。

## 产出

- `report.md` 为报告正文，`report.json` 提供引用、证据级别、截断和失败情况。单篇报告注明原论文来源；多篇报告使用可追溯的正文引用。
- 用 [write_report.py](scripts/write_report.py) 生成结果。`--max-characters` 控制全部论文合计的证据字符预算。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run write-report --papers ./evidence/papers.json --topic "层状钙钛矿的电荷有序证据" --language Chinese --out-dir ./report
```

## 边界

- 报告覆盖输入清单和可取得的证据。摘要、节选或截断情况随结论注明。
- 脚本校验引用 ID。交付前要对照原文检查引用是否支持具体结论；未知引用或多篇报告缺少有效引用时会报错。
