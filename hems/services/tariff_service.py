"""Dynamic Tariffs and Cost Parity Engine."""
from hems.services.thermo_service import LPG_KWH_PER_KG, KEROSENE_KWH_PER_LITER
from datetime import date

DEFAULT_TARIFFS = {
    "electricity_per_kwh": 28.00,
    "lpg_per_kg": 250.00,
    "kerosene_per_liter": 160.00
}

def calculate_costs(electricity_kwh: float = 0.0,
                    lpg_kg: float = 0.0,
                    kerosene_liters: float = 0.0,
                    tariffs: dict = None) -> dict:
    rates = tariffs or DEFAULT_TARIFFS
    elec_cost = round(electricity_kwh * rates.get("electricity_per_kwh", DEFAULT_TARIFFS["electricity_per_kwh"]), 2)
    lpg_cost = round(lpg_kg * rates.get("lpg_per_kg", DEFAULT_TARIFFS["lpg_per_kg"]), 2)
    kero_cost = round(kerosene_liters * rates.get("kerosene_per_liter", DEFAULT_TARIFFS["kerosene_per_liter"]), 2)
    total_cost = round(elec_cost + lpg_cost + kero_cost, 2)

    return {
        "electricity_cost_kes": elec_cost,
        "lpg_cost_kes": lpg_cost,
        "kerosene_cost_kes": kero_cost,
        "total_cost_kes": total_cost
    }

def get_fuel_parity(tariffs: dict = None) -> dict:
    rates = {**DEFAULT_TARIFFS, **(tariffs or {})}
    effective_date = rates.get("effective_date") or date.today().isoformat()
    if hasattr(effective_date, "isoformat"):
        effective_date = effective_date.isoformat()
    elec_rate = rates["electricity_per_kwh"]
    lpg_rate = rates["lpg_per_kg"]
    kero_rate = rates["kerosene_per_liter"]

    return {
        "grid_electricity": {
            "unit": "kWh",
            "retail_rate": elec_rate,
            "effective_date": effective_date,
            "comparison_basis": "input_energy",
            "cost_per_kwh_equiv": round(elec_rate / 1.0, 2)
        },
        "lpg": {
            "unit": "kg",
            "retail_rate": lpg_rate,
            "effective_date": effective_date,
            "comparison_basis": "input_energy",
            "cost_per_kwh_equiv": round(lpg_rate / LPG_KWH_PER_KG, 2)
        },
        "kerosene": {
            "unit": "L",
            "retail_rate": kero_rate,
            "effective_date": effective_date,
            "comparison_basis": "input_energy",
            "cost_per_kwh_equiv": round(kero_rate / KEROSENE_KWH_PER_LITER, 2)
        },
        "solar": {
            "unit": "kWh",
            "retail_rate": 0.0,
            "effective_date": effective_date,
            "comparison_basis": "marginal_energy_cost",
            "cost_per_kwh_equiv": 0.0
        }
    }
