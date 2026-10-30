-- SQLite schema used only by the automated test suite.
CREATE TABLE IF NOT EXISTS households (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location_county TEXT DEFAULT 'Nairobi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'ADMIN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tariffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    electricity_per_kwh REAL NOT NULL DEFAULT 28.00,
    lpg_per_kg REAL NOT NULL DEFAULT 250.00,
    kerosene_per_liter REAL NOT NULL DEFAULT 160.00,
    effective_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appliances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'OTHER',
    rated_wattage REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appliance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appliance_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    runtime_hours REAL NOT NULL,
    computed_kwh REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appliance_id) REFERENCES appliances(id) ON DELETE CASCADE,
    UNIQUE(appliance_id, log_date)
);

CREATE TABLE IF NOT EXISTS lpg_cylinders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    brand TEXT NOT NULL,
    nominal_capacity_kg REAL NOT NULL DEFAULT 13.00,
    tare_weight_kg REAL NOT NULL DEFAULT 15.20,
    is_current_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lpg_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cylinder_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    gross_weight_kg REAL NOT NULL,
    net_gas_kg REAL NOT NULL,
    consumed_kg REAL NOT NULL DEFAULT 0.00,
    computed_kwh REAL NOT NULL DEFAULT 0.000,
    is_refill_event INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cylinder_id) REFERENCES lpg_cylinders(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kerosene_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    liters_used REAL NOT NULL,
    computed_kwh REAL NOT NULL,
    purpose TEXT DEFAULT 'Water Heating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solar_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    panel_peak_watts REAL NOT NULL DEFAULT 300.00,
    battery_capacity_ah REAL,
    system_voltage REAL DEFAULT 12.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solar_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solar_system_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    yield_kwh REAL NOT NULL,
    log_method TEXT NOT NULL DEFAULT 'MANUAL_READING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (solar_system_id) REFERENCES solar_systems(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_household ON users(household_id);
CREATE INDEX IF NOT EXISTS idx_appliance_household ON appliances(household_id);
CREATE INDEX IF NOT EXISTS idx_app_log_date ON appliance_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_lpg_date ON lpg_readings(log_date);
CREATE INDEX IF NOT EXISTS idx_kero_date ON kerosene_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_solar_date ON solar_logs(log_date);
