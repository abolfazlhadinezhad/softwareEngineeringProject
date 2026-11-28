# BNUT — سامانه پاسخگویی و پشتیبانی دانشجویان

A Persian-first university support platform for **Babol Noshirvani University of Technology — دانشگاه صنعتی نوشیروانی بابل**. This repository extends the existing working Django/React/MySQL prototype incrementally; it is a development milestone, **not a completed production platform**. Official branding, organizational policies and integrations have not been approved.

Implemented: public help center with normalized Persian search, FAQs/directory/notices; student request wizard with dynamic forms; private conversation/uploads and tracking; scoped staff queues/claim/reply/internal notes/transfers; resolution confirmation/reopening/feedback; manager and university dashboards using recorded data; custom React organization/content/role/form/calendar/settings management; activation and CSV preview/atomic import; in-app notifications; business-hour SLA monitoring and automatic closure.

Stack: Python 3.12, Django 5.2, Django REST Framework, MySQL 8.0, React **JavaScript**, Vite, React Router, TanStack Query, Redis, Celery/Beat, Nginx and Gunicorn. Dependencies are pinned; all application runtimes and checks run in Docker.

## Run locally

Install Docker Desktop with Compose and Git. Copy `.env.example` to ignored `.env`, replace every CHANGE_ME secret, then:

```powershell
docker compose up -d --build --wait
docker compose exec backend python manage.py createsuperuser
```

Public site: http://localhost:5173 · Student: /login · Staff/manager: /staff/login · React admin: /control/login · Gateway: http://localhost:8080 · Swagger: http://localhost:8000/api/docs/ · Restricted Django maintenance: http://localhost:8000/admin/.

Default Compose is development with hot reload. Persistent MySQL/Redis/private-media volumes survive container rebuilds. Never delete volumes or reset the database without explicit approval. Legacy staff need department memberships; imported students start inactive with no password. Production uses a separate standalone Compose file and requires approved TLS/identity/retention configuration; no production deployment has occurred.

See [development commands and synthetic accounts](docs/deployment/development-guide.md), [production configuration](docs/deployment/production-guide.md), [backup and recovery](docs/deployment/backup-and-recovery.md).

## Verification

```powershell
docker compose exec -T backend python manage.py test --noinput
docker compose exec -T backend python manage.py spectacular --validate --file /tmp/schema.yml
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run build
```

[Browser workflow instructions](docs/deployment/development-guide.md) cover public Persian help, student/staff conversation and privacy, manager metrics and administrator configuration. Tests use **MySQL 8.0**, never SQLite. [Test evidence](docs/testing/test-results.md) records executed results; hosted CI is distinct from local checks.

## Source and documentation

`backend/apps/accounts`: user/session authentication; `ticketing`: ticket models, scoped transactional services, private files; `portal`: organization/RBAC, content, identity/import, forms/SLA, notifications, analytics/operations. `frontend/src`: shared components, auth provider, role-specific pages, public site and services. `nginx`, `scripts`, Compose and Dockerfiles provide runtime operations.

- [Existing project audit](docs/reports/existing-project-audit.md) and [living backlog](docs/backlog.md)
- [Sprint 1 proposal](docs/proposal/project-proposal.md)
- [Official PDF page review](docs/requirements/source-review.md) and [current coverage](docs/requirements/traceability-matrix.md)
- [Architecture and cache strategy](docs/architecture/system-architecture.md), [ticket state machine](docs/architecture/ticket-lifecycle.md)
- [Current ERD](docs/database/erd.md), [API contracts](docs/api/api-reference.md)
- [Permission matrix](docs/security/permission-matrix.md), [privacy and institutional approvals](docs/security/privacy-and-retention.md)
- [Design system/user flows](docs/ui-ux/design-system.md); [original wireframe artifact](docs/ui-ux/wireframes.html) retained as prototype history, no fabricated Figma link
- [Implementation report](docs/reports/implementation-2026-11-28.md), [Sprint 2 coverage](docs/reports/sprint-2-report.md)

## Remaining scope

MFA/reauthentication, complete user/session/reset administration, Excel import, automated assignment, full extended lifecycle/collaboration, configured multilevel escalations, reusable reply templates, content feedback/moderation details, comprehensive reporting/async XLSX/PDF, storage/antivirus adapters, full accessibility/load/security review and tested disaster recovery remain incomplete. Some models represent future workflows; model existence is not a completion claim. Exact next tasks are in the backlog.

No external SSO/student-system/email/SMS/push credentials or endpoints were supplied; those integrations are not operational. Sample accounts and department data are synthetic/provisional. Team roster/student IDs and applicable course deadline remain to be supplied; no contributors or approvals are invented.

