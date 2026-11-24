from urllib.parse import quote

from http_client import request

ROOT = "https://aflow.org/API/aflux/"
FIELDS = "geometry,positions_fractional,species,composition,auid,enthalpy_formation_atom"


def query(formula, limit):
    from pymatgen.core import Composition

    amounts = formula.get_el_amt_dict()
    species = ",".join(sorted(amounts))
    rows = []
    # AFLOW's compound strings may describe a supercell (Si2, Si8, ...).
    # Query by species and check the reduced stoichiometry independently.
    page_size = min(100, max(limit, 30))
    for page in range(1, 5):
        query = f"species({species}),nspecies({len(amounts)}),{FIELDS},paging({page},{page_size})"
        result = request(ROOT + "?" + quote(query, safe="(),"))
        records = list(result.values()) if isinstance(result, dict) else result
        if not isinstance(records, list):
            raise ValueError("AFLOW returned an unexpected result")
        for entry in records:
            symbols = entry.get("species", [])
            counts = entry.get("composition", [])
            candidate = Composition(dict(zip(symbols, counts)))
            if candidate.reduced_composition == formula.reduced_composition:
                rows.append(entry)
            if len(rows) == limit:
                return rows
        if len(records) < page_size:
            break
    return rows


def structure(record):
    from pymatgen.core import Lattice, Structure

    symbols = [
        symbol for symbol, count in zip(record["species"], record["composition"])
        for _ in range(int(count))
    ]
    return Structure(
        Lattice.from_parameters(*record["geometry"][:6]), symbols,
        record["positions_fractional"],
    )
