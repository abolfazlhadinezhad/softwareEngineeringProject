# BNUT implementation ledger

Updated 2026-11-28. The master development request supersedes the earlier prototype's exclusions. No institutional policies or official department structure are asserted. Existing dirty files at session start are preserved and reviewed; they are not attributed to a fabricated contributor.

| Requirement / task | Status | Evidence / files | Verification | Commit | Remaining limitations |
| --- | --- | --- | --- | --- | --- |
| Phase 0 repository, history, Docker and PDF audit | In progress | docs/reports/existing-project-audit.md; docs/requirements/source-review.md | Source inspection; Docker engine operational | See Git history | Re-extract source PDFs in this session |
| Preserve session cache hardening and browser-test work | Under review | accounts/tests.py; AuthProvider.jsx; frontend/e2e | Baseline checks pending | Existing uncommitted work | Do not overwrite or misrepresent baseline |
| Organization hierarchy and configurable scoped roles | Next | apps/portal models already partially drafted | New MySQL authorization tests required | — | Legacy staff sees all tickets; priority security gap |
| Ticket lifecycle, assignment, transfers, notes, privacy | Next | apps/ticketing | Core vertical slice and IDOR regression tests required | — | No department isolation or confidentiality yet |
| Public Persian website, help center and content APIs | Next | apps/portal; frontend | API and browser checks required | — | Existing UI is English and login-only |
| Redis, Celery worker/beat, Nginx and production Compose | Next | docker-compose*.yml; config | Build, health and scheduled-task checks required | — | Existing stack only backend/frontend/MySQL |
| Secure activation and identity management | Planned | accounts; portal Profile/Activation drafts | One-use activation and password policy tests | — | No predictable national-ID credentials allowed |
| Student import preview/commit CSV/XLSX | Planned | portal ImportBatch draft | Atomic import and duplicate tests | — | No importer exists |
| Versioned forms and business-calendar SLA | Planned | portal RequestForm/Calendar drafts | Calendar, holiday, validation tests | — | Models alone do not implement workflows |
| Staff/manager/admin React tools and real metrics | Planned | frontend portals | Permission, browser and data checks | — | Django admin only today |
| Private attachments and scoped reports/exports | Planned | ticketing; reports | MIME, authorization, formula injection tests | — | No storage or reports today |
| Notifications, feedback and escalation | Planned | portal model drafts | Delivery visibility and idempotency tests | — | No operational endpoints/tasks yet |
| MFA, reauthentication, reset, session revocation | Planned | accounts | Security tests | — | Production identity controls incomplete |
| Backups/recovery, CI quality, dependency/secret scanning | Planned | scripts; .github/workflows | Container validation; isolated restore | — | No production deployment authorized |
| Updated proposal, ERD, API and sprint traceability | Planned | docs | Cross-check against actual implementation | — | Team roster and applicable course deadline absent |

Next work proceeds in the order above. A task is verified only after the checks are actually executed. The final session report records exact continuation tasks if the full platform exceeds the execution session.
