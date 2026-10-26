# HEMS Technical Specification

*Home Energy Consumption Management System. Based on the project proposal by Abdijabar Abdullahi (BIT/2024/62274). October 2026.*

## 1. Purpose and scope

HEMS is a web-based platform for tracking multi-source domestic energy consumption in Kenyan households. It gives a household one place to record electricity, LPG, solar, and kerosene data, convert the data to a common energy unit, calculate costs in Kenya Shillings, and view trends and efficiency advice.

The prototype uses manual entry. It does not include IoT sensors, smart plugs, direct KPLC or other utility APIs, native iOS or Android applications, or automated hardware control.

### 1.1 Users

- **Homeowner:** primary administrator with full data-entry and management privileges.
- **Family member:** authenticated view-only user who can view dashboards and reports but cannot modify records.

The initial design supports one primary administrator and one household context. Monetary values are recorded and displayed in KES.

### 1.2 Functional scope

1. Register, authenticate, and log out users.
2. Manage appliance profiles, wattage ratings, and runtime hours.
3. Record electricity, LPG, solar, and kerosene readings.
4. Convert readings to kWh and calculate per-source and total costs.
5. Display summary cards, cost comparisons, historical weekly/monthly trends, and reports.
6. Display a rule-based tip about the more cost-efficient source where the comparison supports one.

## 2. Technology and architecture

| Tier | Technology | Responsibility |
| --- | --- | --- |
| Presentation | HTML5, CSS3, Bootstrap 5, Chart.js | Responsive forms, dashboards, charts, and reports |
| Application | Python 3.x, Flask | Routes, sessions, validation, calculations, and advisory logic |
| Data | MySQL | Persistent relational storage for users, appliances, and readings |
| Testing | pytest | Unit, integration, and application tests |

The application uses a three-tier structure:

```text
Browser
  -> Flask routes and services
      -> MySQL
```

Routes handle HTTP concerns and call services for conversion, costing, aggregation, and advisory calculations. Services do not depend on Flask so that calculation logic can be unit tested independently. Database queries use parameterised statements.

Suggested project structure:

```text
hems/
  create_app.py
  config.py
  api/
    auth_routes.py
    appliance_routes.py
    fuel_routes.py
    analytics_routes.py
  services/
    auth_service.py
    appliance_service.py
    conversion.py
    costing.py
    aggregation.py
    advisory.py
  schema.sql
  templates/
  static/
tests/
```

## 3. Data model

The database links one household administrator and view-only family members to the household's appliances and readings. Every reading includes a date and the user who created it.

| Entity | Important fields | Rules |
| --- | --- | --- |
| users | id, username, password_hash, role | Username is unique. Password is never stored in plain text. |
| households | id, name | Represents the household context. |
| appliances | id, household_id, name, wattage_w | Wattage is positive. |
| appliance_usage | id, appliance_id, log_date, hours | Runtime is between 0 and 24 hours. |
| electricity_readings | id, household_id, log_date, kwh | Supports the electricity record used for comparison or verification. |
| lpg_readings | id, household_id, log_date, kg_consumed | Stores cylinder mass-drop consumption in kilograms. |
| kerosene_logs | id, household_id, log_date, litres_used | Stores volumetric consumption in litres. |
| solar_logs | id, household_id, log_date, kwh_yield | Stores estimated solar generation. |
| prices | id, fuel, price_kes, effective_from | Stores the average or configured price used by the calculation. |

Use foreign keys for household and appliance relationships, indexes on household and date fields, and decimal types for energy, quantity, and price values. A household deletion must remove its dependent records.

## 4. Input and validation rules

All forms use client-side constraints for immediate feedback and server-side validation before database writes.

| Field | Rule |
| --- | --- |
| Username | Required, unique, and 3 to 80 characters |
| Password | Required and at least 6 characters before hashing |
| Appliance name | Required text |
| Wattage | Required positive number |
| Runtime hours | Required number from 0 to 24 |
| LPG quantity | Non-negative decimal in kilograms |
| Kerosene quantity | Non-negative decimal in litres |
| Solar yield | Non-negative decimal in kWh |
| Electricity value | Non-negative decimal in kWh |
| Reading date | Required date; future dates are rejected |

On a failed submission, show a clear validation or connection error and preserve the entered form values. Do not show raw database errors to users.

## 5. Calculation rules

### 5.1 Conversion constants

Keep the constants in configuration so that they can be cited, reviewed, and changed without rewriting route code:

- Grid electricity: `1.00 kWh = 1.00 kWh`.
- LPG: `1 kg = 12.80 kWh`.
- Kerosene: `1 litre = 10.35 kWh`.

### 5.2 Energy totals

For a selected period:

```text
electricity_kwh = sum(wattage_w * runtime_hours / 1000)
lpg_kwh        = sum(kg_consumed * 12.80)
kerosene_kwh   = sum(litres_used * 10.35)
solar_kwh      = sum(kwh_yield)
total_kwh      = electricity_kwh + lpg_kwh + kerosene_kwh + solar_kwh
```

Where an actual electricity reading is available for the period, it may be compared with the appliance/runtime estimate. A period with no reading for a source returns `0.00`, not an error.

