"""Tests for Dynamic Tariffs and Cost Parity."""
from datetime import date
from hems.services.tariff_service import calculate_costs, get_fuel_parity

def test_calculate_costs_defaults():
    # 10 kWh elec @ 28 = 280, 2 kg lpg @ 250 = 500, 1 L kero @ 160 = 160.
    costs = calculate_costs(
        electricity_kwh=10.0,
        lpg_kg=2.0,
        kerosene_liters=1.0
    )
    assert costs["electricity_cost_kes"] == 280.0
    assert costs["lpg_cost_kes"] == 500.0
    assert costs["kerosene_cost_kes"] == 160.0
    assert costs["total_cost_kes"] == 940.0

def test_fuel_parity_compares_input_energy_rates_and_dates():
    parity = get_fuel_parity()
    # KPLC Grid is KES 28.00 / kWh
    assert parity["grid_electricity"]["cost_per_kwh_equiv"] == 28.00
    assert parity["grid_electricity"]["comparison_basis"] == "input_energy"
    # LPG is KES 250 / 12.80 = 19.53 / kWh
    assert parity["lpg"]["cost_per_kwh_equiv"] == 19.53
    assert parity["lpg"]["comparison_basis"] == "input_energy"
    # Kerosene is KES 160 / 10.35 = 15.46 / kWh
    assert parity["kerosene"]["cost_per_kwh_equiv"] == 15.46
    assert parity["kerosene"]["comparison_basis"] == "input_energy"
    assert parity["kerosene"]["cost_per_kwh_equiv"] < parity["grid_electricity"]["cost_per_kwh_equiv"]
    # Solar marginal cost is 0.00
    assert parity["solar"]["cost_per_kwh_equiv"] == 0.00
    assert parity["solar"]["comparison_basis"] == "marginal_energy_cost"
    assert {
        source["effective_date"] for source in parity.values()
    } == {date.today().isoformat()}
