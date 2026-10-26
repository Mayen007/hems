"""Conversion Service - Thermodynamic Normalization to kWh."""
from hems.services.thermo_service import (
    LPG_KWH_PER_KG,
    KEROSENE_KWH_PER_LITER,
    GRID_KWH_PER_KWH,
    SOLAR_KWH_PER_KWH,
    lpg_to_kwh,
    kerosene_to_kwh,
    electricity_to_kwh,
    solar_to_kwh,
    total_energy_kwh
)

__all__ = [
    "LPG_KWH_PER_KG",
    "KEROSENE_KWH_PER_LITER",
    "GRID_KWH_PER_KWH",
    "SOLAR_KWH_PER_KWH",
    "lpg_to_kwh",
    "kerosene_to_kwh",
    "electricity_to_kwh",
    "solar_to_kwh",
    "total_energy_kwh"
]
