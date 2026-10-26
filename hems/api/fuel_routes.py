"""Multi-Source Fuel Logging Endpoints (LPG, Kerosene, Solar)."""
from flask import Blueprint, request, jsonify, g
from hems.db import get_db
from hems.services.auth_service import login_required, require_role
from hems.services.lpg_service import compute_lpg_reading
from hems.services.thermo_service import kerosene_to_kwh, solar_to_kwh
from hems.services.analytics_service import get_tariff_rates
from hems.api.validation import finite_number, is_iso_date

fuel_bp = Blueprint("fuel", __name__)

@fuel_bp.route("/lpg/cylinders", methods=["GET"])
@login_required
def list_cylinders():
    hid = g.current_user["household_id"]
    db = get_db()
    rows = db.execute(
        "SELECT id, brand, nominal_capacity_kg, tare_weight_kg, is_current_active FROM lpg_cylinders WHERE household_id = ?",
        (hid,)
    ).fetchall()
    return jsonify({"status": "success", "data": [dict(r) for r in rows]}), 200

@fuel_bp.route("/lpg/cylinders", methods=["POST"])
@require_role("ADMIN")
def create_cylinder():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    brand = data.get("brand", "Total Gas")
    brand = brand.strip() if isinstance(brand, str) else ""
    nominal = finite_number(data.get("nominal_capacity_kg"), 13.00)
    tare = finite_number(data.get("tare_weight_kg"), 15.20)
    if not brand or nominal is None or nominal <= 0 or tare is None or tare < 0:
        return jsonify({"status": "error", "message": "Valid brand, capacity, and tare weight required"}), 400
    hid = g.current_user["household_id"]

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO lpg_cylinders (household_id, brand, nominal_capacity_kg, tare_weight_kg) VALUES (?, ?, ?, ?)",
        (hid, brand, nominal, tare)
    )
    db.commit()
    return jsonify({"status": "success", "data": {"id": cur.lastrowid, "brand": brand}}), 201

