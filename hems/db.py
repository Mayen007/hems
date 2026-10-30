"""MySQL database access with an isolated SQLite adapter for tests."""
import os
import secrets
import sqlite3
import click
from datetime import date
from typing import Any, Callable, cast
from flask import current_app, g
import pymysql
from pymysql.constants import FIELD_TYPE
from pymysql.converters import conversions
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash


class MySQLCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, parameters=()):
        self._cursor.execute(query.replace("?", "%s"), parameters)
        return self

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class MySQLConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return MySQLCursor(self._connection.cursor())

    def execute(self, query, parameters=()):
        cursor = self.cursor()
        return cursor.execute(query, parameters)

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()


def _connect_mysql():
    config = current_app.config
    if not config["MYSQL_USER"]:
        raise RuntimeError("Set MYSQL_USER before connecting to MySQL.")
    mysql_conversions = cast(
        dict[int | type[Any], Callable[[Any], str] | Callable[[str], Any]],
        conversions.copy(),
    )
    mysql_conversions[FIELD_TYPE.DECIMAL] = float
    mysql_conversions[FIELD_TYPE.NEWDECIMAL] = float
    return MySQLConnection(pymysql.connect(
        host=config["MYSQL_HOST"],
        port=config["MYSQL_PORT"],
        user=config["MYSQL_USER"],
        password=config["MYSQL_PASSWORD"],
        database=config["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        conv=mysql_conversions,
        autocommit=False,
    ))


def _connect_sqlite(db_path=None):
    if db_path is None:
        db_path = current_app.config.get("SQLITE_DATABASE_PATH") or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "hems_dev.db"
        )
    is_new = not os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    if is_new:
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "tests",
            "schema_sqlite.sql",
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    return conn


def get_db():
    if "db" not in g:
        test_db_path = current_app.config.get("TEST_DATABASE_PATH")
        if current_app.config.get("TESTING") and test_db_path:
            g.db = _connect_sqlite(test_db_path)
        elif current_app.config.get("USE_SQLITE"):
            g.db = _connect_sqlite()
        else:
            g.db = _connect_mysql()
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    if isinstance(db, sqlite3.Connection):
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "tests",
            "schema_sqlite.sql",
        )
    else:
        schema_path = os.path.join(
            os.path.dirname(__file__), "schema_mysql.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    if isinstance(db, sqlite3.Connection):
        db.executescript(schema)
    else:
        for statement in schema.split(";"):
            if statement.strip():
                db.execute(statement)
    db.commit()


def seed_demo_data(username=None, password=None):
    db = get_db()
    existing = db.execute("SELECT id FROM households WHERE id = 1").fetchone()
    if existing:
        return None

    if (username is None) != (password is None):
        raise ValueError("Provide both demo username and password, or neither.")
    if username is None:
        username = f"demo_{secrets.token_hex(4)}"
        password = secrets.token_urlsafe(24)

    # Seed Default Household
    cur = db.cursor()
    cur.execute("INSERT INTO households (name, location_county) VALUES (?, ?)",
                ("Abdullahi Household", "Nairobi"))
    hid = cur.lastrowid

    # Seed Admin User
    p_hash = generate_password_hash(password, method="pbkdf2:sha256")
    cur.execute(
        "INSERT INTO users (household_id, username, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
        (hid, username, f"{username}@example.test", p_hash, "ADMIN")
    )

    # Seed Initial Tariffs
    cur.execute(
        "INSERT INTO tariffs (household_id, electricity_per_kwh, lpg_per_kg, kerosene_per_liter, effective_date) VALUES (?, ?, ?, ?, ?)",
        (hid, 28.00, 250.00, 160.00, date.today().isoformat())
    )

    # Seed Kenya Typical Appliances
    presets = [
        ("Samsung Refrigerator 250L", "REFRIGERATION", 220.0),
        ("Living Room LED Bulbs (6x)", "LIGHTING", 60.0),
        ("Electric Kettle 1.7L", "COOKING", 1800.0),
        ("Instant Shower Head", "WATER_HEATING", 3500.0),
        ("Smart TV 43-Inch", "ENTERTAINMENT", 75.0),
    ]
    for name, cat, watt in presets:
        cur.execute(
            "INSERT INTO appliances (household_id, name, category, rated_wattage) VALUES (?, ?, ?, ?)",
            (hid, name, cat, watt)
        )

    # Seed LPG Cylinder (13kg Total, 15.2kg Tare)
    cur.execute(
        "INSERT INTO lpg_cylinders (household_id, brand, nominal_capacity_kg, tare_weight_kg) VALUES (?, ?, ?, ?)",
        (hid, "Total Gas", 13.00, 15.20)
    )
    cyl_id = cur.lastrowid

    # Seed Initial LPG Reading (Gross 22.10 kg -> Net 6.90 kg)
    cur.execute(
        "INSERT INTO lpg_readings (cylinder_id, log_date, gross_weight_kg, net_gas_kg, consumed_kg, computed_kwh, is_refill_event) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (cyl_id, "2026-10-01", 22.10, 6.90, 0.00, 0.000, 0)
    )

    # Seed Solar System (300W array)
    cur.execute(
        "INSERT INTO solar_systems (household_id, panel_peak_watts, battery_capacity_ah, system_voltage) VALUES (?, ?, ?, ?)",
        (hid, 300.0, 100.0, 12.0)
    )

    db.commit()
    return {"username": username, "password": password}


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the HEMS database.")


@click.command("seed-demo-data")
def seed_demo_data_command():
    credentials = seed_demo_data()
    if credentials is None:
        click.echo("Demo data already exists; no new login credentials were generated.")
        return
    click.echo("Seeded HEMS demo data.")
    click.echo(f"Demo username: {credentials['username']}")
    click.echo(f"Demo password: {credentials['password']}")
