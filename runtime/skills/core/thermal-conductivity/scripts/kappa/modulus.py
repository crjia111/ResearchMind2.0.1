"""Infer bulk and shear modulus with the original 300 K model pipeline."""
import math

import torch

from .cgcnn_model import CrystalGraphConvNet

CHECKPOINTS = {
    "bulk_GPa": "Bulk modulus (GPa)-pre-trained.pth.tar",
    "shear_GPa": "Shear modulus (GPa)-pre-trained.pth.tar",
}


def predict(path, graph, device):
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    options = checkpoint["args"]
    model = CrystalGraphConvNet(
        graph[0].shape[-1], graph[1].shape[-1], atom_fea_len=options["atom_fea_len"],
        h_fea_len=options["h_fea_len"], n_conv=options["n_conv"], n_h=options["n_h"],
    ).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    with torch.inference_mode():
        predicted_scaled = model(*graph).item()
    scale = checkpoint["normalizer"]
    log_modulus = predicted_scaled * float(scale["std"]) + float(scale["mean"])
    result = 10.0 ** log_modulus
    if result <= 0 or not math.isfinite(result):
        raise ValueError("Nonphysical elastic modulus predicted by checkpoint")
    return result
