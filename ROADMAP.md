# HEMS Project Roadmap

*Home Energy Consumption Management System. Based on the project proposal by Abdijabar Abdullahi (BIT/2024/62274). Development model: Agile-driven iterative prototyping. October 2026.*

## 1. Project outcome

Deliver and verify a web-based Home Energy Consumption Management System for a single Kenyan household context. Household members will manually record:

- electricity through appliance wattage and runtime hours;
- LPG through cylinder mass-drop readings in kilograms;
- solar through estimated generation yield; and
- kerosene through consumed volume in litres.

The system will convert the four sources to kilowatt-hours, calculate costs in Kenya Shillings, and present consolidated dashboards, trend charts, and rule-based efficiency tips.

The primary homeowner is the administrator. Other family members have view-only access. IoT sensors, smart plugs, direct KPLC billing APIs, and native mobile applications are outside this prototype.

## 2. Timeline at a glance

The proposal allocates 34.5 weeks across five sequential phases. Agile sprints run within the phases so that each increment is reviewed and improved before the next increment begins.

| Phase | Weeks | Agile delivery focus | Main outcome |
| --- | --- | --- | --- |
| 1. Requirements Analysis | 0 to 2.5 | Interviews, observation, document review, requirements backlog | Approved requirements and acceptance criteria |
| 2. System Architecture Design | 2.5 to 6.5 | UML, interface design, database and deployment design | Approved architecture, wireframes, and schema |
| 3. Application Engineering | 6.5 to 14 | Four implementation sprints | Working authentication, logging, calculations, dashboard, and advice |
| 4. Quality Assurance Testing | 14 to 23.5 | Unit, integration, system, responsive, and security testing | Verified prototype with corrected defects |
| 5. Final Deployment and Packaging | 23.5 to 34.5 | Pilot, accuracy verification, documentation, and packaging | Deployed prototype and final project deliverables |

## 3. Agile sprint plan

### Sprint 0: Requirements and architecture (weeks 0 to 6.5)

- Interview five target households.
- Observe electricity, LPG, solar, and kerosene tracking routines.
- Review tokens, receipts, and fuel records.
- Define functional and non-functional requirements.
- Produce UML artefacts, data-flow diagrams, wireframes, and the relational schema.
- Set up the Flask, MySQL, Bootstrap, Chart.js, and pytest development environment.

**Exit test:** the supervisor approves the requirements, architecture, wireframes, and schema.

### Sprint 1: Authentication and user management (weeks 6.5 to 8.5)

- Implement registration, login, logout, and password hashing.
- Create the homeowner administrator account.
- Add view-only family-member access.
- Protect routes with session and role checks.

**Exit test:** a homeowner can register and authenticate; a family member can view protected pages but cannot change records.

### Sprint 2: Multi-source data logging (weeks 8.5 to 10.5)

- Add appliance profiles with wattage and runtime hours.
- Add electricity, LPG, kerosene, and solar entry forms.
- Validate required fields, types, ranges, and dates on the server; require confirmation before saving a non-refill LPG reading that records zero consumption.
- Persist the records in MySQL.

**Exit test:** each source saves a valid record; invalid or negative values are rejected; zero-consumption LPG readings require explicit confirmation, while refill events remain valid.

### Sprint 3: Analytical processing and dashboard (weeks 10.5 to 12.5)

- Implement the electricity, LPG, and kerosene conversion formulas.
- Aggregate all four sources in kWh.
- Calculate source costs and total household cost in KES using the tariff effective on each log date.
- Preserve earlier cost history when a later tariff version is added.
- Present advice for the highest-spend energy source before general utilization tips.
- Build summary cards, cost comparisons, and weekly/monthly trend charts.

**Exit test:** results match hand-calculated values for the test dataset, including zero values for sources with no records; adding a later tariff does not change costs for earlier-dated logs; the highest-spend source is the first advice item.

### Sprint 4: Reporting and advisory logic (weeks 12.5 to 14)

- Add selected-timeframe reports.
- Add rule-based efficiency recommendations only when appliance-specific efficiency assumptions have comparable, cited test data.
- Add empty states, validation messages, and error handling.
- Confirm responsive rendering on mobile and desktop widths.

**Exit test:** no source-switching savings are claimed from raw input-energy rates alone, and the primary pages render without overlap from 360 px to 1920 px.

## 4. Quality assurance and hardening (weeks 14 to 23.5)

- Run unit tests for conversion and costing functions.
- Run integration tests from saved readings to dashboard output.
- Walk through every functional requirement end to end.
- Test duplicate usernames, invalid values, incorrect credentials, and access control.
- Test responsive layouts and chart rendering.
- Fix defects and update the requirements traceability, data dictionary, and documentation.

