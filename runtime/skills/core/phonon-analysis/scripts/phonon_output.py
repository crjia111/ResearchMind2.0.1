import math

from common import write_csv


def export(phonon, directory):
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot

    band = phonon.get_band_structure_dict()
    rows = []
    for segment, (points, distances, arrays) in enumerate(zip(
        band["qpoints"], band["distances"], band["frequencies"], strict=True
    ), 1):
        for point, distance, array in zip(points, distances, arrays, strict=True):
            for mode, frequency in enumerate(array, 1):
                value = float(frequency)
                if not math.isfinite(value):
                    raise ValueError("Phonopy produced nonfinite frequencies")
                rows.append({"segment": segment, "q_x": point[0], "q_y": point[1],
                             "q_z": point[2], "distance": distance, "mode": mode,
                             "frequency_THz": value})
    if not rows:
        raise ValueError("No phonon frequencies were computed")
    csv = write_csv(directory / "dispersion.csv", rows)
    figure = directory / "dispersion.png"
    phonon.plot_band_structure().savefig(figure, dpi=160, bbox_inches="tight")
    pyplot.close("all")
    return {"csv": str(csv.resolve()), "plot": str(figure.resolve()),
            "frequency_unit": "THz", "min_frequency_THz": min(row["frequency_THz"] for row in rows),
            "negative_frequencies_below_minus_0.05_THz": sum(row["frequency_THz"] < -0.05 for row in rows),
            "frequency_values": len(rows)}
