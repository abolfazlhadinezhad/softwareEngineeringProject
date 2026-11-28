# Executed test evidence — 2026-11-28

Environment: Windows PowerShell host, Docker Desktop Linux containers, Python 3.12, Django 5.2.19, DRF 3.18.3, MySQL 8.0, Node 24, Chromium Playwright 1.65.1. All application checks were executed inside containers. No destructive volume removal or database restore occurred.

| Check | Observed result |
| --- | --- |
| Original baseline Django tests | 17 passed before implementation |
| Final MySQL backend suite | 32 passed; 9.757 seconds after DRF update and maintenance access hardening |
| Frontend Vitest | 8 passed |
| Chromium integration | 4 passed; 38.9 seconds after DRF update |
| ESLint | Pass |
| React production build | Pass; 105 modules, JS bundle approx. 367 kB / 111 kB gzip |
| Django system check | Pass |
| Migration drift | No changes detected |
| OpenAPI validation | 0 errors; 4 warnings (enum naming and shared public-resource operation IDs) |
| Ruff | All checks passed |
| npm dependency audit | 0 vulnerabilities reported |
| pip-audit of fully pinned runtime | No known vulnerabilities after DRF upgrade |
| Production frontend Docker image | Built `bnut-frontend:production-check`; non-root `nginx -t` passed |
| Development Compose | Config and build/start passed; db/backend/frontend/Redis/Nginx healthy; worker and Beat running |
| Production Compose | `config --quiet` passed with example environment; not deployed |
| Worker | Inspect ping returned pong; Beat-triggered monitor executions recorded successful tasks |

During verification, browser tests exposed public-query cancellation at anonymous session initialization, an administrator path/proxy collision, duplicated attachment UI and metadata method collisions. These were corrected and the browser suite rerun successfully. Attachment streaming tests initially closed Django's test response prematurely, disrupting the enclosing test transaction; the test now consumes the response stream and passes. Dependency audit found five DRF 3.16.1 advisories; pin upgraded to 3.18.3, image rebuilt and tests/audit rerun. These failures are not omitted or reported as successes.

Final maintenance-console regression additionally verifies direct ticket status editing is denied and confidential ticket titles are absent from maintenance lists. Ticket events are also scoped and immutable through maintenance APIs.

Not executed: full production TLS deployment, restore rehearsal, formal WCAG/load/security assessment, university SSO/external notification delivery. Hosted CI status is recorded separately in the delivery report after push.

Hosted evidence: feature run 46108875895 and main merge run 46108920694 both completed successfully (container integration and Python quality). The subsequent maintenance hardening commit has a local 32-test pass and triggers its own hosted run; do not conflate the earlier successful commit with later pending revisions.
