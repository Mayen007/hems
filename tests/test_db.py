import pytest
from unittest.mock import Mock

from hems import create_app
from hems.db import MySQLCursor, get_db, init_db, seed_demo_data


def test_mysql_cursor_translates_sqlite_placeholders():
    cursor = Mock()
    mysql_cursor = MySQLCursor(cursor)

    result = mysql_cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        ("abdijabar",),
    )

    cursor.execute.assert_called_once_with(
        "SELECT id FROM users WHERE username = %s",
        ("abdijabar",),
    )
    assert result is mysql_cursor


def test_mysql_connection_errors_are_not_hidden_by_sqlite_fallback(monkeypatch):
    def fail_mysql_connection():
        raise RuntimeError("MySQL unavailable")

    def fail_sqlite_fallback(*args, **kwargs):
        raise AssertionError("SQLite fallback should not be used")

    monkeypatch.setattr("hems.db._connect_mysql", fail_mysql_connection)
    monkeypatch.setattr("hems.db._connect_sqlite", fail_sqlite_fallback)
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key"})

    with app.app_context(), pytest.raises(RuntimeError, match="MySQL unavailable"):
        get_db()


def test_demo_seed_generates_credentials_that_can_log_in(tmp_path):
    app = create_app({
        "TESTING": True,
        "TEST_DATABASE_PATH": str(tmp_path / "demo.sqlite"),
        "SECRET_KEY": "test-key",
        "TOKEN_EXPIRY_SECONDS": 3600,
    })

    with app.app_context():
        init_db()
        credentials = seed_demo_data()
        assert credentials["username"].startswith("demo_")
        assert seed_demo_data() is None

    response = app.test_client().post("/api/v1/auth/login", json=credentials)
    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == credentials["username"]
