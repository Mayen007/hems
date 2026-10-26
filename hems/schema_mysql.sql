CREATE TABLE IF NOT EXISTS households (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    location_county VARCHAR(100) DEFAULT 'Nairobi',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(254) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'ADMIN',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_user_household (household_id),
    CONSTRAINT fk_users_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tariffs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    electricity_per_kwh DECIMAL(10,2) NOT NULL DEFAULT 28.00,
    lpg_per_kg DECIMAL(10,2) NOT NULL DEFAULT 250.00,
    kerosene_per_liter DECIMAL(10,2) NOT NULL DEFAULT 160.00,
    effective_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tariff_household_date (household_id, effective_date),
    CONSTRAINT fk_tariffs_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS appliances (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(40) NOT NULL DEFAULT 'OTHER',
    rated_wattage DECIMAL(10,2) NOT NULL,
    default_duty_cycle DECIMAL(5,4) NOT NULL DEFAULT 1.0000,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_appliance_household (household_id),
    CONSTRAINT fk_appliances_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS appliance_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    appliance_id BIGINT UNSIGNED NOT NULL,
    log_date DATE NOT NULL,
    runtime_hours DECIMAL(5,2) NOT NULL,
    computed_kwh DECIMAL(10,3) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_appliance_log_date (appliance_id, log_date),
    INDEX idx_app_log_date (log_date),
    CONSTRAINT fk_appliance_logs_appliance FOREIGN KEY (appliance_id)
        REFERENCES appliances(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lpg_cylinders (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    brand VARCHAR(100) NOT NULL,
    nominal_capacity_kg DECIMAL(6,2) NOT NULL DEFAULT 13.00,
    tare_weight_kg DECIMAL(6,2) NOT NULL DEFAULT 15.20,
    is_current_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cylinder_household (household_id),
    CONSTRAINT fk_cylinders_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lpg_readings (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cylinder_id BIGINT UNSIGNED NOT NULL,
    log_date DATE NOT NULL,
    gross_weight_kg DECIMAL(8,2) NOT NULL,
    net_gas_kg DECIMAL(8,2) NOT NULL,
    consumed_kg DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    computed_kwh DECIMAL(10,3) NOT NULL DEFAULT 0.000,
    is_refill_event TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_lpg_date (log_date),
    CONSTRAINT fk_lpg_readings_cylinder FOREIGN KEY (cylinder_id)
        REFERENCES lpg_cylinders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kerosene_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    log_date DATE NOT NULL,
    liters_used DECIMAL(10,2) NOT NULL,
    computed_kwh DECIMAL(10,3) NOT NULL,
    purpose VARCHAR(100) NOT NULL DEFAULT 'Water Heating',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kero_date (log_date),
    CONSTRAINT fk_kerosene_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS solar_systems (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    panel_peak_watts DECIMAL(10,2) NOT NULL DEFAULT 300.00,
    battery_capacity_ah DECIMAL(10,2) NULL,
    system_voltage DECIMAL(6,2) NOT NULL DEFAULT 12.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_solar_system_household (household_id),
    CONSTRAINT fk_solar_systems_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS solar_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    solar_system_id BIGINT UNSIGNED NOT NULL,
    log_date DATE NOT NULL,
    yield_kwh DECIMAL(10,3) NOT NULL,
    log_method VARCHAR(40) NOT NULL DEFAULT 'MANUAL_READING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_solar_date (log_date),
    CONSTRAINT fk_solar_logs_system FOREIGN KEY (solar_system_id)
        REFERENCES solar_systems(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS daily_energy_summary (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    household_id BIGINT UNSIGNED NOT NULL,
    summary_date DATE NOT NULL,
    electricity_kwh DECIMAL(10,3) NOT NULL DEFAULT 0.000,
    lpg_kwh DECIMAL(10,3) NOT NULL DEFAULT 0.000,
    kerosene_kwh DECIMAL(10,3) NOT NULL DEFAULT 0.000,
    solar_kwh DECIMAL(10,3) NOT NULL DEFAULT 0.000,
    total_kwh DECIMAL(10,3) NOT NULL DEFAULT 0.000,
    total_cost_kes DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_summary_household_date (household_id, summary_date),
    INDEX idx_summary_date (summary_date),
    CONSTRAINT fk_summary_household FOREIGN KEY (household_id)
        REFERENCES households(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
