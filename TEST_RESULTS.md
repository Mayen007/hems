# HEMS Verification Results

**Verification date:** 24 October 2026

## Automated checks

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m pytest tests -q` | 56 passed |
| `node --check .\hems\static\js\app.js` | Passed |

## Scope and limitations

The automated suite includes service-level and API integration tests using isolated SQLite databases. The application itself is configured for MySQL/MariaDB; see the QA record in [ROADMAP.md](./ROADMAP.md) for the separately recorded database and browser workflow checks.

The two-week household pilot, real-household accuracy comparison, and deployment have not been completed. These remain Phase 5 activities; software test results do not establish real-world accuracy or household acceptance.
