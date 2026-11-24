---
name: materials-search
description: 按化学组成查询 COD、OQMD、AFLOW 或 Materials Project，导出带来源的记录及可用 CIF，或按数据库内的指标排序。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 材料数据库查询

## 适合用它做什么

- 从 COD 查实验晶体记录，或从 OQMD、AFLOW 和 Materials Project 查计算结构及已有材料性质。
- 导出可用于后续计算的 CIF，或按各来源已有的数值字段整理候选。

## 典型请求

- “从 COD 和 OQMD 各找两个硅结构，把能拿到的 CIF 下载给我。”
- “查 OQMD 的 NaCl 候选结构，在同一数据库内按形成能排序。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 提供化学式，可选数据源及每个源的记录上限，然后指定输出目录。查询 Materials Project 需 `MP_API_KEY`。
- 依赖由启动器准备。公开数据库的实时查询需要联网。排名或解释数据库字段时查看 [来源与排序指标](references/sources.md)。

## 产出

- [search_materials.py](scripts/search_materials.py) 生成 `materials.json`，[recommend_materials.py](scripts/recommend_materials.py) 生成 `recommendations.json`。记录含 `source`、`source_id` 和可用元数据。
- 结构下载成功时，记录中的 `cif` 指向输出目录下的实际文件。按来源交付结果，并汇报 `failures` 和 `warnings`。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run search-materials --formula Si --sources cod oqmd aflow --limit 2 --out-dir ./silicon
.\scripts\run.ps1 run recommend-materials --formula NaCl --sources oqmd --limit 5 --out-dir ./ranked
```

## 边界

- 数据库结果可能只有记录和属性。缺 CIF 时说明原因，并保留仍有用的记录。单一来源失败时可使用其他成功来源。
- 排序在同一来源内解释。形成能和凸包距离应分别报告，查询结果覆盖范围以所选来源实际返回为准。
