# University Support Desk

University Support Desk is a private web ticketing system for university students and support staff. Students submit and follow requests; support staff search, claim, reply to, and resolve the shared queue; administrators provision accounts and manage categories.

The university name, group roster, student IDs, institutional identity provider, and final course date were not supplied. They are marked as placeholders in the [proposal](docs/proposal/project-proposal.md) rather than invented.

## Problem and version-one features

Informal support channels make it difficult to know whether a request was received, who owns it, or what remains to resolve it. The first release provides:

- administrator-provisioned session accounts with student/support/administrator roles;
- private student ticket lists and detail pages;
- categorized low/normal/high-priority requests;
- shared support queue with search, filters, pagination, assignment, and statuses;
- plain-text replies, close/reopen controls, and an activity history;
- Django administrator console for users and categories;
- responsive accessible UI with loading, error, empty, and validation states;
- generated OpenAPI/Swagger documentation and MySQL-backed automated tests.

University SSO, public registration, email/SMS, attachments, rich text, internal notes, SLA automation, real-time sockets, AI, and multi-university tenancy are explicitly outside version one. See [scope](docs/requirements/scope.md).

## Technology and architecture

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 5.2, Django REST Framework, django-filter, drf-spectacular, Gunicorn |
| Frontend | React 19 JavaScript, Vite, React Router, TanStack Query, Vitest |
| Database | MySQL 8.0, `mysqlclient`, InnoDB, utf8mb4 |
| Infrastructure | Docker Compose, persistent MySQL volume, health-gated migration/backend/frontend services |
| Source control | Git, GitHub Actions, Conventional Commits |

This is a modular monolith. Django services own ticket state transitions and transactions; DRF owns HTTP/serialization; React owns presentation and server-state fetching. The [architecture document](docs/architecture/architecture.md) contains component/deployment diagrams and the caching decision. The [ERD](docs/database/schema.md) matches the migrations.

## Directory structure

`backend/config` contains settings, URLs, errors, and WSGI. `backend/apps/accounts` contains user roles, sessions, and admin. `backend/apps/ticketing` contains models, services, API, filters, and tests. `frontend/src` contains reusable components, the auth feature, pages, and the API client. `docs` contains requirements, proposal, architecture, ERD, API, UI, and reports. `database` contains MySQL test-schema initialization. `.github/workflows` contains CI.

## Prerequisites

Install Docker Desktop with the Compose plugin. No Python, Node.js, MySQL, or application runtime is required on the host. Git is needed to clone the repository. Docker needs enough memory for the MySQL and build containers.

## Environment setup and run

From the repository root, run `Copy-Item .env.example .env`, edit `.env`, replace every `CHANGE_ME` value, and run `docker compose up --build`.

Open the frontend at http://localhost:5173, API health at http://localhost:8000/api/health/, Swagger UI at http://localhost:8000/api/docs/, OpenAPI schema at http://localhost:8000/api/schema/, and Django admin at http://localhost:8000/admin/.

Compose waits for the MySQL health check, runs migrations once, then starts the backend and frontend. MySQL data is held in the named `university-support_mysql_data` volume. Rebuilding images does not remove it. Do **not** run `docker compose down -v` unless you explicitly intend to erase local database data.

Useful commands are `docker compose ps`, `docker compose logs -f backend`, `docker compose exec backend python manage.py migrate`, `docker compose exec backend python manage.py createsuperuser`, `docker compose exec backend python manage.py shell`, `docker compose down` (keeps the named volume), and `docker compose up --build`.

The first administrator must create users and active categories in `/admin/`. Students do not self-register. To create a support user, an administrator can create a user and set `role` to **Support staff**; only the Administrator role receives admin-console access.

## Tests and quality checks

All checks run in Docker against MySQL 8.0. Run `docker compose exec backend python manage.py check`, `docker compose exec backend python manage.py test --noinput`, `docker compose exec backend python manage.py spectacular --validate --file /tmp/schema.yml`, `docker compose exec frontend npm test`, and `docker compose exec frontend npm run build`.

The CI workflow repeats Django migrations/tests/schema validation with a MySQL 8.0 service and runs frontend tests/build. Do not claim a check passed without executing it; the sprint report records the latest actual results.

## Documentation

- [Requirements source review and page traceability](docs/requirements/source-review.md)
- [Scope and acceptance criteria](docs/requirements/scope.md)
- [Requirements traceability matrix](docs/requirements/traceability.md)
- [Sprint 1 proposal](docs/proposal/project-proposal.md)
- [Architecture and caching](docs/architecture/architecture.md)
- [Database design and ERD](docs/database/schema.md)
- [API contract](docs/api/api.md)
- [UI/UX design and local wireframes](docs/ui-ux/design.md) · [wireframes artifact](docs/ui-ux/wireframes.html)
- [Sprint 2 report](docs/reports/sprint-2-report.md)

The local wireframe is a reviewable repository artifact. No Figma link is claimed because no Figma file was created.

## Team information

| Member | Student ID | Responsibilities |
| --- | --- | --- |
| `[to be supplied]` | `[to be supplied]` | `[to be supplied]` |

## Current limitations

This is an integrated course prototype, not a production institutional deployment. It needs a confirmed university identity policy, real team metadata, production TLS/reverse proxy, backup and monitoring plan, secrets manager, and stakeholder review before use with real student data.
