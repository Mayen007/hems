"""Appliance Calculation Engine."""

KENYAN_APPLIANCE_PRESETS = [
    {"name": "Samsung Refrigerator 250L", "category": "REFRIGERATION", "rated_wattage": 220.0},
    {"name": "Living Room LED Bulbs (6x)", "category": "LIGHTING", "rated_wattage": 60.0},
    {"name": "Electric Kettle 1.7L", "category": "COOKING", "rated_wattage": 1800.0},
    {"name": "Instant Shower Head", "category": "WATER_HEATING", "rated_wattage": 3500.0},
    {"name": "Smart TV 43-Inch", "category": "ENTERTAINMENT", "rated_wattage": 75.0},
    {"name": "Microwave 20L", "category": "COOKING", "rated_wattage": 1100.0},
    {"name": "Dry Electric Iron", "category": "OTHER", "rated_wattage": 1000.0},
]

def calculate_appliance_kwh(rated_wattage: float, runtime_hours: float) -> float:
    if rated_wattage < 0 or runtime_hours < 0:
        raise ValueError("Parameters cannot be negative")
    clamped_runtime = min(24.0, runtime_hours)
    return round((rated_wattage * clamped_runtime) / 1000.0, 3)

def get_presets() -> list:
    return list(KENYAN_APPLIANCE_PRESETS)
