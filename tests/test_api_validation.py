import pytest

from hems.api.validation import finite_number, is_iso_date


@pytest.mark.parametrize("value", ["bad", float("nan"), float("inf"), True, None])
def test_finite_number_rejects_invalid_values(value):
    assert finite_number(value) is None


def test_finite_number_uses_default_for_missing_value():
    assert finite_number(None, 28.0) == 28.0


@pytest.mark.parametrize("value", ["2026-10-22", "2024-02-29"])
def test_iso_date_accepts_valid_calendar_dates(value):
    assert is_iso_date(value)


@pytest.mark.parametrize("value", ["2026-02-29", "2026-W43-4", "not-a-date", None])
def test_iso_date_rejects_invalid_or_noncanonical_values(value):
    assert not is_iso_date(value)
