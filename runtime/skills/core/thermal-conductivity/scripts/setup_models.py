from common import execute
from model_download import cli

ASSETS = (
    (
        "Bulk modulus (GPa)-pre-trained.pth.tar",
        "https://raw.githubusercontent.com/Jack-Liu0227/AI4Kappa/de1608c9cae3c934d43324cd01904ffd7e546142/model/Bulk%20modulus%20%28GPa%29-pre-trained.pth.tar",
        "bfc8eb09e819ec307a0420b3b37bae64cac657474ba04a219126adda80a33ea7",
    ),
    (
        "Shear modulus (GPa)-pre-trained.pth.tar",
        "https://raw.githubusercontent.com/Jack-Liu0227/AI4Kappa/de1608c9cae3c934d43324cd01904ffd7e546142/model/Shear%20modulus%20%28GPa%29-pre-trained.pth.tar",
        "3a7366e13cc1640d6f06078dd45b5eea14a41c3b081726a1ae09a08734acb83b",
    ),
    (
        "atom_init.json",
        "https://raw.githubusercontent.com/Jack-Liu0227/AI4Kappa/de1608c9cae3c934d43324cd01904ffd7e546142/root_dir/atom_init.json",
        "cb90bd2257dbf8cfc4e6b2b6d4348d4616e8e9680f1339b1461137032e0f1894",
    ),
)

if __name__ == "__main__":
    raise SystemExit(execute(lambda: cli(ASSETS)))
