# MatterSim 1M

首次安装可使用 `python scripts/setup_models.py --model-dir ./models`。从 [Microsoft 固定版本](https://raw.githubusercontent.com/microsoft/mattersim/e59b088ee621cafe0df1b399a27299f3e9092ede/pretrained_models/mattersim-v1.0.0-1M.pth)下载微软的原版权重。SHA-256 为 `28b0b0b0f13efefee06b47ea4c9105a26bd3e2c8396da193430da96b3b49a8be`。[官方模型卡](https://github.com/microsoft/mattersim/blob/e59b088ee621cafe0df1b399a27299f3e9092ede/MODEL_CARD.md) · [MIT 许可证](https://github.com/microsoft/mattersim/blob/e59b088ee621cafe0df1b399a27299f3e9092ede/LICENSE.txt)

MatterSim 1.2.2 包含 C 扩展。需要从源码安装的平台应准备可用于 Python 扩展的本地 C 编译工具。本技能在 Windows x64 使用锁定的 Zig 和 Cython 自动构建扩展。CUDA 模式要求为当前显卡配置匹配的 PyTorch。
