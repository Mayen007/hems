"""Thermodynamic Normalization Service.

Converts heterogeneous fuel vectors (kg LPG, Litres kerosene) into
standard kilowatt-hours (kWh) using certified Lower Heating Values.
"""

LPG_KWH_PER_KG = 12.800
KEROSENE_KWH_PER_LITER = 10.350
GRID_KWH_PER_KWH = 1.000
SOLAR_KWH_PER_KWH = 1.000

def lpg_to_kwh(mass_kg: float) -> float:
    if mass_kg < 0:
        raise ValueError("Mass cannot be negative")
    return round(mass_kg * LPG_KWH_PER_KG, 3)

def kerosene_to_kwh(volume_liters: float) -> float:
    if volume_liters < 0:
        raise ValueError("Volume cannot be negative")
    return round(volume_liters * KEROSENE_KWH_PER_LITER, 3)

def electricity_to_kwh(kwh: float) -> float:
    if kwh < 0:
        raise ValueError("Electricity cannot be negative")
    return round(kwh * GRID_KWH_PER_KWH, 3)

def solar_to_kwh(kwh: float) -> float:
    if kwh < 0:
        raise ValueError("Solar generation cannot be negative")
    return round(kwh * SOLAR_KWH_PER_KWH, 3)

def total_energy_kwh(electricity_kwh: float = 0.0,
                     lpg_kg: float = 0.0,
                     kerosene_liters: float = 0.0,
                     solar_kwh: float = 0.0) -> float:
    e_elec = electricity_to_kwh(electricity_kwh)
    e_lpg = lpg_to_kwh(lpg_kg)
    e_kero = kerosene_to_kwh(kerosene_liters)
    e_solar = solar_to_kwh(solar_kwh)
    return round(e_elec + e_lpg + e_kero + e_solar, 3)
