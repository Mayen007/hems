"""Appliance Inventory and Batch Duty Cycle Endpoints."""
from flask import Blueprint, request, jsonify, g
from hems.db import get_db, MySQLConnection
from hems.services.auth_service import login_required, require_role
from hems.services.appliance_service import calculate_appliance_kwh, get_presets
from hems.services.analytics_service import get_tariff_rates
from hems.api.validation import finite_number, is_iso_date

appliance_bp = Blueprint("appliances", __name__)


def _validated_appliance_fields(data):
    name = data.get("name", "")
    name = name.strip() if isinstance(name, str) else ""
    category = data.get("category", "OTHER")
    category = category.strip() if isinstance(category, str) else ""
    wattage = finite_number(data.get("rated_wattage"), 0.0)

    if not name or not category or wattage is None or wattage <= 0:
        return None
    return name, category, wattage


@appliance_bp.route("", methods=["GET"])
@login_required
def list_appliances():
    hid = g.current_user["household_id"]
    db = get_db()
    rows = db.execute(
        """SELECT id, name, category, rated_wattage, is_active
           FROM appliances WHERE household_id = ? ORDER BY id ASC""",
        (hid,)
    ).fetchall()
    return jsonify({"status": "success", "data": [dict(r) for r in rows]}), 200

@appliance_bp.route("/presets", methods=["GET"])
def presets():
    return jsonify({"status": "success", "data": get_presets()}), 200

@appliance_bp.route("", methods=["POST"])
@require_role("ADMIN")
def create_appliance():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    fields = _validated_appliance_fields(data)
    if fields is None:
        return jsonify({"status": "error", "message": "Valid name, wattage, and duty cycle required"}), 400

    hid = g.current_user["household_id"]
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO appliances (household_id, name, category, rated_wattage)
           VALUES (?, ?, ?, ?)""",
        (hid, *fields)
    )
    db.commit()
    return jsonify({"status": "success", "data": {"id": cur.lastrowid, "name": fields[0]}}), 201


@appliance_bp.route("/<int:aid>", methods=["PUT"])
@require_role("ADMIN")
def update_appliance(aid: int):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    fields = _validated_appliance_fields(data)
    if fields is None:
        return jsonify({"status": "error", "message": "Valid name, wattage, and duty cycle required"}), 400

    hid = g.current_user["household_id"]
    db = get_db()
    appliance = db.execute(
        "SELECT id FROM appliances WHERE id = ? AND household_id = ?",
        (aid, hid),
    ).fetchone()
    if not appliance:
        return jsonify({"status": "error", "message": "Appliance not found"}), 404

    db.execute(
        """UPDATE appliances
           SET name = ?, category = ?, rated_wattage = ?
           WHERE id = ? AND household_id = ?""",
        (*fields, aid, hid),
    )
    db.commit()
    return jsonify({"status": "success", "data": {"id": aid, "name": fields[0]}}), 200

@appliance_bp.route("/batch-log", methods=["POST"])
@require_role("ADMIN")
def batch_log():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    log_date = data.get("log_date")
    entries = data.get("entries", [])

    if not is_iso_date(log_date) or not isinstance(entries, list) or not entries:
        return jsonify({"status": "error", "message": "Valid log_date and non-empty entries array required"}), 400

    validated_entries = []
    seen_appliance_ids = set()
    for item in entries:
        if not isinstance(item, dict):
            return jsonify({"status": "error", "message": "Each entry must be an object"}), 400
        aid = item.get("appliance_id")
        runtime = finite_number(item.get("runtime_hours"))
        if not isinstance(aid, int) or runtime is None or not 0 <= runtime <= 24:
            return jsonify({"status": "error", "message": "Valid appliance_id and runtime_hours from 0 to 24 required"}), 400
        if aid in seen_appliance_ids:
            return jsonify({"status": "error", "message": f"Duplicate appliance_id {aid} in batch"}), 400
        seen_appliance_ids.add(aid)
        validated_entries.append((aid, runtime))

    hid = g.current_user["household_id"]
    db = get_db()
    total_kwh = 0.0

    appliances = []
    for aid, runtime in validated_entries:
        app = db.execute(
            "SELECT rated_wattage FROM appliances WHERE id = ? AND household_id = ?",
            (aid, hid)
        ).fetchone()
        if not app:
            return jsonify({"status": "error", "message": "Appliance not found"}), 404
        appliances.append((aid, runtime, app))

    for aid, runtime, app in appliances:
        kwh = calculate_appliance_kwh(app["rated_wattage"], runtime)
        total_kwh += kwh
        if isinstance(db, MySQLConnection):
            upsert_query = """INSERT INTO appliance_logs (appliance_id, log_date, runtime_hours, computed_kwh)
                              VALUES (?, ?, ?, ?)
                              ON DUPLICATE KEY UPDATE
                              runtime_hours = VALUES(runtime_hours),
                              computed_kwh = VALUES(computed_kwh)"""
        else:
            upsert_query = """INSERT INTO appliance_logs (appliance_id, log_date, runtime_hours, computed_kwh)
                              VALUES (?, ?, ?, ?)
                              ON CONFLICT(appliance_id, log_date) DO UPDATE SET
                              runtime_hours = excluded.runtime_hours,
                              computed_kwh = excluded.computed_kwh"""
        db.execute(upsert_query, (aid, log_date, runtime, kwh))

    db.commit()
    
    # Get tariff
    rate = get_tariff_rates(hid, log_date)["electricity_per_kwh"]
    cost = round(total_kwh * rate, 2)

    return jsonify({
        "status": "success",
        "total_electricity_kwh": round(total_kwh, 3),
        "estimated_cost_kes": cost
    }), 200

@appliance_bp.route("/<int:aid>", methods=["DELETE"])
@require_role("ADMIN")
def delete_appliance(aid: int):
    hid = g.current_user["household_id"]
    db = get_db()
    appliance = db.execute(
        "SELECT id FROM appliances WHERE id = ? AND household_id = ?",
        (aid, hid),
    ).fetchone()
    if not appliance:
        return jsonify({"status": "error", "message": "Appliance not found"}), 404
    db.execute("DELETE FROM appliances WHERE id = ? AND household_id = ?", (aid, hid))
    db.commit()
    return jsonify({"status": "success", "message": "Appliance deleted"}), 200
