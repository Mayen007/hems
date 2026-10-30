"""Comprehensive Integration Tests for HEMS REST API."""
import os
import tempfile
from datetime import date, timedelta
import pytest
from hems import create_app
from hems.db import init_db, seed_demo_data

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        "TESTING": True,
        "TEST_DATABASE_PATH": db_path,
        "SECRET_KEY": "test-secret-key-123",
        "TOKEN_EXPIRY_SECONDS": 3600
    })

    with app.app_context():
        init_db()
        seed_demo_data(username="abdijabar", password="SecurePassword123!")

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def get_auth_token(client):
    res = client.post("/api/v1/auth/login", json={
        "username": "abdijabar",
        "password": "SecurePassword123!"
    })
    return res.get_json()["token"]

def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "username": "abdijabar",
        "password": "SecurePassword123!"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["user"]["username"] == "abdijabar"

def test_invalid_login_and_duplicate_registration_are_rejected(client):
    bad_login = client.post("/api/v1/auth/login", json={
        "username": "abdijabar",
        "password": "incorrect"
    })
    assert bad_login.status_code == 401

    duplicate = client.post("/api/v1/auth/register", json={
        "household_name": "Duplicate Household",
        "username": "abdijabar",
        "email": "another@example.com",
        "password": "Password1234!"
    })
    assert duplicate.status_code == 400

