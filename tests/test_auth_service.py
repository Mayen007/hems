"""Tests for Authentication and Security Service."""
from hems import create_app
from hems.services.auth_service import (
    hash_password,
    verify_password,
    generate_token,
    verify_token
)

def test_password_hashing():
    pwd = "SecretPassword123!"
    h = hash_password(pwd)
    assert h != pwd
    assert verify_password(h, pwd) is True
    assert verify_password(h, "WrongPassword") is False

def test_token_generation_and_verification():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key-123", "TOKEN_EXPIRY_SECONDS": 3600})
    with app.app_context():
        token = generate_token(user_id=1, household_id=10, role="ADMIN")
        assert token is not None
        payload = verify_token(token)
        assert payload["user_id"] == 1
        assert payload["household_id"] == 10
        assert payload["role"] == "ADMIN"
