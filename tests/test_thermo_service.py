"""Tests for Thermodynamic Normalization Service."""
import pytest
from hems.services.thermo_service import (
    lpg_to_kwh,
    kerosene_to_kwh,
    electricity_to_kwh,
    solar_to_kwh,
    total_energy_kwh
)

def test_lpg_to_kwh():
    assert lpg_to_kwh(1.0) == 12.800
    assert lpg_to_kwh(0.7) == 8.960
    assert lpg_to_kwh(13.0) == 166.400

def test_kerosene_to_kwh():
    assert kerosene_to_kwh(1.0) == 10.350
    assert kerosene_to_kwh(1.5) == 15.525

def test_electricity_and_solar_to_kwh():
    assert electricity_to_kwh(5.5) == 5.500
    assert solar_to_kwh(3.2) == 3.200

def test_negative_values_raise_error():
    with pytest.raises(ValueError):
        lpg_to_kwh(-1.0)
    with pytest.raises(ValueError):
        kerosene_to_kwh(-0.5)

def test_total_energy_kwh():
    total = total_energy_kwh(
        electricity_kwh=10.0,
        lpg_kg=2.0,
        kerosene_liters=1.0,
        solar_kwh=5.0
    )
    # 10.0 + (2.0 * 12.8) + (1.0 * 10.35) + 5.0 = 10.0 + 25.6 + 10.35 + 5.0 = 50.95
    assert total == 50.950
