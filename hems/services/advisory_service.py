"""Heuristic Energy Advisory Engine.

Analyzes consumption patterns across fuel vectors to generate high-impact,
actionable cost-saving recommendations tailored to Kenyan households.
"""
def _highest_cost_advisory(source_costs: dict) -> dict | None:
    source_labels = {
        "grid_electricity": "grid electricity",
        "lpg": "LPG",
        "kerosene": "kerosene",
    }
    source_actions = {
        "grid_electricity": "Review the highest-use appliances and their recorded runtimes.",
        "lpg": "Review LPG refill amounts and cooking usage before changing fuel.",
        "kerosene": "Review kerosene use and its logged purpose; compare safe alternatives using your current prices before switching.",
    }
    source, cost = max(source_costs.items(), key=lambda item: item[1], default=(None, 0))
    total_cost = sum(source_costs.values())
    if source not in source_labels or cost <= 0 or total_cost <= 0:
        return None
    share = round(cost / total_cost * 100)
    return {
        "id": "ADV_HIGHEST_COST_SOURCE",
        "severity": "WARNING",
        "title": f"{source_labels[source].capitalize()} is your largest energy cost",
        "message": (
            f"{source_labels[source].capitalize()} accounts for KES {cost:.2f} "
            f"({share}% of recorded energy spend). {source_actions[source]}"
        ),
        "source": source,
        "cost_kes": round(cost, 2),
        "share_pct": share,
    }


def generate_advisories(metrics: dict) -> list:
    advisories = []
    cost_advisory = _highest_cost_advisory(metrics.get("source_costs", {}))
    if cost_advisory:
        advisories.append(cost_advisory)

    # 2. LPG Low Capacity Warning
    lpg_pct = metrics.get("lpg_percent_remaining", 100.0)
    if lpg_pct < 20.0:
        advisories.append({
            "id": "ADV_LOW_LPG",
            "severity": "DANGER" if lpg_pct < 10.0 else "WARNING",
            "title": "LPG Cylinder Running Low",
            "message": f"Active cylinder is at {lpg_pct}%. Order a replacement cylinder before mealtime depletion.",
            "potential_monthly_saving_kes": 0.0
        })

    # 3. Solar Utilization Nudge
    solar_kwh = metrics.get("solar_kwh", 0.0)
    if solar_kwh > 0:
        advisories.append({
            "id": "ADV_SOLAR_HARVEST",
            "severity": "INFO",
            "title": "Maximize Daytime Solar Yield",
            "message": "Solar generation has already offset grid electricity costs. Shift device charging and daytime entertainment to peak sun hours (11:00 AM - 2:30 PM) to use more of your future solar generation.",
            "estimated_avoided_cost_kes": metrics.get("solar_avoided_cost_kes", 0.0)
        })

    return advisories
