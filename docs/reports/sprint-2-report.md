# Sprint 2 report — University Support Desk

Updated November 26, 2026 (Asia/Tehran). This report maps each Sprint 2 deliverable to actual files and executed evidence. The user supplied the product concept and roles; unavailable university/team metadata is labeled in the proposal rather than fabricated.

| Deliverable | Implemented evidence | Verification / status |
| --- | --- | --- |
| Technology Stack | `backend/requirements.txt`, `frontend/package.json`, `docker-compose.yml`, `docs/architecture/architecture.md` | Selected stack matches user constraints; backend resolves Django 5.2.19/DRF 3.16.1 and frontend build passed. |
| Architecture Diagram | `docs/architecture/architecture.md` Mermaid component and deployment diagrams | Matches current Compose services and modular monolith boundaries. |
| UI/UX Design | `docs/ui-ux/design.md`, `docs/ui-ux/wireframes.html`, React `frontend/src/styles.css` and pages | Local reviewable artifact; no Figma claim. Responsive states and accessibility rules documented. |
| Project Structure | `backend/config`, `backend/apps/accounts`, `backend/apps/ticketing`, `frontend/src/{components,features,pages,services}`, `docs` | Modules have separated responsibilities; source tree is tracked. |
| Database Design and ERD | `docs/database/schema.md`, Django migrations, MySQL named volume | `migrate` runs before backend; MySQL 8.0 test verifies actual server. |
| API Documentation | `docs/api/api.md`, drf-spectacular schema, Swagger UI `/api/docs/` | `manage.py spectacular --validate` passed with zero errors; live HTTP status 200 verified. |
| Caching Strategy | Architecture document caching section | No Redis chosen; client cache invalidation and authorization boundary specified. |
| Backend / frontend source | `backend/`, `frontend/` | Docker images build; source is actual functional code. |
| Working prototype | Student login -> ticket create -> MySQL -> scoped list/detail; support claim/reply/status | 15 backend tests passed in MySQL-backed container; frontend build and six unit tests passed. |
| Automated testing | `backend/apps/accounts/tests.py`, `backend/apps/ticketing/tests.py`, frontend tests | Executed: 15 Django tests and 6 Vitest tests; no SQLite fallback. |
| README and report | `README.md`, this report, proposal/traceability docs | Setup and deliverable index included. |

## Executed checks

- `docker compose config --quiet` — PASS
- `docker compose up -d --wait` — PASS; db/backend/frontend healthy
- `python manage.py check` — PASS
- `python manage.py spectacular --validate` — PASS; 0 errors
- `python manage.py test --noinput` — PASS; 15 tests, MySQL 8.0
- `npm test` — PASS; 6 tests
- `npm run build` — PASS
- `GET http://localhost:8000/api/health/` — PASS (`{"status":"ok"}`)
- `GET http://localhost:8000/api/schema/` — PASS (HTTP 200)
- `GET http://localhost:5173` — PASS (HTTP 200)

## Git milestones

| Milestone | Branch | Commit | Integration |
| --- | --- | --- | --- |
| Requirements and PDF traceability | `docs/requirements-analysis` | `19ed47e` | Merged to `main` as `dc17ddf`; branch pushed. |
| Runtime, MySQL, initial Django/React, architecture/design | `feature/docker-infrastructure` | `8be79da`, `cb7ce0f` | Merged to `main` as `dffcd00`; branch pushed. |
| Session authentication and login UI | `feature/authentication` | `9fd388a` | Merged to `main` as `fa5d1f1`; branch pushed. |
| Ticketing vertical slice | `feature/ticket-submission` | `f1c802c` | Merged to `main` as `5466ff2`; branch pushed. |

Docs/API work is committed separately after checks and then merged to `main`. GitHub push status is reported in the final milestone update; no force push or destructive volume command was used.

## Remaining limitations

University name, team roster/student IDs, actual institutional identity rules, and current course deadline remain unavailable. Version-one exclusions are listed in the proposal and scope. Production deployment, TLS, backups, monitoring, SSO, notifications, and attachments are not claimed.
