"""Tests for LPG Physics and Tare Weight Calculation."""
from hems.services.lpg_service import (
    compute_net_gas,
    compute_percent_remaining,
    is_refill_event,
    compute_lpg_reading
)

def test_compute_net_gas():
    assert compute_net_gas(21.40, 15.20) == 6.20
    assert compute_net_gas(14.00, 15.20) == 0.0

def test_compute_percent_remaining():
    assert compute_percent_remaining(6.20, 13.00) == 47.7
    assert compute_percent_remaining(13.00, 13.00) == 100.0
    assert compute_percent_remaining(0.0, 13.00) == 0.0

def test_is_refill_detection():
    assert is_refill_event(28.20, 16.00) is True
    assert is_refill_event(21.40, 22.10) is False
    assert is_refill_event(20.00, 22.00, manual_flag=True) is True

def test_compute_lpg_reading_normal_consumption():
    res = compute_lpg_reading(
        gross_curr=21.40,
        gross_prev=22.10,
        tare_weight=15.20,
        nominal_capacity=13.00
    )
    assert res["consumed_kg"] == 0.70
    assert res["computed_kwh"] == 8.960
    assert res["net_gas_kg"] == 6.20
    assert res["percent_remaining"] == 47.7
    assert res["is_refill_event"] is False

def test_compute_lpg_reading_refill():
    res = compute_lpg_reading(
        gross_curr=28.20,
        gross_prev=16.00,
        tare_weight=15.20,
        nominal_capacity=13.00
    )
    assert res["consumed_kg"] == 0.0
    assert res["computed_kwh"] == 0.0
    assert res["net_gas_kg"] == 13.00
    assert res["percent_remaining"] == 100.0
    assert res["is_refill_event"] is True
