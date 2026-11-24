from urllib.parse import urlencode

from http_client import request

ROOT = "https://www.crystallography.net/cod"


def query(formula, limit):
    text = " ".join(
        symbol + (str(int(count)) if int(count) != 1 else "")
        for symbol, count in sorted(formula.get_el_amt_dict().items())
    )
    url = ROOT + "/result?" + urlencode({"formula": text, "format": "json", "maxv": limit})
    result = request(url)
    if not isinstance(result, list):
        raise ValueError("COD returned an unexpected result")
    return result[:limit]


def cif(record):
    identifier = str(record["file"])
    if not identifier.isascii() or not identifier.isdecimal():
        raise ValueError("Invalid COD identifier")
    return request(f"{ROOT}/{identifier}.cif", raw=True).decode("utf-8-sig")
