# BNUT implementation milestone — 2026-11-28

This is a substantial, locally verified development milestone. The complete master platform is not finished and is not ready for institutional production enrollment. Status categories below are deliberate.

## Audit and architecture

The original repository at `482996f` implemented three fixed account types, English login/queue/detail screens and a small private-ticket workflow. The dirty working tree contained useful session/browser hardening and incomplete portal models; these were preserved and integrated. The priority security defect was university-wide staff access. Both official PDFs were read completely (6 + 12 pages). Details: existing-project-audit.md and requirements/source-review.md.

The modular monolith retains existing accounts/ticketing and adds portal services. React JavaScript/Vite/Router/TanStack Query consumes DRF version-one APIs backed by real MySQL 8.0. Redis supports bounded public caching/throttles/Celery broker; worker/Beat perform SLA monitoring. Nginx provides same-origin routing; Gunicorn/static build/TLS configuration exists separately for production. ERD and domain limitations are in database/erd.md.

## Implemented and locally verified

| Environment/domain | Actual behavior |
| --- | --- |
| Public | Persian RTL home, help search with Arabic/Persian character/digit/half-space normalization, published article/detail, FAQ, current public announcements, active department directory/details, provisional about/privacy/accessibility text |
| Student | Issued-token activation/new password, session login, attention dashboard, four-stage wizard with suggestions/departments/category/forms/review, unique tracking, own queue/conversation/history/files, reply, confirmation/reopening, feedback, notifications, read-only academic profile/password/preferences |
| Staff | Authorized department queue, claim/release, public replies, internal notes, state controls and resolution summaries, manager-authorized transfer preserving history/deadlines, assigned queue |
| Manager | Scoped real counts, team workloads, recorded response/resolution mean/median and satisfaction; transfer/export permissions |
| Administration | React university overview, department/category/form/content/role/membership/calendar/holiday/SLA configuration, CSV preview/commit, settings, audit list and restricted service health; initial user creation still uses maintenance admin |
| Forms | Supported field types and server validation, conditional visibility, required/options/ranges, editor version increments, historical submission snapshot |
| SLA | Working calendars/holidays/timezone calculations, response/resolution deadlines, eligible waiting-student pause/resume, idempotent warning/breach manager notifications, timed closure |
| Privacy | Own-object restrictions, scoped staff visibility, no routine admin sensitive-content bypass, expiring grants, internal-note filtering, private MIME/signature-validated documents and generic notifications |

Security controls: Django hashes/password validation; CSRF including anonymous activation/login; HTTP-only/SameSite/production-secure cookies; Redis throttles; session-cache cancellation/clearing across accounts; plain text rendering; constrained mutation serializers; transactional locks; immutable API audit/history interfaces; protected download endpoints; bounded formula-safe CSV exports. No national-ID storage/default passwords, external credentials or real student seed data introduced.

## Executed validation

Final rebuilt runtime uses DRF 3.18.3 after dependency audit found vulnerabilities in the inherited 3.16.1 pin. Tests reran after update: **31 MySQL backend tests**, **8 frontend tests**, **4 real Chromium workflows** passed. Lint/build/migration drift/system checks passed. OpenAPI validated with zero errors and four naming warnings. Ruff passed; npm audit reported zero vulnerabilities; pip-audit reported no known vulnerabilities for the pinned runtime. These are point-in-time checks, not a security certification.

Browser tests cover guest mobile help/FAQ, real student request/dynamic form/upload and staff claim/private note/reply, student reply/resolution confirmation/feedback, another student's denied ticket/attachment, React department/category creation, and manager recorded metrics. See testing/test-results.md for failures discovered/fixed and exact limits. Not all requested E2E scenarios exist as separate cases.

## Runtime and instructions

Development MySQL/backend/frontend/Redis/Nginx are healthy; worker/Beat run and a worker ping returned pong. Periodic monitor tasks executed successfully. Migration service exited successfully. Gateway readiness returned HTTP 200. Production frontend image built and non-root Nginx config passed; production Compose validated. Full production stack/TLS is not deployed or verified. No database reset/volume deletion/restore was performed.

Run: copy/edit ignored `.env`, then `docker compose up -d --build --wait`. Website http://localhost:5173, student `/login`, staff `/staff/login`, React administration `/control/login`, Swagger http://localhost:8000/api/docs/. API base `/api/v1/`; legacy aliases remain. Use `createsuperuser` for initial administrator. See deployment/development-guide.md and production-guide.md; synthetic setup uses an operator-supplied random E2E_TEST_PASSWORD and `seed_e2e_data`, never production defaults. Backup/restore scripts and unverified drill procedure are documented in deployment/backup-and-recovery.md.

## Partial and planned scope

Incomplete: MFA/reauthentication/general password reset/session administration; complete React user CRUD; all role presets/lockout policy; Excel import; automated routing and availability assignment; full extended lifecycle/concurrent-version preconditions/submission idempotency; collaboration tasks/response templates/bulk/saved views; configurable multilevel escalation; all article review/scheduling/feedback/search analytics; complete report filters/percentiles/comparisons/asynchronous Excel/PDF; antivirus/quarantine/S3; complete confidential complaint/emergency-access approvals; complete retention purge/audit archival; full accessibility/load/security/recovery assessments and all required pages. Some models are schema drafts only; backlog names them explicitly.

Externally blocked: university-approved identity/SSO/student-system contracts, real mail/SMS/push providers/credentials, official organizational hierarchy/service calendars, branding authorization, retention/privacy/complaint policies, production host/TLS details and explicit deployment authorization. No external integration is claimed operational. Team roster/student IDs and applicable course date are missing.

## Sprint and Git delivery

Sprint 1 proposal has all thirteen required sections with actual BNUT identity and two consulted vendor comparisons; team/deadline gaps remain explicit. Sprint 2's eleven deliverables have repository evidence, including the local historical wireframe artifact/current design system and executed vertical slices. See requirements/traceability-matrix.md and reports/sprint-2-report.md. No invented Figma link, teammates or approvals.

Granular Conventional Commits preserve existing history. Starting main/remote was `482996f`; implementation on `feature/final-hardening`. Key commits: `3a6746f` audit, `b626f19` session baseline, `36e3b42` scope/lifecycle, `96df33f` public/config APIs, `447b7eb` activation/import, `8b4deb7` infrastructure/tasks, `8ed052c` private files, `013b73b` RTL foundation, `7cf02ca` public site, `328f81f` student flow, `d6f8d58` portals, `76557d6` production/backup, `01a46b5` operations, `45e7ef1` workflows, `ee5097a` integration fixes, `7b698fa` security dependency/CI update. Final docs/integration commit references and observed push/CI status are appended after execution; no force push, history rewrite or fabricated authorship.

Next priority: identity hardening before any real enrollment; complete administrator user management/import issuance; auto-routing with transaction/concurrency tests; extended lifecycle and configurable escalations; advanced reporting; isolated recovery and production integration review. The persistent backlog has exact continuation files/checks.
