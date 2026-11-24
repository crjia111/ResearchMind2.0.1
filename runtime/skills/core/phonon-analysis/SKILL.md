---
name: phonon-analysis
description: 用 MatterSim 力模型和 Phonopy 有限位移法计算给定 CIF 的声子色散，输出频率表和色散图。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 声子色散分析

## 适合用它做什么

- 对已收敛的周期晶体计算谐近似声子色散。
- 查看频率分支和负频率位置。需要时可先弛豫，再用收敛结构计算。

## 典型请求

- “用 2×2×2 超胞计算这个硅晶体的声子谱，给我图和频率表。”
- “先弛豫这份 CIF，再计算声子色散并列出负频率出现的位置。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 提供输入 CIF 和输出目录。运行时按需获取 MatterSim 权重。可补充超胞、位移幅度和设备，默认超胞为 `2 2 2`，位移为 0.01 Å。
- 启动器自动准备计算依赖与 [MatterSim 权重](references/model.md)。已收敛结构可直接使用。需要预弛豫时用 `--relax-first`，或先用 [relax_structure.py](scripts/relax_structure.py) 保存结果。

## 产出

- [calculate_phonon.py](scripts/calculate_phonon.py) 生成 `dispersion.png`、`dispersion.csv`、`phonon.json`。核对超胞、位移、频率单位 THz 和频率值数量。
- 有负频率时给出频率大小和路径位置，以 CSV 保留原值。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run calculate-phonon --input ./si.cif --supercell 2 2 2 --amplitude 0.01 --out-dir ./phonon
```

## 边界

- 初步弛豫未收敛时，先检查结构和收敛记录。接近零的负频率需要结合收敛、超胞和位移的数值敏感性解读。
- 本流程计算谐近似色散。热导率或有限温度下的动力学性质需另行计算。
