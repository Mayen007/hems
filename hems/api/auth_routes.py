"""Authentication Endpoints."""
from datetime import date
from flask import Blueprint, request, jsonify, make_response
from hems.db import get_db
from hems.services.auth_service import hash_password, verify_password, generate_token, login_required
from hems.services.tariff_service import DEFAULT_TARIFFS
from flask import g

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    hname = data.get("household_name", "My Household").strip()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip() or None
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return jsonify({"status": "error", "message": "Username already taken"}), 400

    cur = db.cursor()
    cur.execute("INSERT INTO households (name) VALUES (?)", (hname,))
    hid = cur.lastrowid

    p_hash = hash_password(password)
    cur.execute(
        "INSERT INTO users (household_id, username, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
        (hid, username, email, p_hash, "ADMIN")
    )
    uid = cur.lastrowid
    
    # Create default tariff for household
    cur.execute(
        "INSERT INTO tariffs (household_id, electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date) VALUES (?, ?, ?, ?, ?)",
        (
            hid,
            DEFAULT_TARIFFS["electricity_per_kwh"],
            DEFAULT_TARIFFS["lpg_per_kg"],
            DEFAULT_TARIFFS["kerosene_per_liter"],
            date.today().isoformat(),
        )
    )
    db.commit()

    return jsonify({
        "status": "success",
        "message": "User and household registered successfully",
        "data": {"user_id": uid, "household_id": hid, "role": "ADMIN"}
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db = get_db()
    user = db.execute(
        """SELECT u.id, u.household_id, u.username, u.password_hash, u.role,
                  h.name AS household_name
           FROM users u JOIN households h ON u.household_id = h.id
           WHERE u.username = ?""",
        (username,)
    ).fetchone()

    if not user or not verify_password(user["password_hash"], password):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    token = generate_token(user["id"], user["household_id"], user["role"])
    
    db.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],))
    db.commit()

    resp = make_response(jsonify({
        "status": "success",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "household_id": user["household_id"],
            "household_name": user["household_name"]
        }
    }))
    resp.set_cookie("hems_token", token, httponly=True, samesite="Lax")
    return resp, 200

@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    db = get_db()
    user = db.execute(
        """SELECT u.id, u.household_id, u.username, u.email, u.role,
                  h.name AS household_name
           FROM users u JOIN households h ON u.household_id = h.id
           WHERE u.id = ?""",
        (g.current_user["user_id"],)
    ).fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    return jsonify({
        "status": "success",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "household_id": user["household_id"],
            "household_name": user["household_name"]
        }
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"status": "success", "message": "Logged out"}))
    resp.delete_cookie("hems_token")
    return resp, 200
