from pathlib import Path

from common import write_text
from .providers import cod


def export_cif(source, provider, record, formula, destination: Path):
    from pymatgen.core import Structure
    from pymatgen.io.cif import CifWriter

    if source == "cod":
        content = cod.cif(record)
        structure = Structure.from_str(content, fmt="cif")
    else:
        structure = provider.structure(record)
        content = str(CifWriter(structure))
    if structure.composition.reduced_composition != formula.reduced_composition:
        raise ValueError(f"Structure composition differs: {structure.composition.reduced_formula}")
    write_text(destination, content)
    return destination
