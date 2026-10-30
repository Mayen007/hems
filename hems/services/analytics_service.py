"""Aggregation and Dashboard Analytics Service."""
from hems.db import get_db
from hems.services.tariff_service import DEFAULT_TARIFFS, calculate_costs
from hems.services.advisory_service import generate_advisories
from datetime import date

def get_latest_cylinder(household_id: int) -> dict:
    db = get_db()
    row = db.execute(
        """SELECT c.id, c.brand, c.nominal_capacity_kg, c.tare_weight_kg,
                  r.gross_weight_kg, r.net_gas_kg, r.computed_kwh
           FROM lpg_cylinders c
           LEFT JOIN lpg_readings r ON c.id = r.cylinder_id
           WHERE c.household_id = ? AND c.is_current_active = 1
           ORDER BY r.log_date DESC, r.id DESC LIMIT 1""",
        (household_id,)
    ).fetchone()
    if not row:
        return {
            "id": None,
            "brand": "None",
            "net_gas_kg": 0.0,
            "nominal_capacity_kg": 13.0,
            "tare_weight_kg": 15.20,
            "percent_remaining": 0.0
        }
    net_kg = float(row["net_gas_kg"] or 0.0)
    nom_kg = float(row["nominal_capacity_kg"] or 13.0)
    tare_kg = float(row["tare_weight_kg"] or 15.20)
    pct = round(min(100.0, max(0.0, (net_kg / nom_kg) * 100.0)), 1)
    return {
        "id": row["id"],
        "brand": row["brand"],
        "net_gas_kg": round(net_kg, 2),
        "nominal_capacity_kg": nom_kg,
        "tare_weight_kg": tare_kg,
        "percent_remaining": pct
    }

def get_tariff_rates(household_id: int, effective_on: str = None) -> dict:
    db = get_db()
    if effective_on:
        row = db.execute(
            """SELECT electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date
               FROM tariffs
               WHERE household_id = ? AND effective_date <= ?
               ORDER BY effective_date DESC, id DESC LIMIT 1""",
            (household_id, effective_on),
        ).fetchone()
    else:
        row = db.execute(
            """SELECT electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date
               FROM tariffs WHERE household_id = ?
               ORDER BY effective_date DESC, id DESC LIMIT 1""",
            (household_id,),
        ).fetchone()
    if not row and effective_on:
        row = db.execute(
            """SELECT electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date
               FROM tariffs WHERE household_id = ?
               ORDER BY effective_date, id LIMIT 1""",
            (household_id,),
        ).fetchone()
    if not row:
        return {**DEFAULT_TARIFFS, "effective_date": date.today().isoformat()}
    return _normalize_tariff_row(row)


def _normalize_tariff_row(row) -> dict:
    tariffs = dict(row)
    for rate_name in DEFAULT_TARIFFS:
        tariffs[rate_name] = float(tariffs[rate_name])
    if hasattr(tariffs["effective_date"], "isoformat"):
        tariffs["effective_date"] = tariffs["effective_date"].isoformat()
    return tariffs


