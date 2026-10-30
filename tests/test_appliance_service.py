"""Tests for Appliance kWh Calculation and Presets."""
import pytest
from hems.services.appliance_service import calculate_appliance_kwh, get_presets

def test_calculate_appliance_kwh_standard():
    # 220W fridge running 24h: (220 * 24) / 1000 = 5.28 kWh
    assert calculate_appliance_kwh(220.0, 24.0) == 5.280

def test_calculate_appliance_kwh_instant_shower():
    # 3500W instant shower running 0.5 hours: (3500 * 0.5) / 1000 = 1.75 kWh
    assert calculate_appliance_kwh(3500.0, 0.5) == 1.750

def test_negative_values_raise_error():
    with pytest.raises(ValueError):
        calculate_appliance_kwh(-100, 1.0)

def test_get_presets_returns_kenyan_catalog():
    presets = get_presets()
    assert len(presets) >= 5
    names = [p["name"] for p in presets]
    assert any("Refrigerator" in n for n in names)
    assert any("Instant Shower" in n for n in names)
