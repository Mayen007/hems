"""Analytics and Energy Dashboard Blueprint."""
from flask import Blueprint, jsonify, g, request
from datetime import date
from hems.services.auth_service import login_required
from hems.services.analytics_service import get_dashboard_data, get_report_data
from hems.services.tariff_service import get_fuel_parity
from hems.api.validation import is_iso_date

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    hid = g.current_user["household_id"]
    data = get_dashboard_data(hid)
    return jsonify({"status": "success", "data": data}), 200


@analytics_bp.route("/report", methods=["GET"])
@login_required
def report():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if not is_iso_date(start_date) or not is_iso_date(end_date):
        return jsonify({
            "status": "error",
            "message": "Valid start_date and end_date in YYYY-MM-DD format are required",
        }), 400
    if start_date > end_date:
        return jsonify({
            "status": "error",
            "message": "start_date must be on or before end_date",
        }), 400

    data = get_report_data(g.current_user["household_id"], start_date, end_date)
    return jsonify({"status": "success", "data": data}), 200


@analytics_bp.route("/parity", methods=["GET"])
@login_required
def fuel_parity():
    hid = g.current_user["household_id"]
    from hems.services.analytics_service import get_tariff_rates
    tariffs = get_tariff_rates(hid, date.today().isoformat())
    parity = get_fuel_parity(tariffs)
    return jsonify({"status": "success", "data": parity}), 200