**Exit test:** all planned tests pass and no critical defect remains open.

**QA status (24 October 2026): Complete.** All 56 automated tests pass. A disposable MySQL QA household verified registration, admin and member login, appliance profile create/edit/delete, appliance/electricity logging, LPG, kerosene and solar entries, dashboard and date-filtered report calculations, invalid-input rejection, member read-only access, and logout; all QA records were deleted afterward. Browser checks exercised registration/login, appliance profile CRUD, all four source workflows, and weekly, monthly, and custom reports against an isolated SQLite database. Chart.js rendered the dashboard and report charts. No horizontal page overflow was observed at 360, 768, 1024, 1440, or 1920 px.

| Requirement | QA evidence | Status |
| --- | --- | --- |
| FR1 Authentication and access control | Registration, login/logout, password hashing, and member read/write checks in `tests/test_api_endpoints.py`, `tests/test_auth_service.py`, and the MySQL workflow | Verified |
| FR2 Appliance management | Create, edit, delete, runtime logging, validation, and role checks in `tests/test_api_endpoints.py`, the MySQL workflow, and browser checks | Verified |
| FR3 Multi-source tracking | Appliance/electricity, LPG, kerosene, solar, and invalid-input cases in `tests/test_api_endpoints.py` and the MySQL workflow | Verified |
| FR4 Engine calculations | Hand-calculated source and dashboard totals in `tests/test_api_endpoints.py`; browser totals matched; MySQL totals matched at displayed precision | Verified |
| FR5 Visual analytics and advice | Dashboard, advice, weekly/monthly/custom date ranges, report totals, source comparisons, daily trends, and chart rendering in tests and browser checks | Verified |

**Phase 4 exit criteria are met.** Pilot accuracy verification, the two-week household trial, and deployment remain Phase 5 work. An initial source package and automated test evidence have been assembled; the academic report and final packaging must be completed after pilot results are available.

## 5. Pilot and final packaging (weeks 23.5 to 34.5)

- Deploy the prototype to a low-cost hosting environment.
- Run a two-week pilot with three of the interviewed households.
- Compare system totals with household records and receipts.
- Collect usability feedback and make only approved corrective changes.
- Maintain the source package with database schema, test evidence, and user documentation; finalize the academic report after pilot results are collected and verified.

**Exit test:** the pilot accuracy report, feedback records, final documentation, and deployment package are complete.

## 6. Accuracy verification

For each pilot household:

- compare electricity estimated from appliance wattage and runtime with the household's available token or meter records;
- compare LPG kilograms calculated from cylinder weight drops with refill records;
- compare kerosene litres with receipts or household records; and
- compare calculated costs with receipts and recorded prices.

Report the percentage difference for each source and document the accepted accuracy target with the supervisor. Anonymise pilot records in the final report.

## 7. Delivery rules

- Keep the backlog as issues, each with an acceptance test.
- Plan each sprint at its start and review it with the supervisor at its end.
- Use one branch per story and commit completed features.
- Do not add features mid-sprint; record them in the backlog.
- If work slips, reduce backlog scope rather than removing tests.

## 8. Risks and mitigation

| Risk | Mitigation |
| --- | --- |
| Users forget to log usage | Keep forms short and familiar; provide clear feedback after submission. |
| Invalid or inconsistent entries | Use HTML5 constraints and server-side type and range validation. |
| Internet access interruptions | Use local browser caching to preserve dashboard stability when access is interrupted. |
| Security or access-control fault | Test authentication, password hashing, and administrator/view-only permissions throughout development. |
| Schedule or scope creep | Maintain the backlog and cut unstarted features, not tests. |

## 9. Future work

Future versions may add IoT sensors, smart plugs, KPLC or other utility integrations, native mobile applications, and broader fuel coverage such as charcoal and firewood. These are excluded from the prototype to keep the deliverable achievable within the proposal's time, budget, and skill constraints.

---

## 10. Report accuracy fixes (abdijabar.md)

The items below are corrections required to align the written report with the implemented system. Each item lists the section(s) that need updating, what the report currently says, and what it should say instead. Work through them in order; tick the checkbox when the relevant passage in `abdijabar.md` has been rewritten and cross-checked against the code.

---

### Fix 1 — Database library: replace `flask_mysqldb` with PyMySQL

