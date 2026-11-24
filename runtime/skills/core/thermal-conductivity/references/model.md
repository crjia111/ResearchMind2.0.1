# AI4Kappa 模型

安装脚本从 [Jack-Liu0227/AI4Kappa 的固定提交](https://github.com/Jack-Liu0227/AI4Kappa/tree/de1608c9cae3c934d43324cd01904ffd7e546142)直接下载原权重和原元素特征表，并校验以下 SHA-256。

- `Bulk modulus (GPa)-pre-trained.pth.tar`：`bfc8eb09e819ec307a0420b3b37bae64cac657474ba04a219126adda80a33ea7`
- `Shear modulus (GPa)-pre-trained.pth.tar`：`3a7366e13cc1640d6f06078dd45b5eea14a41c3b081726a1ae09a08734acb83b`
- `atom_init.json`：`cb90bd2257dbf8cfc4e6b2b6d4348d4616e8e9680f1339b1461137032e0f1894`

模块使用 [MIT 许可的 CGCNN 网络定义](https://github.com/txie-93/cgcnn/blob/f42ab233c4ee0c416879d6bc2d22a264418413ad/cgcnn/model.py)加载同一网络架构，并按上游的 300 K 表达式计算两个结果。
