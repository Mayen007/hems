"""LPG Cylinder Physics and Net Mass Engine."""
from hems.services.thermo_service import lpg_to_kwh

def compute_net_gas(gross_weight_kg: float, tare_weight_kg: float) -> float:
    if gross_weight_kg < tare_weight_kg:
        return 0.0
    return round(gross_weight_kg - tare_weight_kg, 2)

def compute_percent_remaining(net_gas_kg: float, nominal_capacity_kg: float) -> float:
    if nominal_capacity_kg <= 0:
        return 0.0
    pct = (net_gas_kg / nominal_capacity_kg) * 100.0
    return round(min(100.0, max(0.0, pct)), 1)

def is_refill_event(gross_curr: float, gross_prev: float, manual_flag: bool = False) -> bool:
    if manual_flag:
        return True
    return gross_curr > gross_prev

def compute_lpg_reading(gross_curr: float,
                        gross_prev: float,
                        tare_weight: float,
                        nominal_capacity: float,
                        manual_refill_flag: bool = False) -> dict:
    net_remaining = compute_net_gas(gross_curr, tare_weight)
    refill = is_refill_event(gross_curr, gross_prev, manual_refill_flag)
    
    if refill:
        consumed = 0.0
    else:
        consumed = round(max(0.0, gross_prev - gross_curr), 2)
        
    kwh = lpg_to_kwh(consumed)
    pct_left = compute_percent_remaining(net_remaining, nominal_capacity)

    return {
        "net_gas_kg": net_remaining,
        "consumed_kg": consumed,
        "computed_kwh": kwh,
        "percent_remaining": pct_left,
        "is_refill_event": refill
    }
