from urllib.parse import urlencode

from http_client import request

ROOT = "https://oqmd.org/oqmdapi/formationenergy"


def query(formula, limit):
    url = ROOT + "?" + urlencode({"composition": formula.reduced_formula, "limit": limit})
    return request(url)["data"]


def structure(record):
    from pymatgen.core import Lattice, Structure

    species = []
    coordinates = []
    for site in record["sites"]:
        symbol, fractions = site.split("@", 1)
        species.append(symbol.strip())
        coordinates.append([float(fraction) for fraction in fractions.split()])
    return Structure(Lattice(record["unit_cell"]), species, coordinates)
