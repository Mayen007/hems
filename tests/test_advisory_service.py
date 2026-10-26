"""Tests for energy advisory calculations and labels."""
from hems.services.advisory_service import generate_advisories


def test_solar_advisory_reports_already_avoided_cost_not_monthly_saving():
    advisories = generate_advisories({
        "solar_kwh": 10.0,
        "solar_avoided_cost_kes": 159.60,
    })

    solar_advisory = next(
        advisory for advisory in advisories
        if advisory["id"] == "ADV_SOLAR_HARVEST"
    )
    assert solar_advisory["estimated_avoided_cost_kes"] == 159.60
    assert "potential_monthly_saving_kes" not in solar_advisory


def test_raw_input_energy_rates_do_not_trigger_cooking_savings_advice():
    advisories = generate_advisories({
        "grid_electricity_kwh": 25.0,
        "has_electric_cooking": True,
        "solar_kwh": 0.0,
    })

    assert all(advisory["id"] != "ADV_THERMAL_COOKING" for advisory in advisories)
    assert all(
        "potential_monthly_saving_kes" not in advisory
        for advisory in advisories
    )


def test_highest_spend_advice_is_first_even_when_solar_was_generated():
    advisories = generate_advisories({
        "source_costs": {
            "grid_electricity": 0.0,
            "lpg": 0.0,
            "kerosene": 160.0,
        },
        "solar_kwh": 10.0,
        "solar_avoided_cost_kes": 280.0,
    })

    assert advisories[0]["id"] == "ADV_HIGHEST_COST_SOURCE"
    assert advisories[0]["source"] == "kerosene"
    assert advisories[0]["share_pct"] == 100
    assert "kerosene" in advisories[0]["message"].lower()
    assert advisories[1]["id"] == "ADV_SOLAR_HARVEST"
