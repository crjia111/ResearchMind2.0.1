import os
from urllib.parse import urlencode

from http_client import request


def query(formula, limit):
    key = os.getenv("MP_API_KEY")
    if not key:
        raise RuntimeError("Set MP_API_KEY to query Materials Project")
    fields = "material_id,formula_pretty,band_gap,density,energy_above_hull,structure"
    params = urlencode({"formula": formula.reduced_formula, "_limit": limit, "_fields": fields})
    return request(
        "https://api.materialsproject.org/materials/summary/?" + params,
        headers={"X-API-KEY": key},
    )["data"]


def structure(record):
    from pymatgen.core import Structure

    return Structure.from_dict(record["structure"])
