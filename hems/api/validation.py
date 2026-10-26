"""Shared validation helpers for API request values."""
from datetime import date
from math import isfinite
from typing import Any


def finite_number(value: Any, default: float | int | None = None) -> float | None:
    if isinstance(value, bool):
        return None
    numeric_value = default if value is None else value
    if numeric_value is None:
        return None
    try:
        number = float(numeric_value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def is_iso_date(value):
    if not isinstance(value, str):
        return False
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        return False
    return parsed_date.isoformat() == value