### 5.3 Costs and advice

```text
source_cost = source_quantity * configured_price
total_cost  = sum(source_cost for the selected period)
```

The prototype stores household-configurable prices in KES and displays the effective date of the active tariff set in the fuel comparison. Each tariff row is a start date: a log uses the latest tariff effective on or before its log date. A new tariff must start after the latest saved tariff date, so it cannot replace an earlier tariff period. Its start date applies inclusively. Its starting values are grid KES 28.00/kWh, LPG KES 250.00/kg, kerosene KES 160.00/litre, and solar KES 0.00/kWh marginal cost. The LPG starting value is a representative estimate based on a KES 3,250 13 kg refill (KES 250/kg); the supplied Kenyan retail ranges vary by cylinder size, brand, and location. It is not a live market quote. Households should enter their actual prices and the date those prices apply.

The dashboard fuel comparison is a raw input-energy comparison: retail price divided by the source's energy content (KES per kWh of fuel/electricity input). It does not compare useful cooking heat or the cost of completing the same cooking task. Appliance efficiencies vary by model, condition, cookware, and use, so the dashboard does not claim that LPG is inherently more efficient or kerosene is inherently more expensive. Its badges rank the displayed input-energy rates, not appliance performance. Solar is shown separately at zero marginal energy cost.

Do not describe these input-energy rates as useful-heat costs. A useful-heat comparison requires appliance-specific efficiency values measured under a common cooking-task protocol and disclosed with their sources. For example, the published heterogeneous stove-testing study of three kerosene stoves reports model-specific test results rather than a universal kerosene efficiency ([Jetter et al., 2012](https://doi.org/10.1016/j.esd.2012.06.002)). Until comparable values for the household's electric, LPG, and kerosene appliances are available, no useful-heat ranking or fuel-switching savings recommendation is made from these rates.

## 6. Functional requirements

| ID | Requirement | Acceptance test |
| --- | --- | --- |
| FR1 | Authentication and access control | Registration hashes the password; users can log in and out; a family member can view but cannot modify records. |
| FR2 | Appliance management | The administrator can add, edit, and delete appliance profiles and log runtime hours. |
| FR3 | Multi-source tracking | The administrator can save valid electricity, LPG, solar, and kerosene records; invalid values are rejected. |
| FR4 | Engine calculations | The system converts readings to kWh and costs in KES using the stated constants and configured prices. |
| FR5 | Visual analytics and advice | The selected timeframe shows totals, cost comparisons, trend charts, reports, and a rule-based advisory message. |

## 7. Routes and access

| Route | Methods | Access |
| --- | --- | --- |
| `/` | GET | Public landing or login page |
| `/register` | GET, POST | Public |
| `/login` | GET, POST | Public |
| `/logout` | POST | Authenticated users |
| `/appliances` | GET, POST | Administrator changes; family member read-only |
| `/appliances/<id>/usage` | POST | Administrator |
| `/log/electricity` | GET, POST | Administrator |
| `/log/lpg` | GET, POST | Administrator |
| `/log/kerosene` | GET, POST | Administrator |
| `/log/solar` | GET, POST | Administrator |
| `/dashboard` | GET | Administrator and family member |
| `/reports` | GET | Administrator and family member |

Route-level access checks are mandatory. Hiding a form in a template is not access control.

## 8. Security and non-functional requirements

- Hash passwords with a standard Werkzeug method such as `pbkdf2:sha256`; never encrypt or log plain-text passwords.
- Use a secret key loaded from configuration or the environment.
- Use parameterised SQL statements.
- Validate every input on the server, including values submitted after browser validation is bypassed.
- Use secure session handling and expire inactive sessions appropriately.
- Do not expose raw database errors or secrets.
- Keep the interface usable without horizontal scrolling from 360 px to 1920 px.
- Keep conversion and costing logic separate from routes for maintainability.

## 9. Testing strategy

Testing runs continuously during the Agile sprints:

| Level | Scope | Timing |
| --- | --- | --- |
| Unit | Conversion, costing, aggregation, and advisory functions | Every sprint |
| Integration | Saved readings through to dashboard totals | From Sprint 2 |
| System | Registration, data entry, dashboards, reports, and access control | Quality assurance phase |
| User acceptance | Three pilot households recording real data for two weeks | Final deployment phase |

Required cases include:

- 1 kg LPG returns 12.80 kWh and 3 kg returns 38.40 kWh.
- Kerosene conversion rounds consistently to the displayed precision.
- A period with no kerosene records returns `0.00` without an error.
- Negative wattage and negative fuel quantities are rejected server-side.
- Duplicate usernames are rejected.
- Incorrect credentials do not authenticate.
- A family-member write request is rejected.
- The dashboard renders a weekly trend for four weeks of data.
- Actual electricity records can be compared with appliance/runtime estimates.

## 10. Constraints and future extensions

Accuracy depends on consistent manual input and the representativeness of the conversion constants and configured prices. The prototype assumes access to a browser and an intermittent but usable internet connection.

Future work may add automated sensors, smart plugs, utility integrations, native mobile applications, and charcoal or firewood tracking. These items are not part of the proposal's prototype scope.