def get_cost_totals(
    household_id: int, start_date: str = None, end_date: str = None
) -> dict:
    db = get_db()
    range_filter = " AND {date_column} BETWEEN ? AND ?" if start_date and end_date else ""
    range_params = (start_date, end_date) if start_date and end_date else ()
    query = f"""SELECT log_date, source, SUM(quantity) AS quantity
        FROM (
            SELECT al.log_date, 'electricity' AS source, al.computed_kwh AS quantity
            FROM appliance_logs al
            JOIN appliances a ON al.appliance_id = a.id
            WHERE a.household_id = ?{range_filter.format(date_column='al.log_date')}
            UNION ALL
            SELECT r.log_date, 'lpg' AS source, r.consumed_kg AS quantity
            FROM lpg_readings r
            JOIN lpg_cylinders c ON r.cylinder_id = c.id
            WHERE c.household_id = ?{range_filter.format(date_column='r.log_date')}
            UNION ALL
            SELECT log_date, 'kerosene' AS source, liters_used AS quantity
            FROM kerosene_logs
            WHERE household_id = ?{range_filter.format(date_column='log_date')}
            UNION ALL
            SELECT sl.log_date, 'solar' AS source, sl.yield_kwh AS quantity
            FROM solar_logs sl
            JOIN solar_systems s ON sl.solar_system_id = s.id
            WHERE s.household_id = ?{range_filter.format(date_column='sl.log_date')}
        ) AS daily_usage
        GROUP BY log_date, source
        ORDER BY log_date"""
    params = (
        (household_id, *range_params)
        + (household_id, *range_params)
        + (household_id, *range_params)
        + (household_id, *range_params)
    )
    rows = db.execute(query, params).fetchall()
    tariff_history = db.execute(
        """SELECT electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date
           FROM tariffs WHERE household_id = ? ORDER BY effective_date, id""",
        (household_id,),
    ).fetchall()
    daily_usage = {}
    for row in rows:
        log_date = row["log_date"]
        day = log_date.isoformat() if hasattr(log_date, "isoformat") else str(log_date)
        quantities = daily_usage.setdefault(
            day,
            {
                "electricity": 0.0,
                "lpg": 0.0,
                "kerosene": 0.0,
                "solar": 0.0,
            },
        )
        quantities[row["source"]] = float(row["quantity"] or 0.0)

    usage_by_tariff = {}
    tariff_index = 0
    active_rates = None
    baseline_rates = (
        _normalize_tariff_row(tariff_history[0])
        if tariff_history else DEFAULT_TARIFFS
    )
    for day in sorted(daily_usage):
        while tariff_index < len(tariff_history):
            start_date = tariff_history[tariff_index]["effective_date"]
            start_date = start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date)
            if start_date > day:
                break
            active_rates = _normalize_tariff_row(tariff_history[tariff_index])
            tariff_index += 1
        quantities = daily_usage[day]
        rates = active_rates or baseline_rates
        period = usage_by_tariff.setdefault(
            rates.get("effective_date", "default"),
            {
                "rates": rates,
                "quantities": {
                    "electricity": 0.0,
                    "lpg": 0.0,
                    "kerosene": 0.0,
                    "solar": 0.0,
                },
            },
        )
        for source, quantity in quantities.items():
            period["quantities"][source] += quantity

    source_costs = {"electricity": 0.0, "lpg": 0.0, "kerosene": 0.0}
    solar_savings = 0.0
    for period in usage_by_tariff.values():
        quantities = period["quantities"]
        rates = period["rates"]
        period_costs = calculate_costs(
            round(quantities["electricity"], 2),
            round(quantities["lpg"], 2),
            round(quantities["kerosene"], 2),
            rates,
        )
        source_costs["electricity"] += period_costs["electricity_cost_kes"]
        source_costs["lpg"] += period_costs["lpg_cost_kes"]
        source_costs["kerosene"] += period_costs["kerosene_cost_kes"]
        solar_savings += round(
            round(quantities["solar"], 2) * rates["electricity_per_kwh"], 2
        )

    electricity_cost = round(source_costs["electricity"], 2)
    lpg_cost = round(source_costs["lpg"], 2)
    kerosene_cost = round(source_costs["kerosene"], 2)
    return {
        "electricity_cost_kes": electricity_cost,
        "lpg_cost_kes": lpg_cost,
        "kerosene_cost_kes": kerosene_cost,
        "total_cost_kes": round(electricity_cost + lpg_cost + kerosene_cost, 2),
        "solar_savings_kes": round(solar_savings, 2),
    }


