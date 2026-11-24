import math


def inspect_cif(content):
    from pymatgen.core import Structure

    structure = Structure.from_str(content, fmt="cif")
    if not len(structure) or not math.isfinite(structure.volume) or structure.volume <= 0:
        raise ValueError("CIF must have sites and a finite, positive unit-cell volume")
    if any(not math.isfinite(value) for site in structure for value in site.frac_coords):
        raise ValueError("CIF atomic coordinates must be finite")
    return structure


def generated_structure(cif, formula):
    from crystallm._utils import (
        extract_space_group_symbol, remove_atom_props_block, replace_symmetry_operators,
    )

    group = extract_space_group_symbol(cif)
    if group and group not in {"P1", "P 1"}:
        cif = replace_symmetry_operators(cif, group)
    cif = remove_atom_props_block(cif)
    structure = inspect_cif(cif)
    if structure.composition.reduced_composition != formula.reduced_composition:
        raise ValueError(f"Candidate has composition {structure.composition.reduced_formula}")
    return cif, structure
