"""Appliance and Duty Cycle Calculation Engine."""

KENYAN_APPLIANCE_PRESETS = [
    {"name": "Samsung Refrigerator 250L", "category": "REFRIGERATION", "rated_wattage": 220.0, "default_duty_cycle": 0.50},
    {"name": "Living Room LED Bulbs (6x)", "category": "LIGHTING", "rated_wattage": 60.0, "default_duty_cycle": 1.00},
    {"name": "Electric Kettle 1.7L", "category": "COOKING", "rated_wattage": 1800.0, "default_duty_cycle": 1.00},
    {"name": "Instant Shower Head", "category": "WATER_HEATING", "rated_wattage": 3500.0, "default_duty_cycle": 1.00},
    {"name": "Smart TV 43-Inch", "category": "ENTERTAINMENT", "rated_wattage": 75.0, "default_duty_cycle": 1.00},
    {"name": "Microwave 20L", "category": "COOKING", "rated_wattage": 1100.0, "default_duty_cycle": 1.00},
    {"name": "Dry Electric Iron", "category": "OTHER", "rated_wattage": 1000.0, "default_duty_cycle": 1.00},
]

def calculate_appliance_kwh(rated_wattage: float,
                            runtime_hours: float,
                            duty_cycle: float = 1.0) -> float:
    if rated_wattage < 0 or runtime_hours < 0 or duty_cycle < 0:
        raise ValueError("Parameters cannot be negative")
    clamped_runtime = min(24.0, runtime_hours)
    clamped_duty = min(1.0, duty_cycle)
    kwh = (rated_wattage * clamped_runtime * clamped_duty) / 1000.0
    return round(kwh, 3)

def get_presets() -> list:
    return list(KENYAN_APPLIANCE_PRESETS)