def get_source_totals(household_id: int, start_date: str = None, end_date: str = None) -> dict:
    db = get_db()
    date_filter = " AND {col} BETWEEN ? AND ?" if start_date and end_date else ""
    date_params = (start_date, end_date) if start_date and end_date else ()

    # 1. Electricity from appliance logs
    elec_row = db.execute(
        f"""SELECT COALESCE(SUM(al.computed_kwh), 0.0) as kwh
           FROM appliance_logs al
           JOIN appliances a ON al.appliance_id = a.id
           WHERE a.household_id = ?{date_filter.format(col='al.log_date')}""",
        (household_id, *date_params)
    ).fetchone()
    elec_kwh = round(elec_row["kwh"] if elec_row else 0.0, 2)

    # 2. LPG from readings
    lpg_row = db.execute(
        f"""SELECT COALESCE(SUM(r.consumed_kg), 0.0) as kg, COALESCE(SUM(r.computed_kwh), 0.0) as kwh
           FROM lpg_readings r
           JOIN lpg_cylinders c ON r.cylinder_id = c.id
           WHERE c.household_id = ?{date_filter.format(col='r.log_date')}""",
        (household_id, *date_params)
    ).fetchone()
    lpg_kg = round(lpg_row["kg"] if lpg_row else 0.0, 2)
    lpg_kwh = round(lpg_row["kwh"] if lpg_row else 0.0, 2)

    # 3. Kerosene
    kero_row = db.execute(
        f"SELECT COALESCE(SUM(liters_used), 0.0) as liters, COALESCE(SUM(computed_kwh), 0.0) as kwh FROM kerosene_logs WHERE household_id = ?{date_filter.format(col='log_date')}",
        (household_id, *date_params)
    ).fetchone()
    kero_liters = round(kero_row["liters"] if kero_row else 0.0, 2)
    kero_kwh = round(kero_row["kwh"] if kero_row else 0.0, 2)

    # 4. Solar
    solar_row = db.execute(
        f"""SELECT COALESCE(SUM(sl.yield_kwh), 0.0) as kwh
           FROM solar_logs sl
           JOIN solar_systems s ON sl.solar_system_id = s.id
           WHERE s.household_id = ?{date_filter.format(col='sl.log_date')}""",
        (household_id, *date_params)
    ).fetchone()
    solar_kwh = round(solar_row["kwh"] if solar_row else 0.0, 2)

    return {
        "elec_kwh": elec_kwh,
        "lpg_kg": lpg_kg,
        "lpg_kwh": lpg_kwh,
        "kero_liters": kero_liters,
        "kero_kwh": kero_kwh,
        "solar_kwh": solar_kwh
    }

def get_weekly_trends(household_id: int) -> dict:
    from datetime import date, timedelta
    today = date.today()
    weeks = []
    for i in range(3, -1, -1):
        start = today - timedelta(days=(i * 7) + 6)
        end = today - timedelta(days=i * 7)
        weeks.append((start.isoformat(), end.isoformat()))

    db = get_db()
    elec_data = []
    lpg_data = []
    kerosene_data = []
    solar_data = []

    for start_str, end_str in weeks:
        e = db.execute(
            """SELECT COALESCE(SUM(al.computed_kwh), 0.0) as kwh
               FROM appliance_logs al JOIN appliances a ON al.appliance_id = a.id
               WHERE a.household_id = ? AND al.log_date >= ? AND al.log_date <= ?""",
            (household_id, start_str, end_str)
        ).fetchone()
        elec_data.append(round(e["kwh"] if e else 0.0, 2))

        l = db.execute(
            """SELECT COALESCE(SUM(r.computed_kwh), 0.0) as kwh
               FROM lpg_readings r JOIN lpg_cylinders c ON r.cylinder_id = c.id
               WHERE c.household_id = ? AND r.log_date >= ? AND r.log_date <= ?""",
            (household_id, start_str, end_str)
        ).fetchone()
        lpg_data.append(round(l["kwh"] if l else 0.0, 2))

        k = db.execute(
            """SELECT COALESCE(SUM(computed_kwh), 0.0) AS kwh
               FROM kerosene_logs
               WHERE household_id = ? AND log_date >= ? AND log_date <= ?""",
            (household_id, start_str, end_str)
        ).fetchone()
        kerosene_data.append(round(k["kwh"] if k else 0.0, 2))

        s = db.execute(
            """SELECT COALESCE(SUM(sl.yield_kwh), 0.0) as kwh
               FROM solar_logs sl JOIN solar_systems sys ON sl.solar_system_id = sys.id
               WHERE sys.household_id = ? AND sl.log_date >= ? AND sl.log_date <= ?""",
            (household_id, start_str, end_str)
        ).fetchone()
        solar_data.append(round(s["kwh"] if s else 0.0, 2))

    return {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "electricity": elec_data,
        "lpg": lpg_data,
        "kerosene": kerosene_data,
        "solar": solar_data
    }

