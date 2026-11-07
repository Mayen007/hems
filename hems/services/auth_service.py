"""Authentication and Role-Based Access Control (RBAC) Service."""
from functools import wraps
from typing import Any
from flask import current_app, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from hems.db import get_db

def hash_password(password: str) -> str:
    """Create a salted password hash suitable for database storage."""
    return generate_password_hash(password, method="pbkdf2:sha256")

def verify_password(password_hash: str, password: str) -> bool:
    """Check a submitted password against its stored hash."""
    return check_password_hash(password_hash, password)

def generate_token(user_id: int, household_id: int, role: str) -> str:
    """Sign the identity and role claims used by authenticated requests."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    payload = {"user_id": user_id, "household_id": household_id, "role": role}
    return s.dumps(payload)

def verify_token(token: str) -> dict[str, Any] | None:
    """Decode a signed token, returning None when it is expired or invalid."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    max_age = current_app.config["TOKEN_EXPIRY_SECONDS"]
    try:
        return s.loads(token, max_age=max_age)
    except (SignatureExpired, BadTimeSignature):
        return None

def get_auth_token_from_request():
    """Read the bearer token first, falling back to the session cookie."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return request.cookies.get("hems_token")

def login_required(f):
    """Require a valid token and expose its claims as the current user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        """Reject missing or invalid sessions before invoking the route."""
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
    """Require authentication and the requested role, allowing administrators."""
    def decorator(f):
        """Wrap a route with role checks while preserving its metadata."""
        @wraps(f)
        def decorated(*args, **kwargs):
            """Authorize the request before calling the wrapped route."""
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
