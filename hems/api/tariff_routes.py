"""Dynamic Tariff Settings Endpoints."""
from datetime import date
from flask import Blueprint, request, jsonify, g
from hems.db import get_db
from hems.services.auth_service import login_required, require_role
from hems.services.tariff_service import DEFAULT_TARIFFS
from hems.api.validation import finite_number, is_iso_date

tariff_bp = Blueprint("tariffs", __name__)

@tariff_bp.route("", methods=["GET"])
@login_required
def get_tariffs():
    hid = g.current_user["household_id"]
    db = get_db()
    row = db.execute(
        """SELECT id, electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date
           FROM tariffs WHERE household_id = ?
           ORDER BY effective_date DESC, id DESC LIMIT 1""",
        (hid,)
    ).fetchone()
    if not row:
        return jsonify({
            "status": "success",
            "data": {**DEFAULT_TARIFFS, "effective_date": date.today().isoformat()},
        }), 200
    tariffs = dict(row)
    if hasattr(tariffs["effective_date"], "isoformat"):
        tariffs["effective_date"] = tariffs["effective_date"].isoformat()
    return jsonify({"status": "success", "data": tariffs}), 200

@tariff_bp.route("", methods=["POST"])
@require_role("ADMIN")
def update_tariffs():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "JSON object required"}), 400
    elec = finite_number(data.get("electricity_per_kwh"), DEFAULT_TARIFFS["electricity_per_kwh"])
    lpg = finite_number(data.get("lpg_per_kg"), DEFAULT_TARIFFS["lpg_per_kg"])
    kero = finite_number(data.get("kerosene_per_liter"), DEFAULT_TARIFFS["kerosene_per_liter"])
    eff_date = data.get("effective_date", date.today().isoformat())
    if any(rate is None or rate < 0 for rate in (elec, lpg, kero)) or not is_iso_date(eff_date):
        return jsonify({"status": "error", "message": "Valid non-negative tariff rates and effective_date required"}), 400
    hid = g.current_user["household_id"]

    db = get_db()
    latest = db.execute(
        """SELECT effective_date FROM tariffs WHERE household_id = ?
           ORDER BY effective_date DESC, id DESC LIMIT 1""",
        (hid,),
    ).fetchone()
    latest_date = latest["effective_date"] if latest else date.today()
    if hasattr(latest_date, "isoformat"):
        latest_date = latest_date.isoformat()
    if eff_date <= latest_date:
        return jsonify({
            "status": "error",
            "message": "effective_date must be later than the current tariff start date",
        }), 400

    cur = db.cursor()
    cur.execute(
        """INSERT INTO tariffs (household_id, electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date)
           VALUES (?, ?, ?, ?, ?)""",
        (hid, elec, lpg, kero, eff_date)
    )
    db.commit()

    return jsonify({"status": "success", "message": "Tariffs updated", "data": {"id": cur.lastrowid}}), 201
