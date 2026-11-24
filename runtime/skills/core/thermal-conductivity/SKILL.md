---
name: thermal-conductivity
description: 用 AI4Kappa 模量模型及 Kappa-P 或 Kappa-MTP 方法预测晶体在 300 K 的晶格热导率。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 晶格热导率预测

## 适合用它做什么

- 对一个或多个有序周期晶体估算 300 K 的晶格热导率。
- 用 Kappa-P、Kappa-MTP 或两种方法分别计算，并比较预测结果。

## 典型请求

- “用两种方法预测这份硅 CIF 在 300 K 的晶格热导率，导出 CSV。”
- “批量跑这三个结构，只给我 Kappa-P 的结果和失败记录。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 提供周期 CIF、模型目录和输出目录。方法可选 `kappa_p`、`kappa_mtp` 或 `both`。
- 模型目录包含体积模量、剪切模量检查点和元素特征表。若特征表位于其他目录，用 `--atom-init`。首次准备查看 [模型说明](references/model.md) 和 [依赖](requirements.txt)。

## 产出

- [predict_conductivity.py](scripts/predict_conductivity.py) 输出 `thermal_conductivity.json` 和成功结果的 CSV。按输入结构和方法报告 300 K 下的预测值，热导率单位为 W/(m·K)。
- 核对两种模量和热导率均为有限正值，逐项说明失败。若两种方法差异明显，保留各自的数值和方法标签。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run predict-conductivity --input ./si.cif --method both --temperature 300 --out-dir ./conductivity
```

## 边界

- 当前模型的计算温度固定为 300 K。输入必须是有确定原子占位的周期结构。
- 结果为模型预测。用于工程设计或定量比较时，应结合适用范围、参考数据和实验结果。
