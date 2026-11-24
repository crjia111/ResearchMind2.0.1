"""ASE BFGS relaxation using a configured ML potential."""
from math import isfinite


def optimize(atoms, *, fmax, steps, relax_cell, logfile=None):
    from ase.filters import FrechetCellFilter
    from ase.optimize import BFGS

    if not isfinite(fmax) or fmax <= 0 or not 1 <= steps <= 10000:
        raise ValueError("fmax must be positive and steps between 1 and 10000")
    initial_energy = float(atoms.get_potential_energy())
    initial_force = max_force(atoms)
    target = FrechetCellFilter(atoms) if relax_cell else atoms
    optimizer = BFGS(target, logfile=logfile)
    converged = bool(optimizer.run(fmax=fmax, steps=steps))
    final_force = max_force(atoms)
    final_energy = float(atoms.get_potential_energy())
    if not all(isfinite(value) for value in (initial_energy, initial_force, final_energy, final_force)):
        raise ValueError("Potential produced a nonfinite energy or force")
    return {"converged": converged, "steps": optimizer.get_number_of_steps(),
            "fmax_eV_A": fmax, "cell_relaxed": relax_cell,
            "initial_energy_eV": initial_energy, "final_energy_eV": final_energy,
            "initial_max_force_eV_A": initial_force, "final_max_force_eV_A": final_force}


def max_force(atoms):
    from numpy.linalg import norm

    return float(norm(atoms.get_forces(), axis=1).max())
