"""The AI4Kappa Slack and MTP expressions at 300 K."""
import math
from scipy.constants import h, k

TEMPERATURE_K = 300


def calculate(structure, bulk, shear, method):
    density = float(structure.density)
    volume = float(structure.volume)
    atom_count = len(structure)
    mass = sum(float(site.specie.atomic_mass) for site in structure)
    longitudinal = 1000 * math.sqrt((bulk + 4 * shear / 3) / density)
    transverse = 1000 * math.sqrt(shear / density)
    speed = ((longitudinal ** -3 + 2 * transverse ** -3) / 3) ** (-1 / 3)
    debye = (h / k) * (3 / (4 * math.pi * volume)) ** (1 / 3) * speed * 1e10
    squared = (longitudinal / transverse) ** 2
    poisson = (squared - 2) / (2 * squared - 2)
    gamma = 3 * (1 + poisson) / (2 * (2 - 3 * poisson))
    if method == "kappa_p":
        coefficient = 2.43e-8 / (1 - 0.514 / gamma + 0.228 / gamma ** 2)
        value = 100 * coefficient * mass * volume ** (1 / 3) * debye ** 3
        value /= gamma ** 2 * TEMPERATURE_K * atom_count
    else:
        value = shear * 1e9 * speed * (volume * 1e-30) ** (1 / 3)
        value *= math.exp(-gamma) / (atom_count * TEMPERATURE_K)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("Nonphysical thermal conductivity prediction")
    return {"thermal_conductivity_W_mK": value, "debye_temperature_K": debye,
            "sound_velocity_m_s": speed, "poisson_ratio": poisson, "gruneisen": gamma}
