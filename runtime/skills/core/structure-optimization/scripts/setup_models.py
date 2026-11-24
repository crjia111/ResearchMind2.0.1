from common import execute
from model_download import cli

ASSETS = (
    (
        "mattersim-v1.0.0-1M.pth",
        "https://raw.githubusercontent.com/microsoft/mattersim/e59b088ee621cafe0df1b399a27299f3e9092ede/pretrained_models/mattersim-v1.0.0-1M.pth",
        "28b0b0b0f13efefee06b47ea4c9105a26bd3e2c8396da193430da96b3b49a8be",
    ),
)

if __name__ == "__main__":
    raise SystemExit(execute(lambda: cli(ASSETS)))