- **Priority:** Critical — a named tool that does not exist in the project.
- **Sections to edit:** §3.6 (Table 3.2 justification row), §5.6 (Deployment Architecture text and Table 5.3), Appendix B notes.
- **Currently says:** "Direct SQL via `flask_mysqldb`"
- **Should say:** "Direct SQL via **PyMySQL** (`pymysql`), wrapped in a thin `MySQLConnection` / `MySQLCursor` adapter defined in `hems/db.py`. This adapter translates SQLite-style `?` placeholders to MySQL `%s` at runtime, which allows the same query strings to target either backend."
- **Also update:** Table 3.4 (Development Environment) — the library row should list PyMySQL 1.1.1, not flask_mysqldb.

---

### Fix 2 — ERD: add the `households` intermediate table

- **Priority:** High — the ERD is structurally wrong.
- **Sections to edit:** §4.3 (Entity-Relationship Overview table), §4.8 (Data Dictionary), §4.5 (Sequence of Operations).
- **Currently says:** All tables carry a direct `user_id` foreign key back to USERS.
- **Should say:** A `households` table sits between USERS and all log/appliance tables. Users belong to a household (`household_id FK`); appliances, tariffs, and all fuel logs reference `household_id`, not `user_id` directly. Update the ERD table to show HOUSEHOLDS as a parent entity and remove the `user_id` FK column descriptions from APPLIANCES and log tables.

---

### Fix 3 — Electricity table: replace `ELEC_READINGS` with `appliances` + `appliance_logs`

- **Priority:** High — the table name quoted throughout the report does not exist.
- **Sections to edit:** §4.3, §4.5, §4.8, §4.11, §5.3, §5.4, Appendix A.
- **Currently says:** Electricity is stored in `ELEC_READINGS` with a `kwh_value` field.
- **Should say:** Electricity is tracked via two tables: `appliances` (stores the appliance profile including `rated_wattage` and `default_duty_cycle`) and `appliance_logs` (one row per appliance per day, storing `runtime_hours` and `computed_kwh`). kWh is computed as `rated_wattage × runtime_hours × default_duty_cycle / 1000`. The `appliance_logs` table enforces a unique constraint on `(appliance_id, log_date)` and uses an upsert so re-submitting the same day overwrites rather than duplicates.

---

### Fix 4 — LPG table: replace `GAS_READINGS` with `lpg_cylinders` + `lpg_readings`

- **Priority:** High — same issue as Fix 3.
- **Sections to edit:** §4.3, §4.4.1 (use case narrative step 3), §4.5, §4.8, Appendix A.
- **Currently says:** LPG is stored in `GAS_READINGS` with a `kg_consumed` field; user enters weight before and after.
- **Should say:** LPG uses two tables: `lpg_cylinders` (stores brand, `nominal_capacity_kg`, `tare_weight_kg`, active flag) and `lpg_readings` (one row per weighing, storing `gross_weight_kg`, `net_gas_kg`, `consumed_kg`, `computed_kwh`, and an `is_refill_event` flag). Consumption is derived inside `hems/services/lpg_service.py` by comparing the current gross weight to the previous reading's gross weight, subtracting the tare, and applying the 12.80 kWh/kg constant. A refill is detected automatically when gross weight rises above the previous value.

---

### Fix 5 — Tariff table: document the `tariffs` table

- **Priority:** High — the table is completely absent from the ERD and data dictionary.
- **Sections to edit:** §4.3, §4.8, §5.3, §5.4.
- **Currently says:** Prices are treated as fixed constants (KES 28/kWh, KES 250/kg, KES 160/L). The ERD has no pricing table.
- **Should say:** A `tariffs` table stores time-versioned prices per household: columns `electricity_per_kwh`, `lpg_per_kg`, `kerosene_per_liter`, and `effective_date`. Each log is costed using the latest tariff whose `effective_date` is on or before the log date (`get_tariff_rates()` in `analytics_service.py`). Adding a new tariff row does not change costs for earlier-dated logs. The starting illustrative values (KES 28 / KES 250 / KES 160) are seeded as the first tariff row; households update them through the settings UI. Add TARIFFS to the ERD with a FK to HOUSEHOLDS.

---

### Fix 6 — Appliance formula: add the duty-cycle factor

- **Priority:** Medium.
- **Sections to edit:** §4.5, §5.2 (Input Design table), §5.4.
- **Currently says:** `electricity_kwh = wattage × runtime_hours / 1000`
- **Should say:** `electricity_kwh = rated_wattage × runtime_hours × default_duty_cycle / 1000`. The `default_duty_cycle` is a decimal between 0 and 1 (e.g. 0.5 for a fridge that cycles on/off). It is set per appliance at creation time and defaults to 1.0 for appliances that run continuously. Update the Input Design table (§5.2) to add a "Duty Cycle" row with constraint "Decimal 0–1, required".

---

### Fix 7 — Dual database backend: mention SQLite for testing