@fuel_bp.route("/lpg", methods=["POST"])
@require_role("ADMIN")
def log_lpg():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    cyl_id = data.get("cylinder_id")
    log_date = data.get("log_date")
    gross_curr = finite_number(data.get("gross_weight_kg"), 0.0)
    manual_refill = data.get("is_refill_event", False)

    if not is_iso_date(log_date) or gross_curr is None or gross_curr <= 0 or not isinstance(manual_refill, bool):
        return jsonify({"status": "error", "message": "Valid log_date and gross_weight_kg required"}), 400
    if cyl_id is not None and not isinstance(cyl_id, int):
        return jsonify({"status": "error", "message": "Valid cylinder_id required"}), 400

    hid = g.current_user["household_id"]
    db = get_db()

    if not cyl_id:
        active = db.execute("SELECT id FROM lpg_cylinders WHERE household_id = ? AND is_current_active = 1 LIMIT 1", (hid,)).fetchone()
        cyl_id = active["id"] if active else None

    if not cyl_id:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO lpg_cylinders (household_id, brand, nominal_capacity_kg, tare_weight_kg, is_current_active) VALUES (?, ?, ?, ?, 1)",
            (hid, "Total Gas", 13.00, 15.20)
        )
        cyl_id = cur.lastrowid
        db.commit()

    cyl = db.execute(
        "SELECT id, brand, nominal_capacity_kg, tare_weight_kg FROM lpg_cylinders WHERE id = ? AND household_id = ?",
        (cyl_id, hid)
    ).fetchone()
    if not cyl:
        return jsonify({"status": "error", "message": "Cylinder not found"}), 404
    if gross_curr < cyl["tare_weight_kg"]:
        return jsonify({"status": "error", "message": "Gross weight cannot be below cylinder tare weight"}), 400

    # Get latest reading
    last_reading = db.execute(
        "SELECT gross_weight_kg FROM lpg_readings WHERE cylinder_id = ? ORDER BY log_date DESC, id DESC LIMIT 1",
        (cyl_id,)
    ).fetchone()
    gross_prev = last_reading["gross_weight_kg"] if last_reading else gross_curr

    calc = compute_lpg_reading(
        gross_curr=gross_curr,
        gross_prev=gross_prev,
        tare_weight=cyl["tare_weight_kg"],
        nominal_capacity=cyl["nominal_capacity_kg"],
        manual_refill_flag=manual_refill
    )
    if (
        calc["consumed_kg"] == 0
        and not calc["is_refill_event"]
        and data.get("confirm_zero_consumption") is not True
    ):
        return jsonify({
            "status": "error",
            "message": "This reading records 0 kg LPG consumed. Confirm to save a baseline or zero-usage reading."
        }), 400

    db.execute(
        """INSERT INTO lpg_readings
           (cylinder_id, log_date, gross_weight_kg, net_gas_kg, consumed_kg, computed_kwh, is_refill_event)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (cyl_id, log_date, gross_curr, calc["net_gas_kg"], calc["consumed_kg"], calc["computed_kwh"], 1 if calc["is_refill_event"] else 0)
    )
    db.commit()

    return jsonify({
        "status": "success",
        "consumed_kg": calc["consumed_kg"],
        "computed_kwh": calc["computed_kwh"],
        "net_gas_remaining_kg": calc["net_gas_kg"],
        "percent_remaining": calc["percent_remaining"],
        "is_refill_event": calc["is_refill_event"]
    }), 201

@fuel_bp.route("/kerosene", methods=["POST"])
@require_role("ADMIN")
def log_kerosene():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    log_date = data.get("log_date")
    liters = finite_number(data.get("liters_used"), 0.0)
    purpose = data.get("purpose", "Water Heating")

    if not is_iso_date(log_date) or liters is None or liters <= 0:
        return jsonify({"status": "error", "message": "Valid log_date and liters_used required"}), 400

    hid = g.current_user["household_id"]
    kwh = kerosene_to_kwh(liters)

    db = get_db()
    rate = get_tariff_rates(hid, log_date)["kerosene_per_liter"]
    cost = round(liters * rate, 2)

    db.execute(
        "INSERT INTO kerosene_logs (household_id, log_date, liters_used, computed_kwh, purpose) VALUES (?, ?, ?, ?, ?)",
        (hid, log_date, liters, kwh, purpose)
    )
    db.commit()

    return jsonify({
        "status": "success",
        "computed_kwh": kwh,
        "estimated_cost_kes": cost
    }), 201

@fuel_bp.route("/solar", methods=["POST"])
@require_role("ADMIN")
def log_solar():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    log_date = data.get("log_date")
    yield_kwh = finite_number(data.get("yield_kwh"), 0.0)
    method = data.get("log_method", "MANUAL_READING")

    if not is_iso_date(log_date) or yield_kwh is None or yield_kwh < 0:
        return jsonify({"status": "error", "message": "Valid log_date and yield_kwh required"}), 400

    hid = g.current_user["household_id"]
    db = get_db()
    sys = db.execute("SELECT id FROM solar_systems WHERE household_id = ? LIMIT 1", (hid,)).fetchone()
    sys_id = sys["id"] if sys else None
    if not sys_id:
        cur = db.cursor()
        cur.execute("INSERT INTO solar_systems (household_id) VALUES (?)", (hid,))
        sys_id = cur.lastrowid

    kwh = solar_to_kwh(yield_kwh)
    db.execute(
        "INSERT INTO solar_logs (solar_system_id, log_date, yield_kwh, log_method) VALUES (?, ?, ?, ?)",
        (sys_id, log_date, kwh, method)
    )
    db.commit()

    return jsonify({"status": "success", "computed_kwh": kwh}), 201

@fuel_bp.route("/recent", methods=["GET"])
@login_required
def recent_logs():
    hid = g.current_user["household_id"]
    db = get_db()
    
    elec_rows = db.execute(
        """SELECT al.log_date, al.created_at, 'Electricity' as source, al.runtime_hours as amount, 'hrs' as unit, al.computed_kwh, 0 as is_refill_event
           FROM appliance_logs al JOIN appliances a ON al.appliance_id = a.id
           WHERE a.household_id = ? ORDER BY al.created_at DESC, al.id DESC LIMIT 5""",
        (hid,)
    ).fetchall()

    lpg_rows = db.execute(
        """SELECT r.log_date, r.created_at, 'LPG' as source, r.consumed_kg as amount, 'kg' as unit, r.computed_kwh, r.is_refill_event
           FROM lpg_readings r JOIN lpg_cylinders c ON r.cylinder_id = c.id
           WHERE c.household_id = ? ORDER BY r.created_at DESC, r.id DESC LIMIT 5""",
        (hid,)
    ).fetchall()
    
    kero_rows = db.execute(
        """SELECT log_date, created_at, 'Kerosene' as source, liters_used as amount, 'L' as unit, computed_kwh, 0 as is_refill_event
           FROM kerosene_logs WHERE household_id = ? ORDER BY created_at DESC, id DESC LIMIT 5""",
        (hid,)
    ).fetchall()

    solar_rows = db.execute(
        """SELECT sl.log_date, sl.created_at, 'Solar' as source, sl.yield_kwh as amount, 'kWh' as unit, sl.yield_kwh as computed_kwh, 0 as is_refill_event
           FROM solar_logs sl JOIN solar_systems s ON sl.solar_system_id = s.id
           WHERE s.household_id = ? ORDER BY sl.created_at DESC, sl.id DESC LIMIT 5""",
        (hid,)
    ).fetchall()

    combined = [dict(r) for r in elec_rows] + [dict(r) for r in lpg_rows] + [dict(r) for r in kero_rows] + [dict(r) for r in solar_rows]
    combined.sort(key=lambda x: str(x.get("created_at") or x.get("log_date")), reverse=True)
    return jsonify({"status": "success", "data": combined[:10]}), 200
