from common import execute
from model_download import cli

ASSETS = (
    (
        "ckpt.pt",
        "https://zenodo.org/records/10642388/files/crystallm_v1_small.tar.gz",
        "4de094eee7d95249851d451e2dbb0a0277493c14565b6d13d419b0f50e1b9620",
        "crystallm_v1_small/ckpt.pt",
        "eeaa5ccb6597da856dfd5007bccea83d40f3bfad10c8837931307fd70a9a0163",
    ),
)

if __name__ == "__main__":
    raise SystemExit(execute(lambda: cli(ASSETS)))