def get_dashboard_data(household_id: int) -> dict:
    import calendar
    db = get_db()
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()

    rates = get_tariff_rates(household_id)
    totals = get_source_totals(household_id, month_start, month_end)
    costs = get_cost_totals(household_id, month_start, month_end)
    cyl = get_latest_cylinder(household_id)

    # Household info
    hh = db.execute("SELECT name, location_county FROM households WHERE id = ?", (household_id,)).fetchone()
    household_name = hh["name"] if hh else "My Household"
    location_county = hh["location_county"] if hh and hh["location_county"] else None

    total_kwh = round(totals["elec_kwh"] + totals["lpg_kwh"] + totals["kero_kwh"], 2)
    total_cost = costs["total_cost_kes"]

    # Calculate percentage costs
    elec_pct = round((costs["electricity_cost_kes"] / total_cost * 100), 1) if total_cost > 0 else 0.0
    lpg_pct = round((costs["lpg_cost_kes"] / total_cost * 100), 1) if total_cost > 0 else 0.0
    kero_pct = round((costs["kerosene_cost_kes"] / total_cost * 100), 1) if total_cost > 0 else 0.0

    advisories = generate_advisories({
        "lpg_percent_remaining": (
            cyl["percent_remaining"] if cyl["id"] is not None else 100.0
        ),
        "solar_kwh": totals["solar_kwh"],
        "solar_avoided_cost_kes": costs["solar_savings_kes"],
        "source_costs": {
            "grid_electricity": costs["electricity_cost_kes"],
            "lpg": costs["lpg_cost_kes"],
            "kerosene": costs["kerosene_cost_kes"],
        },
    })

    period = today.strftime("%Y-%m")
    period_label = today.strftime("%B %Y")
    weekly_trends = get_weekly_trends(household_id)
    solar_savings_kes = costs["solar_savings_kes"]

    return {
        "household_name": household_name,
        "location_county": location_county,
        "summary": {
            "period": period,
            "period_label": period_label,
            "total_energy_kwh": total_kwh,
            "solar_generated_kwh": totals["solar_kwh"],
            "solar_savings_kes": solar_savings_kes,
            "total_cost_kes": total_cost,
            "savings_vs_previous_month_pct": None
        },
        "source_breakdown": {
            "grid_electricity": {"kwh": totals["elec_kwh"], "cost_kes": costs["electricity_cost_kes"], "pct_cost": elec_pct},
            "lpg": {"kwh": totals["lpg_kwh"], "cost_kes": costs["lpg_cost_kes"], "pct_cost": lpg_pct},
            "kerosene": {"kwh": totals["kero_kwh"], "cost_kes": costs["kerosene_cost_kes"], "pct_cost": kero_pct},
            "solar": {"kwh": totals["solar_kwh"], "cost_kes": 0.0, "pct_cost": 0.0, "savings_kes": solar_savings_kes}
        },
        "active_cylinder": cyl,
        "tariffs": rates,
        "advisory": advisories,
        "weekly_trends": weekly_trends
    }