- **Priority:** Medium — affects reproducibility and test setup documentation.
- **Sections to edit:** §3.7 (Testing Strategy), §5.7 (Sample Test Cases), §5.8 (Testing Results).
- **Currently says:** MySQL is the only database; tests run against MySQL.
- **Should say:** The system supports a SQLite backend (activated by `USE_SQLITE=true` in `.env`) used for all automated tests and local development without a MySQL server. The `hems/db.py` adapter switches between PyMySQL and `sqlite3` at connection time. All 56 automated tests run against an in-memory or file-based SQLite database via `pytest`; the MySQL workflow was verified separately in the QA phase (see §5.8). Mention `tests/schema_sqlite.sql` as the test schema file.

---

### Fix 8 — API-level role enforcement: update §5.5 security description

- **Priority:** Low — the current wording implies template-only guards, which understates the security model.
- **Sections to edit:** §5.5 (Security Design).
- **Currently says:** "Family members with view-only access are restricted at the template level from seeing the data-entry and appliance-management forms."
- **Should say:** Role enforcement operates at two layers. At the API layer, write endpoints (`POST`, `PUT`, `DELETE`) are decorated with `@require_role("ADMIN")` in `hems/services/auth_service.py`, which returns HTTP 403 before any business logic runs if the caller's role is not ADMIN. At the presentation layer, templates additionally hide data-entry controls from non-ADMIN sessions, providing defence in depth rather than relying on UI alone.

---

### Fix 9 — Route table: correct Appendix B and §5.9.2

- **Priority:** Low — the route list omits several endpoints.
- **Sections to edit:** Appendix B (Table B.1), §5.9.2 (Table 5.8).
- **Currently says:** Routes listed are `/`, `/register`, `/login`, `/dashboard`, `/logout`, `/appliances`, `/fuel/lpg`, `/fuel/kerosene`, `/fuel/solar`.
- **Should say:** Add the following missing routes:
  - `GET /api/v1/appliances/presets` — returns a list of common Kenyan household appliance templates.
  - `POST /api/v1/appliances/batch-log` — logs runtime hours for multiple appliances in a single request for a given date.
  - `GET /api/v1/fuel/lpg/cylinders` / `POST /api/v1/fuel/lpg/cylinders` — manages registered LPG cylinders.
  - `GET /api/v1/fuel/recent` — returns the ten most recent log entries across all four sources.
  - `GET/POST /api/v1/settings/tariffs` — reads and creates household tariff records.
  - `GET /api/v1/analytics/*` — analytics and reporting endpoints.
  - All routes are prefixed under `/api/v1/`; the web/template routes are served by a separate `web_bp` blueprint.

---

### Fix 10 — `daily_energy_summary` table: add to schema documentation

- **Priority:** Low — a denormalisation table not mentioned anywhere in the report.
- **Sections to edit:** §4.3, §4.8, §5.3.
- **Should say:** A `daily_energy_summary` table stores pre-aggregated daily totals (`electricity_kwh`, `lpg_kwh`, `kerosene_kwh`, `solar_kwh`, `total_kwh`, `total_cost_kes`) per household per day, with a unique constraint on `(household_id, summary_date)`. It is populated by the analytics service and used to accelerate dashboard and report queries, avoiding full table scans of all four log tables on every page load. Note it in the Physical Design phase of §5.3.

---

### Completion checklist

| # | Fix | Report section(s) | Done |
|---|-----|--------------------|------|
| 1 | Replace `flask_mysqldb` → PyMySQL | §3.6, §5.6, Appendix B, Table 3.4 | ☐ |
| 2 | Add `households` table to ERD | §4.3, §4.5, §4.8 | ☐ |
| 3 | Replace `ELEC_READINGS` → `appliances` + `appliance_logs` | §4.3, §4.5, §4.8, §5.3, §5.4, App. A | ☐ |
| 4 | Replace `GAS_READINGS` → `lpg_cylinders` + `lpg_readings` | §4.3, §4.4.1, §4.5, §4.8, App. A | ☐ |
| 5 | Add `tariffs` table to ERD and data dictionary | §4.3, §4.8, §5.3, §5.4 | ☐ |
| 6 | Add duty-cycle factor to appliance formula | §4.5, §5.2, §5.4 | ☐ |
| 7 | Document SQLite dual backend in testing sections | §3.7, §5.7, §5.8 | ☐ |
| 8 | Clarify API-level role enforcement in security section | §5.5 | ☐ |
| 9 | Expand route table (Appendix B and §5.9.2) | App. B, §5.9.2 | ☐ |
| 10 | Document `daily_energy_summary` in schema section | §4.3, §4.8, §5.3 | ☐ |
