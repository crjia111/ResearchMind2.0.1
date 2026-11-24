"""Compute forces for each finite displacement, preserving supercell site order."""
import numpy as np
from ase import Atoms
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms


def evaluate(atoms, calculator, supercell, amplitude):
    cell = PhonopyAtoms(symbols=atoms.get_chemical_symbols(), cell=atoms.cell.array,
                        scaled_positions=atoms.get_scaled_positions(), masses=atoms.get_masses())
    phonon = Phonopy(cell, np.diag(supercell), primitive_matrix="auto", log_level=0)
    phonon.generate_displacements(distance=amplitude)
    forces = []
    for crystal in phonon.supercells_with_displacements:
        displaced = Atoms(symbols=crystal.symbols, cell=crystal.cell, pbc=True,
                          scaled_positions=crystal.scaled_positions)
        displaced.calc = calculator
        array = displaced.get_forces()
        if not np.isfinite(array).all():
            raise ValueError("MatterSim returned a nonfinite displacement force")
        # Eliminate any net force drift on the periodic supercell.
        forces.append(array - array.mean(axis=0))
    if not forces:
        raise ValueError("Phonopy generated no displacements")
    phonon.forces = forces
    phonon.produce_force_constants()
    phonon.symmetrize_force_constants()
    phonon.auto_band_structure(npoints=51)
    return phonon, len(forces)
