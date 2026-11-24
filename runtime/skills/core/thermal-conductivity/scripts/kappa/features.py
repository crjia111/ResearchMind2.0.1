"""Crystal graph features for AI4Kappa's published CGCNN checkpoints."""
import numpy as np
import torch


def graph(structure, atom_features, device):
    if not structure.is_ordered:
        raise ValueError("CGCNN requires ordered atomic sites")
    radius, width, step = 8.0, 12, 0.2
    atom = np.array([atom_features[str(site.specie.Z)] for site in structure], dtype=np.float32)
    indices, distances = [], []
    for neighbors in structure.get_all_neighbors(radius):
        ranked = sorted(neighbors, key=lambda site: site.nn_distance)[:width]
        missing = width - len(ranked)
        indices.append([site.index for site in ranked] + [0] * missing)
        distances.append([site.nn_distance for site in ranked] + [radius + 1] * missing)
    centers = np.arange(0, radius + step, step)
    values = np.exp(-((np.asarray(distances)[..., None] - centers) / step) ** 2)
    return (
        torch.as_tensor(atom, device=device),
        torch.as_tensor(values, dtype=torch.float32, device=device),
        torch.as_tensor(indices, dtype=torch.long, device=device),
        [torch.arange(len(structure), device=device)],
    )