def test_registration_and_login(client):
    res = client.post("/api/v1/auth/register", json={
        "household_name": "Kariuki Family",
        "username": "kariuki",
        "email": "kariuki@example.com",
        "password": "Password1234!"
    })
    assert res.status_code == 201
    reg_data = res.get_json()
    assert reg_data["status"] == "success"
    assert reg_data["data"]["user_id"] > 1

    login_res = client.post("/api/v1/auth/login", json={
        "username": "kariuki",
        "password": "Password1234!"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()["token"]
    tariff_response = client.get(
        "/api/v1/settings/tariffs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert tariff_response.status_code == 200
    tariffs = tariff_response.get_json()["data"]
    assert tariffs["lpg_per_kg"] == 250.0
    assert tariffs["effective_date"] == date.today().isoformat()

def test_appliance_inventory_and_batch_log(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List seeded appliances
    res = client.get("/api/v1/appliances", headers=headers)
    assert res.status_code == 200
    appliances = res.get_json()["data"]
    assert len(appliances) >= 5

    # 2. Batch log runtimes
    log_payload = {
        "log_date": "2026-10-09",
        "entries": [
            {"appliance_id": appliances[0]["id"], "runtime_hours": 24.0},
            {"appliance_id": appliances[1]["id"], "runtime_hours": 5.0}
        ]
    }
    batch_res = client.post("/api/v1/appliances/batch-log", json=log_payload, headers=headers)
    assert batch_res.status_code == 200
    data = batch_res.get_json()
    assert data["total_electricity_kwh"] > 0
    assert data["estimated_cost_kes"] > 0

    # 3. Reject duplicate appliance_ids in a single batch
    duplicate_payload = {
        "log_date": "2026-10-09",
        "entries": [
            {"appliance_id": appliances[0]["id"], "runtime_hours": 2.0},
            {"appliance_id": appliances[0]["id"], "runtime_hours": 4.0}
        ]
    }
    dup_res = client.post("/api/v1/appliances/batch-log", json=duplicate_payload, headers=headers)
    assert dup_res.status_code == 400
    assert "Duplicate appliance_id" in dup_res.get_json()["message"]

    # 4. Later submission for same date succeeds as an upsert correction
    correction_payload = {
        "log_date": "2026-10-09",
        "entries": [
            {"appliance_id": appliances[0]["id"], "runtime_hours": 12.0}
        ]
    }
    correct_res = client.post("/api/v1/appliances/batch-log", json=correction_payload, headers=headers)
    assert correct_res.status_code == 200


def test_appliance_profile_can_be_updated_and_validated(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"******"}
    appliance = client.get("/api/v1/appliances", headers=headers).get_json()["data"][0]
    updated = {
        "name": "Updated refrigerator",
        "category": "REFRIGERATION",
        "rated_wattage": 250,
    }

    response = client.put(
        f"/api/v1/appliances/{appliance['id']}",
        json=updated,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == updated["name"]

    saved = client.get("/api/v1/appliances", headers=headers).get_json()["data"][0]
    assert saved["name"] == updated["name"]
    assert saved["rated_wattage"] == updated["rated_wattage"]

    invalid = client.put(
        f"/api/v1/appliances/{appliance['id']}",
        json={**updated, "rated_wattage": -1},
        headers=headers,
    )
    missing = client.put(
        "/api/v1/appliances/999999",
        json=updated,
        headers=headers,
    )
    assert invalid.status_code == 400
    assert missing.status_code == 404

    deleted = client.delete(f"/api/v1/appliances/{appliance['id']}", headers=headers)
    repeated_delete = client.delete(
        f"/api/v1/appliances/{appliance['id']}",
        headers=headers,
    )
    assert deleted.status_code == 200
    assert repeated_delete.status_code == 404


def test_lpg_cylinder_reading_and_tare_physics(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    cyl_res = client.get("/api/v1/fuel-logs/lpg/cylinders", headers=headers)
    assert cyl_res.status_code == 200
    cylinders = cyl_res.get_json()["data"]
    assert len(cylinders) >= 1
    cyl_id = cylinders[0]["id"]

    # Log reading: previous gross was 22.10 kg, current gross 21.40 kg
    res = client.post("/api/v1/fuel-logs/lpg", json={
        "cylinder_id": cyl_id,
        "log_date": "2026-10-09",
        "gross_weight_kg": 21.40,
        "is_refill_event": False
    }, headers=headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data["consumed_kg"] == 0.70
    assert data["computed_kwh"] == 8.960
    assert data["net_gas_remaining_kg"] == 6.20
    assert data["percent_remaining"] == 47.7

def test_lpg_zero_consumption_requires_explicit_confirmation(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    cylinders = client.get(
        "/api/v1/fuel-logs/lpg/cylinders",
        headers=headers,
    ).get_json()["data"]
    cylinder_id = cylinders[0]["id"]
    payload = {
        "cylinder_id": cylinder_id,
        "log_date": "2026-10-10",
        "gross_weight_kg": 22.10,
        "is_refill_event": False,
    }

    rejected = client.post(
        "/api/v1/fuel-logs/lpg",
        json=payload,
        headers=headers,
    )
    assert rejected.status_code == 400
    assert "0 kg LPG consumed" in rejected.get_json()["message"]

    confirmed = client.post(
        "/api/v1/fuel-logs/lpg",
        json={**payload, "confirm_zero_consumption": True},
        headers=headers,
    )
    assert confirmed.status_code == 201
    assert confirmed.get_json()["consumed_kg"] == 0.0

    refill = client.post(
        "/api/v1/fuel-logs/lpg",
        json={
            **payload,
            "log_date": "2026-10-11",
            "gross_weight_kg": 28.20,
            "is_refill_event": True,
        },
        headers=headers,
    )
    assert refill.status_code == 201
    assert refill.get_json()["consumed_kg"] == 0.0
    assert refill.get_json()["is_refill_event"] is True

def test_kerosene_and_solar_logs(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Kerosene
    kero_res = client.post("/api/v1/fuel-logs/kerosene", json={
        "log_date": "2026-10-09",
        "liters_used": 1.5,
        "purpose": "Water Heating"
    }, headers=headers)
    assert kero_res.status_code == 201
    assert kero_res.get_json()["computed_kwh"] == 15.525

    # Solar
    solar_res = client.post("/api/v1/fuel-logs/solar", json={
        "log_date": "2026-10-09",
        "yield_kwh": 3.2,
        "log_method": "MANUAL_READING"
    }, headers=headers)
    assert solar_res.status_code == 201
    assert solar_res.get_json()["computed_kwh"] == 3.200

def test_dashboard_analytics_and_advisory(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "summary" in data
    assert "source_breakdown" in data
    assert "active_cylinder" in data
    assert "advisory" in data


def test_dashboard_puts_highest_spend_advice_before_solar_advice(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"******"}
    today = date.today().isoformat()

    kerosene_response = client.post("/api/v1/fuel-logs/kerosene", json={
        "log_date": today,
        "liters_used": 1.0,
    }, headers=headers)
    solar_response = client.post("/api/v1/fuel-logs/solar", json={
        "log_date": today,
        "yield_kwh": 10.0,
    }, headers=headers)
    assert kerosene_response.status_code == 201
    assert solar_response.status_code == 201

    dashboard = client.get(
        "/api/v1/analytics/dashboard", headers=headers
    ).get_json()["data"]
    advisories = dashboard["advisory"]
    assert advisories[0]["id"] == "ADV_HIGHEST_COST_SOURCE"
    assert advisories[0]["source"] == "kerosene"
    assert advisories[0]["share_pct"] == 100
    assert advisories[1]["id"] == "ADV_SOLAR_HARVEST"


def test_saved_readings_match_dashboard_hand_calculations(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    log_date = date.today().isoformat()

    initial = client.get("/api/v1/analytics/dashboard", headers=headers).get_json()["data"]
    assert initial["summary"]["total_energy_kwh"] == 0
    assert initial["summary"]["total_cost_kes"] == 0
    assert all(
        source["kwh"] == 0
        for source in initial["source_breakdown"].values()
    )

    appliance = client.get("/api/v1/appliances", headers=headers).get_json()["data"][0]
    appliance_response = client.post("/api/v1/appliances/batch-log", json={
        "log_date": log_date,
        "entries": [{"appliance_id": appliance["id"], "runtime_hours": 2}]
    }, headers=headers)
    assert appliance_response.status_code == 200
    # 220W * 2h / 1000 = 0.44 kWh  (no duty cycle)
    assert appliance_response.get_json()["total_electricity_kwh"] == 0.44

    lpg_response = client.post("/api/v1/fuel-logs/lpg", json={
        "log_date": log_date,
        "gross_weight_kg": 21.4
    }, headers=headers)
    assert lpg_response.status_code == 201
    assert lpg_response.get_json()["computed_kwh"] == 8.96

    kerosene_response = client.post("/api/v1/fuel-logs/kerosene", json={
        "log_date": log_date,
        "liters_used": 1.5
    }, headers=headers)
    assert kerosene_response.status_code == 201
    assert kerosene_response.get_json()["computed_kwh"] == 15.525

    solar_response = client.post("/api/v1/fuel-logs/solar", json={
        "log_date": log_date,
        "yield_kwh": 3.2
    }, headers=headers)
    assert solar_response.status_code == 201
    assert solar_response.get_json()["computed_kwh"] == 3.2

    dashboard = client.get("/api/v1/analytics/dashboard", headers=headers).get_json()["data"]
    assert dashboard["summary"]["total_energy_kwh"] == 24.93   # electricity + LPG + kerosene only
    assert dashboard["summary"]["solar_generated_kwh"] == 3.2
    assert dashboard["summary"]["total_cost_kes"] == 427.32
    assert dashboard["source_breakdown"]["grid_electricity"]["kwh"] == 0.44
    assert dashboard["source_breakdown"]["lpg"]["kwh"] == 8.96
    assert dashboard["source_breakdown"]["kerosene"]["kwh"] == 15.53
    assert dashboard["source_breakdown"]["solar"]["kwh"] == 3.2


def test_selected_date_report_filters_sources_and_trends(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"******"}
    today = date.today()
    today_string = today.isoformat()
    yesterday_string = (today - timedelta(days=1)).isoformat()
    appliance = client.get("/api/v1/appliances", headers=headers).get_json()["data"][0]

    appliance_log = client.post("/api/v1/appliances/batch-log", json={
        "log_date": today_string,
        "entries": [{"appliance_id": appliance["id"], "runtime_hours": 2}],
    }, headers=headers)
    lpg_log = client.post("/api/v1/fuel-logs/lpg", json={
        "log_date": today_string,
        "gross_weight_kg": 21.1,
    }, headers=headers)
    kerosene_log = client.post("/api/v1/fuel-logs/kerosene", json={
        "log_date": today_string,
        "liters_used": 2,
    }, headers=headers)
    prior_solar_log = client.post("/api/v1/fuel-logs/solar", json={
        "log_date": yesterday_string,
        "yield_kwh": 9,
    }, headers=headers)
    solar_log = client.post("/api/v1/fuel-logs/solar", json={
        "log_date": today_string,
        "yield_kwh": 3,
    }, headers=headers)
    assert [
        appliance_log.status_code,
        lpg_log.status_code,
        kerosene_log.status_code,
        prior_solar_log.status_code,
        solar_log.status_code,
    ] == [200, 201, 201, 201, 201]

    report = client.get(
        f"/api/v1/analytics/report?start_date={today_string}&end_date={today_string}",
        headers=headers,
    )
    assert report.status_code == 200
    data = report.get_json()["data"]
    assert data["summary"] == {
        "start_date": today_string,
        "end_date": today_string,
        "total_energy_kwh": 33.94,          # electricity + LPG + kerosene only
        "solar_generated_kwh": 3.0,
        "solar_savings_kes": round(3.0 * 28.0, 2),
        "total_cost_kes": 582.32,
    }
    assert data["source_breakdown"]["solar"]["kwh"] == 3
    assert data["source_breakdown"]["lpg"]["quantity"] == 1
    assert data["source_breakdown"]["kerosene"]["cost_kes"] == 320
    assert [trend["date"] for trend in data["daily_trends"]] == [today_string]

    extended_report = client.get(
        f"/api/v1/analytics/report?start_date={yesterday_string}&end_date={today_string}",
        headers=headers,
    )
    assert extended_report.status_code == 200
    extended_data = extended_report.get_json()["data"]
    assert extended_data["summary"]["total_energy_kwh"] == 33.94   # solar not included
    assert extended_data["summary"]["solar_generated_kwh"] == 12.0
    assert len(extended_data["daily_trends"]) == 2

    invalid_ranges = [
        client.get("/api/v1/analytics/report", headers=headers),
        client.get(
            "/api/v1/analytics/report?start_date=2026-02-30&end_date=2026-03-01",
            headers=headers,
        ),
        client.get(
            f"/api/v1/analytics/report?start_date={today_string}&end_date={yesterday_string}",
            headers=headers,
        ),
    ]
    assert [response.status_code for response in invalid_ranges] == [400, 400, 400]


def test_empty_report_returns_zero_without_missing_cylinder_warning(client):
    registration = client.post("/api/v1/auth/register", json={
        "household_name": "Empty Report Household",
        "username": "empty_report_user",
        "email": "empty-report@example.com",
        "password": "Password1234!",
    })
    assert registration.status_code == 201
    login = client.post("/api/v1/auth/login", json={
        "username": "empty_report_user",
        "password": "Password1234!",
    })
    assert login.status_code == 200

    today = date.today().isoformat()
    report = client.get(
        f"/api/v1/analytics/report?start_date={today}&end_date={today}"
    )
    assert report.status_code == 200
    data = report.get_json()["data"]
    assert data["summary"]["total_energy_kwh"] == 0
    assert data["summary"]["total_cost_kes"] == 0
    assert data["daily_trends"] == []
    assert "ADV_LOW_LPG" not in {
        advisory["id"] for advisory in data["advisory"]
    }


def test_tariff_update_authorization(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/settings/tariffs", json={
        "electricity_per_kwh": 30.50,
        "lpg_per_kg": 145.00,
        "kerosene_per_liter": 165.00,
        "effective_date": (date.today() + timedelta(days=7)).isoformat()
    }, headers=headers)
    assert res.status_code == 201

    get_res = client.get("/api/v1/settings/tariffs", headers=headers)
    assert get_res.status_code == 200
    assert get_res.get_json()["data"]["electricity_per_kwh"] == 30.50
    assert get_res.get_json()["data"]["effective_date"] == (
        date.today() + timedelta(days=7)
    ).isoformat()

    repeated_start = client.post("/api/v1/settings/tariffs", json={
        "electricity_per_kwh": 31.00,
        "lpg_per_kg": 150.00,
        "kerosene_per_liter": 170.00,
        "effective_date": (date.today() + timedelta(days=7)).isoformat(),
    }, headers=headers)
    assert repeated_start.status_code == 400

    parity_res = client.get("/api/v1/analytics/parity", headers=headers)
    assert parity_res.status_code == 200
    parity = parity_res.get_json()["data"]
    assert parity["lpg"]["effective_date"] == date.today().isoformat()
    assert parity["grid_electricity"]["effective_date"] == date.today().isoformat()
    assert parity["kerosene"]["effective_date"] == date.today().isoformat()
    assert parity["solar"]["effective_date"] == date.today().isoformat()

def test_tariff_start_date_preserves_old_log_costs(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"******"}
    today = date.today()
    start_date = today + timedelta(days=2)

    with client.application.app_context():
        from hems.db import get_db

        db = get_db()
        household_id = db.execute(
            "SELECT household_id FROM users WHERE username = ?",
            ("abdijabar",),
        ).fetchone()["household_id"]
        appliance_id = db.execute(
            "SELECT id FROM appliances WHERE household_id = ? LIMIT 1",
            (household_id,),
        ).fetchone()["id"]
        cylinder_id = db.execute(
            "SELECT id FROM lpg_cylinders WHERE household_id = ? LIMIT 1",
            (household_id,),
        ).fetchone()["id"]
        solar_system_id = db.execute(
            "SELECT id FROM solar_systems WHERE household_id = ? LIMIT 1",
            (household_id,),
        ).fetchone()["id"]
        day = today.isoformat()
        db.execute(
            """INSERT INTO appliance_logs
               (appliance_id, log_date, runtime_hours, computed_kwh)
               VALUES (?, ?, ?, ?)""",
            (appliance_id, day, 1.0, 1.0),
        )
        db.execute(
            """INSERT INTO lpg_readings
               (cylinder_id, log_date, gross_weight_kg, net_gas_kg,
                consumed_kg, computed_kwh, is_refill_event)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cylinder_id, day, 22.1, 6.9, 2.0, 25.6, 0),
        )
        db.execute(
            """INSERT INTO kerosene_logs
               (household_id, log_date, liters_used, computed_kwh)
               VALUES (?, ?, ?, ?)""",
            (household_id, day, 1.0, 10.35),
        )
        db.execute(
            """INSERT INTO solar_logs
               (solar_system_id, log_date, yield_kwh, log_method)
               VALUES (?, ?, ?, ?)""",
            (solar_system_id, day, 2.0, "MANUAL_READING"),
        )
        db.commit()

    before_change = client.get(
        f"/api/v1/analytics/report?start_date={today}&end_date={today}",
        headers=headers,
    ).get_json()["data"]
    assert before_change["summary"]["total_cost_kes"] == 688.0
    assert before_change["advisory"][-1]["estimated_avoided_cost_kes"] == 56.0

    update = client.post("/api/v1/settings/tariffs", json={
        "electricity_per_kwh": 30.50,
        "lpg_per_kg": 145.00,
        "kerosene_per_liter": 165.00,
        "effective_date": start_date.isoformat(),
    }, headers=headers)
    assert update.status_code == 201

    after_change = client.get(
        f"/api/v1/analytics/report?start_date={today}&end_date={today}",
        headers=headers,
    ).get_json()["data"]
    assert after_change["summary"]["total_cost_kes"] == 688.0

    historical_kerosene_log = client.post("/api/v1/fuel-logs/kerosene", json={
        "log_date": today.isoformat(),
        "liters_used": 0.1,
    }, headers=headers)
    assert historical_kerosene_log.status_code == 201
    assert historical_kerosene_log.get_json()["estimated_cost_kes"] == 16.0

    with client.application.app_context():
        from hems.db import get_db

        db = get_db()
        db.execute(
            """INSERT INTO appliance_logs
               (appliance_id, log_date, runtime_hours, computed_kwh)
               VALUES (?, ?, ?, ?)""",
            (appliance_id, start_date.isoformat(), 1.0, 1.0),
        )
        db.execute(
            """INSERT INTO lpg_readings
               (cylinder_id, log_date, gross_weight_kg, net_gas_kg,
                consumed_kg, computed_kwh, is_refill_event)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cylinder_id, start_date.isoformat(), 20.1, 4.9, 2.0, 25.6, 0),
        )
        db.execute(
            """INSERT INTO kerosene_logs
               (household_id, log_date, liters_used, computed_kwh)
               VALUES (?, ?, ?, ?)""",
            (household_id, start_date.isoformat(), 1.0, 10.35),
        )
        db.execute(
            """INSERT INTO solar_logs
               (solar_system_id, log_date, yield_kwh, log_method)
               VALUES (?, ?, ?, ?)""",
            (solar_system_id, start_date.isoformat(), 3.0, "MANUAL_READING"),
        )
        db.commit()

    later_report = client.get(
        f"/api/v1/analytics/report?start_date={start_date}&end_date={start_date}",
        headers=headers,
    ).get_json()["data"]
    assert later_report["summary"]["total_cost_kes"] == 485.5
    assert later_report["advisory"][-1]["estimated_avoided_cost_kes"] == 91.5

    dashboard = client.get(
        "/api/v1/analytics/dashboard", headers=headers
    ).get_json()["data"]
    # Dashboard now shows current month only. The start_date logs (today+2) fall
    # into next month and are intentionally excluded from the running-month snapshot.
    # Only the today-dated logs (old tariff rates) are included.
    assert dashboard["summary"]["total_cost_kes"] == 704.0
    assert dashboard["source_breakdown"]["grid_electricity"]["cost_kes"] == 28.0
    assert dashboard["source_breakdown"]["lpg"]["cost_kes"] == 500.0
    assert dashboard["source_breakdown"]["kerosene"]["cost_kes"] == 176.0
    assert dashboard["source_breakdown"]["solar"]["savings_kes"] == 56.0
    assert dashboard["advisory"][-1]["estimated_avoided_cost_kes"] == 56.0


def test_invalid_measurements_and_negative_tariffs_are_rejected(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    appliance = client.get("/api/v1/appliances", headers=headers).get_json()["data"][0]

    responses = [
        client.post("/api/v1/appliances", json={
            "name": "Missing wattage",
            "rated_wattage": -1,
        }, headers=headers),
        client.post("/api/v1/appliances/batch-log", json={
            "log_date": "2026-10-09",
            "entries": [{"appliance_id": appliance["id"], "runtime_hours": -1}]
        }, headers=headers),
        client.post("/api/v1/fuel-logs/kerosene", json={
            "log_date": "2026-10-09",
            "liters_used": "not-a-number"
        }, headers=headers),
        client.post("/api/v1/fuel-logs/lpg", json={
            "log_date": "2026-10-09",
            "gross_weight_kg": -1
        }, headers=headers),
        client.post("/api/v1/fuel-logs/solar", json={
            "log_date": "2026-10-09",
            "yield_kwh": -1
        }, headers=headers),
        client.post("/api/v1/fuel-logs/solar", json={
            "log_date": "2026-13-40",
            "yield_kwh": 1
        }, headers=headers),
        client.post("/api/v1/fuel-logs/lpg/cylinders", json={
            "brand": "Invalid tare",
            "nominal_capacity_kg": 13,
            "tare_weight_kg": -1
        }, headers=headers),
        client.post("/api/v1/settings/tariffs", json={
            "electricity_per_kwh": -1,
            "lpg_per_kg": 250,
            "kerosene_per_liter": 160,
            "effective_date": "2026-11-01"
        }, headers=headers)
    ]

    assert [response.status_code for response in responses] == [400] * len(responses)

def test_family_member_can_view_but_cannot_log_usage(client):
    with client.application.app_context():
        from hems.db import get_db
        db = get_db()
        db.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            ("MEMBER", "abdijabar")
        )
        db.commit()

    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/appliances", headers=headers).status_code == 200

    appliances = client.get("/api/v1/appliances", headers=headers).get_json()["data"]
    write_requests = [
        ("/api/v1/appliances/batch-log", {
            "log_date": "2026-10-09",
            "entries": [{"appliance_id": appliances[0]["id"], "runtime_hours": 1}]
        }),
        ("/api/v1/fuel-logs/lpg/cylinders", {"brand": "Test"}),
        ("/api/v1/fuel-logs/lpg", {
            "log_date": "2026-10-09",
            "gross_weight_kg": 22
        }),
        ("/api/v1/fuel-logs/kerosene", {
            "log_date": "2026-10-09",
            "liters_used": 1
        }),
        ("/api/v1/fuel-logs/solar", {
            "log_date": "2026-10-09",
            "yield_kwh": 1
        }),
        ("/api/v1/settings/tariffs", {})
    ]
    for path, payload in write_requests:
        response = client.post(path, json=payload, headers=headers)
        assert response.status_code == 403, path
    assert client.get(
        "/api/v1/analytics/report?start_date=2026-10-01&end_date=2026-10-31",
        headers=headers,
    ).status_code == 200

    update_response = client.put(
        f"/api/v1/appliances/{appliances[0]['id']}",
        json={
            "name": "No permission",
            "category": "OTHER",
            "rated_wattage": 100,
        },
        headers=headers,
    )
    assert update_response.status_code == 403

def test_web_index_renders_dashboard(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"HEMS Kenya" in res.data
    assert b"hero-household-name" in res.data
    assert b"bootstrap@5.3.3" in res.data
    assert b"bootstrap-icons@1.11.3" in res.data
    assert b"bi-lightning-charge-fill" in res.data
    assert b"/static/favicon.svg" in res.data
    assert b"chart.js@4.4.1" in res.data
    assert b'id="weekly-chart-state"' in res.data
    assert b'id="donut-chart-state"' in res.data
    assert b"Sign in to view household data" in res.data
    assert b"Illustrative weekly pattern" not in res.data
    assert b"Preview mix" not in res.data
    assert b"49.4%" not in res.data
    assert b"btn-fill-demo" not in res.data
    assert b"SecurePassword123!" not in res.data
    assert b'value="28.00"' not in res.data
    assert b"Sign in to view household logs." in res.data
    assert b"Sign in to view household cost comparison." in res.data
    assert b'class="card dashboard-card' in res.data
    assert b'class="modal fade"' in res.data
    assert b'class="table table-striped table-hover align-middle' in res.data

    favicon = client.get("/static/favicon.svg")
    assert favicon.status_code == 200
    assert favicon.mimetype == "image/svg+xml"

    legacy_favicon = client.get("/favicon.ico")
    assert legacy_favicon.status_code == 200
    assert legacy_favicon.mimetype == "image/svg+xml"

def test_auth_me_returns_household_and_user(client):
    token = get_auth_token(client)
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"
    assert body["user"]["username"] == "abdijabar"
    assert body["user"]["household_name"] == "Abdullahi Household"

def test_dashboard_dynamic_weekly_trends_and_recent_logs(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Verify dashboard returns weekly_trends array
    dash_res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_res.status_code == 200
    data = dash_res.get_json()["data"]
    assert "weekly_trends" in data
    assert len(data["weekly_trends"]["electricity"]) == 4
    assert len(data["weekly_trends"]["lpg"]) == 4
    assert len(data["weekly_trends"]["kerosene"]) == 4
    assert len(data["weekly_trends"]["solar"]) == 4

    kerosene_response = client.post("/api/v1/fuel-logs/kerosene", json={
        "log_date": date.today().isoformat(),
        "liters_used": 65 / 10.35
    }, headers=headers)
    assert kerosene_response.status_code == 201

    updated_dashboard = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert updated_dashboard.status_code == 200
    weekly_kerosene = updated_dashboard.get_json()["data"]["weekly_trends"]["kerosene"]
    assert weekly_kerosene[-1] == 65.0

    # Log appliance run and check recent logs
    appliances = client.get("/api/v1/appliances", headers=headers).get_json()["data"]
    client.post("/api/v1/appliances/batch-log", json={
        "log_date": "2026-10-14",
        "entries": [{"appliance_id": appliances[0]["id"], "runtime_hours": 3.5}]
    }, headers=headers)

    recent = client.get("/api/v1/fuel-logs/recent", headers=headers)
    assert recent.status_code == 200
    recent_entries = recent.get_json()["data"]
    sources = [r["source"] for r in recent_entries]
    assert "Electricity" in sources
