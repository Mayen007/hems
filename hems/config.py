import os
from dotenv import load_dotenv


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


def get_bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    USE_SQLITE = get_bool_env("USE_SQLITE")
    SQLITE_DATABASE_PATH = os.environ.get("SQLITE_DATABASE_PATH")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "hems")
    MYSQL_USER = os.environ.get("MYSQL_USER", "")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    TOKEN_EXPIRY_SECONDS = 86400
    DEBUG = get_bool_env("FLASK_DEBUG", default=True)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = get_bool_env("SESSION_COOKIE_SECURE")
    TESTING = False
