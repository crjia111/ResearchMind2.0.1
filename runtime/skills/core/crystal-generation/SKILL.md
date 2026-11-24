---
name: crystal-generation
description: 用 CrystaLLM 按给定组成和可选空间群生成候选晶体，或验证已有 CIF 的组成、位点和晶胞。
compatibility: 需要本地执行权限和可写缓存。首次下载依赖和模型需联网；已准备的本地计算支持离线。
metadata:
  version: "2.0"
---

# 晶体生成与 CIF 校验

## 适合用它做什么

- 按化学组成和可选空间群生成候选 CIF。
- 检查已有的 CIF 是否可解析，并查看组成、位点数和晶胞体积。

## 典型请求

- “用 CrystaLLM 生成两个 NaCl 候选结构，给我可解析的 CIF。”
- “生成含 4 个 Na 和 4 个 Cl 的晶胞，要求空间群为 Fm-3m。”
- “帮我确认这份 CIF 的组成和晶胞体积。”

## 你需要提供

通过本技能的启动器执行用户的原任务。启动器检查所选操作，按需安装，复查后执行；使用用户原来的输入、参数和输出路径。

- 生成时提供化学组成和输出目录，可补充候选数量、目标空间群、随机种子和运行设备。生成时自动准备 `ckpt.pt`。从源码运行时可覆盖模型目录，权重来源见 [模型安装与校验](references/model.md)。
- 仅校验时提供 CIF 文件。源码环境依赖见 [依赖清单](requirements.txt)。

## 产出

- [generate_crystals.py](scripts/generate_crystals.py) 生成 `generation.json` 和实际通过校验的候选 CIF。汇报通过数量、文件路径和拒收原因。
- [validate_cif.py](scripts/validate_cif.py) 返回约化组成、位点数和晶胞体积。要求固定原子数或空间群时，另行核对生成结构的实际位点和空间群。

## 运行

使用本技能目录内的启动器。Windows 示例如下；Linux 和 macOS 把 `.\scripts\run.ps1` 替换为 `sh ./scripts/run.sh`。从其他目录运行时传入启动器的绝对路径。只读诊断使用 `doctor 操作名 --json`，正常任务使用 `run 操作名`。缺少外部条件时见 [环境与缓存](references/setup.md)。

```powershell
.\scripts\run.ps1 run generate-crystals --formula NaCl --num-samples 2 --seed 1337 --device cpu --out-dir ./nacl
.\scripts\run.ps1 run validate-cif --input ./nacl/candidates/001.cif
```

## 边界

- 空间群参数是生成条件，实际对称性要以结构解析结果为准。模型筛选使用约化组成，指定单胞原子数时应单独核对。
- 输出是候选结构。稳定性、可合成性和材料性质需要后续计算或实验证据。全拒收时说明本次未得到可用候选。
