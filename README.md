# HEMS

HEMS is a Flask web application with a MySQL data store, Bootstrap 5 frontend, and Chart.js visualisations. MySQL is the only supported application database; the test suite uses isolated SQLite databases.

## Project structure

```text
hems/
  api/          Flask API routes
  services/     Energy, tariff, analytics, and authentication logic
  web/          Browser-facing routes
  templates/    Server-rendered HTML
  static/       CSS, JavaScript, and web assets
  config.py     Environment-based settings
  db.py         MySQL access and database CLI commands
  schema_mysql.sql
tests/
  schema_sqlite.sql   Test-only database schema
  test_*.py           Unit and integration tests
app.py          WSGI entry point
run.py          Local development server
```

## Features

- Household accounts with administrator and view-only family-member access.
- Appliance profile creation, editing, and deletion, with runtime-based electricity logging.
- LPG, kerosene, and solar logging with kWh normalization and KES cost estimates.
- Start-dated tariff history that preserves historical cost calculations; fuel comparison is labeled as input-energy cost, not appliance efficiency.
- Explicit confirmation for non-refill LPG readings that record zero consumption.
- Dashboard charts and reports for this week, this month, or a custom date range.

## Prerequisites

For a local development installation, have:

- Windows 10/11 with PowerShell (the commands below use PowerShell syntax).
- Python 3.11 or newer, available as `py` or `python`.
- MySQL Server 8.0 or newer, running locally or at a host reachable from this computer. XAMPP, MySQL Installer, or another MySQL distribution can provide the server.
- A modern browser. The page loads Bootstrap and Chart.js from jsDelivr, so the browser needs internet access to load those frontend libraries.

Apache is not required when using WampServer or XAMPP. The Flask development server serves the application.

## Install and run on Windows

Run the following commands from the project root (the folder containing `requirements.txt`).

### 1. Create the database in phpMyAdmin

Start WampServer and make sure its MySQL/MariaDB service is running. In phpMyAdmin, create an empty database named `hems` if it does not already exist. You do not need to run SQL statements or create a separate database user when using the existing local credentials configured in `.env`.

`flask --app app init-db` creates the application tables inside this database; it does not create the database itself.

### 2. Create the Python environment

In PowerShell:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the Python launcher is unavailable, replace `py -3` with `python`. If PowerShell blocks environment activation, use the environment's executables directly instead:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Configure the application

The project `.env` file contains the MySQL connection settings. Keep its `MYSQL_DATABASE` value set to `hems`, and ensure the host and port match your WampServer setup. This local installation may use WampServer's existing `root` account with a blank password if that is how your MySQL/MariaDB service is configured; confirm the values with your phpMyAdmin setup. This root-without-a-password configuration is for local development only, not for a networked or production deployment.

If you need to create `.env` for a fresh checkout, copy the example first, then edit it:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set `SECRET_KEY` to a private random value; generate one with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the generated value into `.env`. Keep `.env` private; it is excluded by Git.

### 4. Initialize the database and start HEMS

With the virtual environment activated:

```powershell
flask --app app init-db
python run.py
```

Open <http://127.0.0.1:5000/> in your browser. Keep the PowerShell window running while using the app; press **Ctrl+C** there to stop the server. To use a different port, set `PORT` before starting it, for example:

```powershell
$env:PORT = "5050"
python run.py
```

### Optional: load demo data

For local evaluation only, stop the server if it is running, then run:

```powershell
flask --app app seed-demo-data
```

The command prints a randomly generated demo username and password. Save them for sign-in. Seeding an already populated database does not create replacement credentials. Do not seed demo data in a production database.

## Troubleshooting

- **MySQL connection error:** confirm the MySQL service is running and that the host, port, database, username, and password in `.env` are correct.
- **`SECRET_KEY` error:** confirm `.env` exists in the project root and contains a non-empty `SECRET_KEY`.
- **`flask` or package command not found:** activate `venv`, or invoke the command using `.\venv\Scripts\flask.exe` / `.\venv\Scripts\python.exe`.
- **Frontend styles or charts are missing:** check that the browser can reach jsDelivr.

## Run tests

The test suite uses isolated SQLite databases and does not need the MySQL service:

```powershell
python -m pytest
```