# Existing project audit — 2026-11-28

Repository: abolfazlhadinezhad/softwareEngineeringProject. Starting branch `feature/final-hardening`, HEAD `482996f`, also local/remote main. Existing modifications span eleven tracked files plus account test fixtures, an unfinished portal module, and browser tests. They will be preserved.

The committed implementation is a Django modular monolith with accounts and ticketing, React JavaScript/Vite/Router/TanStack Query, MySQL 8.0 and Docker Compose. It supports session/CSRF authentication, student-owned ticket creation/list/detail, staff claim/release/reply, simple status operations, activity events, API schema, tests and initial sprint documentation. Existing transactions and ownership filtering are worth preserving.

Critical gaps found by inspecting source: staff querysets are university-wide; role values are three fixed account types; no organizational scoping, confidential classification, internal notes or protected attachments; students set operational priority; status changes have only a closed-ticket guard. No secure activation/import, SLA engine, escalation task, Redis, Celery, public content endpoints, notification delivery or custom administrator portal exists in the registered application. Portal models in the dirty tree are drafts, not implemented functionality. In particular an unencrypted MFA-secret draft must not become an operational credential store.

The UI is English, login-only and shares one shell. Dashboard counts are real but narrow. No public university help journey exists. Previous documentation describes university identity as missing and excludes features that the current request explicitly mandates; those statements need superseding. Prior recorded test results are historical, not proof for current changes.

Docker Desktop is running. Baseline `docker compose up -d --build` started MySQL, migration, backend and frontend; no database volume reset was performed. Both official PDF files exist; the prior page review covers six Sprint 1 pages and twelve Sprint 2 pages. This session will independently extract the full text before updating coverage.

Architectural direction: extend the existing modular monolith with organizational/content services; retain legacy endpoints during migration to `/api/v1/`; enforce scoped querysets and service permissions together; use plaintext rendered as text for safe initial content; add purposeful public caching and scheduled background jobs. Department examples and branding are provisional configurable data. No external delivery, SSO or real-student integration will be claimed.

See `docs/backlog.md` for implementation status and evidence.
