"""Authentication and Role-Based Access Control (RBAC) Service."""
from functools import wraps
from flask import current_app, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from hems.db import get_db

def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256")

def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

def generate_token(user_id: int, household_id: int, role: str) -> str:
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    payload = {"user_id": user_id, "household_id": household_id, "role": role}
    return s.dumps(payload)

def verify_token(token: str) -> dict:
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    max_age = current_app.config["TOKEN_EXPIRY_SECONDS"]
    try:
        return s.loads(token, max_age=max_age)
    except (SignatureExpired, BadTimeSignature):
        return None

def get_auth_token_from_request():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return request.cookies.get("hems_token")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_auth_token_from_request()
        if not token:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        payload = verify_token(token)
        if not payload:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
        g.current_user = payload
        return f(*args, **kwargs)
    return decorated

def require_role(required_role: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_auth_token_from_request()
            if not token:
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            payload = verify_token(token)
            if not payload:
                return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
            if payload.get("role") != required_role and payload.get("role") != "ADMIN":
                return jsonify({"status": "error", "message": "Forbidden: insufficient permissions"}), 403
            g.current_user = payload
            return f(*args, **kwargs)
        return decorated
    return decorator