def get_report_data(household_id: int, start_date: str, end_date: str) -> dict:
    db = get_db()
    date_range = (household_id, start_date, end_date)

    electricity = db.execute(
        """SELECT COALESCE(SUM(al.computed_kwh), 0.0) AS kwh
           FROM appliance_logs al
           JOIN appliances a ON al.appliance_id = a.id
           WHERE a.household_id = ? AND al.log_date BETWEEN ? AND ?""",
        date_range,
    ).fetchone()
    lpg = db.execute(
        """SELECT COALESCE(SUM(r.consumed_kg), 0.0) AS quantity,
                  COALESCE(SUM(r.computed_kwh), 0.0) AS kwh
           FROM lpg_readings r
           JOIN lpg_cylinders c ON r.cylinder_id = c.id
           WHERE c.household_id = ? AND r.log_date BETWEEN ? AND ?""",
        date_range,
    ).fetchone()
    kerosene = db.execute(
        """SELECT COALESCE(SUM(liters_used), 0.0) AS quantity,
                  COALESCE(SUM(computed_kwh), 0.0) AS kwh
           FROM kerosene_logs
           WHERE household_id = ? AND log_date BETWEEN ? AND ?""",
        date_range,
    ).fetchone()
    solar = db.execute(
        """SELECT COALESCE(SUM(sl.yield_kwh), 0.0) AS kwh
           FROM solar_logs sl
           JOIN solar_systems s ON sl.solar_system_id = s.id
           WHERE s.household_id = ? AND sl.log_date BETWEEN ? AND ?""",
        date_range,
    ).fetchone()

    electricity_kwh = round(float(electricity["kwh"]), 2)
    lpg_kg = round(float(lpg["quantity"]), 2)
    lpg_kwh = round(float(lpg["kwh"]), 2)
    kerosene_liters = round(float(kerosene["quantity"]), 2)
    kerosene_kwh = round(float(kerosene["kwh"]), 2)
    solar_kwh = round(float(solar["kwh"]), 2)
    costs = get_cost_totals(household_id, start_date, end_date)
    total_cost = costs["total_cost_kes"]
    cost_fields = (
        ("grid_electricity", electricity_kwh, electricity_kwh, "kWh", costs["electricity_cost_kes"]),
        ("lpg", lpg_kwh, lpg_kg, "kg", costs["lpg_cost_kes"]),
        ("kerosene", kerosene_kwh, kerosene_liters, "L", costs["kerosene_cost_kes"]),
        ("solar", solar_kwh, solar_kwh, "kWh", 0.0),
    )
    source_breakdown = {
        name: {
            "kwh": energy,
            "quantity": quantity,
            "unit": unit,
            "cost_kes": cost,
            "pct_cost": round(cost / total_cost * 100, 1) if total_cost else 0.0,
        }
        for name, energy, quantity, unit, cost in cost_fields
    }

    trend_rows = db.execute(
        """SELECT al.log_date AS log_date, 'grid_electricity' AS source,
                  SUM(al.computed_kwh) AS kwh
           FROM appliance_logs al
           JOIN appliances a ON al.appliance_id = a.id
           WHERE a.household_id = ? AND al.log_date BETWEEN ? AND ?
           GROUP BY al.log_date
           UNION ALL
           SELECT r.log_date AS log_date, 'lpg' AS source, SUM(r.computed_kwh) AS kwh
           FROM lpg_readings r
           JOIN lpg_cylinders c ON r.cylinder_id = c.id
           WHERE c.household_id = ? AND r.log_date BETWEEN ? AND ?
           GROUP BY r.log_date
           UNION ALL
           SELECT log_date AS log_date, 'kerosene' AS source, SUM(computed_kwh) AS kwh
           FROM kerosene_logs
           WHERE household_id = ? AND log_date BETWEEN ? AND ?
           GROUP BY log_date
           UNION ALL
           SELECT sl.log_date AS log_date, 'solar' AS source, SUM(sl.yield_kwh) AS kwh
           FROM solar_logs sl
           JOIN solar_systems s ON sl.solar_system_id = s.id
           WHERE s.household_id = ? AND sl.log_date BETWEEN ? AND ?
           GROUP BY sl.log_date
           ORDER BY log_date""",
        date_range * 4,
    ).fetchall()
    daily_trends = {}
    trend_fields = {
        "grid_electricity": "grid_electricity_kwh",
        "lpg": "lpg_kwh",
        "kerosene": "kerosene_kwh",
        "solar": "solar_kwh",
    }
    for row in trend_rows:
        row_date = row["log_date"]
        day = row_date.isoformat() if hasattr(row_date, "isoformat") else str(row_date)
        trend = daily_trends.setdefault(day, {
            "date": day,
            "grid_electricity_kwh": 0.0,
            "lpg_kwh": 0.0,
            "kerosene_kwh": 0.0,
            "solar_kwh": 0.0,
        })
        trend[trend_fields[row["source"]]] = round(float(row["kwh"]), 2)

    active_cylinder = get_latest_cylinder(household_id)
    advisories = generate_advisories({
        "lpg_percent_remaining": (
            active_cylinder["percent_remaining"]
            if active_cylinder["id"] is not None else 100.0
        ),
        "solar_kwh": solar_kwh,
        "solar_avoided_cost_kes": costs["solar_savings_kes"],
        "source_costs": {
            "grid_electricity": costs["electricity_cost_kes"],
            "lpg": costs["lpg_cost_kes"],
            "kerosene": costs["kerosene_cost_kes"],
        },
    })

    return {
        "summary": {
            "start_date": start_date,
            "end_date": end_date,
            "total_energy_kwh": round(electricity_kwh + lpg_kwh + kerosene_kwh, 2),
            "solar_generated_kwh": solar_kwh,
            "solar_savings_kes": costs["solar_savings_kes"],
            "total_cost_kes": total_cost,
        },
        "source_breakdown": source_breakdown,
        "daily_trends": list(daily_trends.values()),
        "advisory": advisories,
    }
