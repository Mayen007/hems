"""Load environment-backed settings for local and deployed HEMS instances."""
import os
from dotenv import load_dotenv
from MySQLdb.constants import FIELD_TYPE
from MySQLdb.converters import conversions


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

_MYSQL_CONVERSIONS = conversions.copy()
_MYSQL_CONVERSIONS[FIELD_TYPE.DECIMAL] = float
_MYSQL_CONVERSIONS[FIELD_TYPE.NEWDECIMAL] = float


def get_bool_env(name, default=False):
    """Parse common truthy environment-variable values."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    """Flask and database settings sourced from the process environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    USE_SQLITE = get_bool_env("USE_SQLITE")
    SQLITE_DATABASE_PATH = os.environ.get("SQLITE_DATABASE_PATH")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_DB = os.environ.get("MYSQL_DATABASE", "hems")
    MYSQL_USER = os.environ.get("MYSQL_USER", "")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_CHARSET = "utf8mb4"
    MYSQL_CURSORCLASS = "DictCursor"
    MYSQL_AUTOCOMMIT = False
    MYSQL_CUSTOM_OPTIONS = {"conv": _MYSQL_CONVERSIONS}
    TOKEN_EXPIRY_SECONDS = 86400
    DEBUG = get_bool_env("FLASK_DEBUG", default=True)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = get_bool_env("SESSION_COOKIE_SECURE")
    TESTING = False
