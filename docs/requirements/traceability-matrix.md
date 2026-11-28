# Current requirements traceability — 2026-11-28

This supersedes prior version-one exclusions and stale blocked statuses. Full supplied master scope is accepted as backlog, not all completed. Both root PDFs were read completely as extracted text (Sprint 1 six pages; Sprint 2 twelve pages) in this session. Original source SHA-256/page analysis remains in `source-review.md`.

| Master requirement group | Implementation evidence | Executed evidence | Status / remaining |
| --- | --- | --- | --- |
| Existing-code audit and incremental Git | audit report, preserved accounts/ticketing, Git commits | Source/history inspection | Implemented |
| Docker/MySQL/Redis/Celery/Nginx/Gunicorn | Compose files, images, config/celery.py | MySQL tests, dev startup, worker ping/tasks, production frontend build | Development verified; full production TLS unverified |
| Public website/help/FAQ/directory/notices | PublicView, PublicPages, search.normalize | API tests and mobile guest browser test | Implemented core; search suggestions, feedback/popularity and search gaps partial/unimplemented |
| Student identity/activation | accounts, portal/identity.py | CSRF/one-use activation/password tests | Core verified; official SSO/reset delivery/MFA absent |
| Student import | ImportBatch and CSV preview/commit UI/API | Duplicate, atomic/idempotency tests | CSV verified; XLSX and full management unimplemented |
| Organizational scope/RBAC | Department, Membership, AccessRole, RoleAssignment, permissions.py | Department isolation, manager/admin browser flows | Core verified; descendant scopes, lockout prevention and all role presets incomplete |
| Ticket creation/conversation/history | wizard, services, snapshots, Reply/TicketEvent | Student/staff browser vertical slice | Verified five-state core; full suggested lifecycle/idempotency/bulk/merge incomplete |
| Assignment/transfer/internal notes | claim/release/transfer/note operations | MySQL tests; private note browser check | Manual verified; automatic strategies stored only; cross-department tasks absent |
| Confidentiality | classification, expiring grants, scoped queries | Admin denial and staff scope tests | Core verified; independent complaint routing/emergency-access UI incomplete |
| Secure documents | TicketAttachment, private volume, download endpoints | MIME/signature/ownership tests and browser upload/denial | Core verified; antivirus/quarantine/Office/S3 absent |
| Dynamic forms | form builder, RequestForm.version, validation/snapshots | Conditional form backend/frontend tests and wizard browser | Supported text/number/options/checkbox/date/time; field-level file/read-only identity absent |
| SLA/calendar/escalation | sla.py, tasks.py, Calendar/Holiday/Policy | Holidays/weekends, idempotent breach/closure tests, live scheduled tasks | Core verified; configurable multilevel/escalation lifecycle incomplete |
| Notifications/feedback | in-app APIs/UI and generic previews; one-per-ticket Feedback | Browser feedback and task idempotency tests | Core implemented; channel adapters/delivery history absent |
| Staff/manager portals | scoped queue/workspace and recorded metrics | Staff/manager browser checks | Core verified; advanced filters/templates/availability editor/productivity partial |
| Custom React administration | backend metadata/resource editors and dashboards | Create department/category through actual UI | Core verified; complete student/employee management and policy editors incomplete |
| Reporting/exports | dashboard real counts/mean/median/satisfaction, scoped CSV | Operational browser/authorization checks | Basic implemented; all report filters, percentiles, asynchronous XLSX/PDF absent |
| Persian RTL/accessible responsive design | fa RTL, Vazirmatn, reusable controls, provisional navy brand | Frontend tests, browser 390px check, lint/build | Core verified; WCAG/multi-browser/full responsive audit pending |
| Security/observability/operations | cookies/CSRF, privacy filtering, audits, service health, dependency audit | Tests, npm/pip audit, worker heartbeat | Partial; MFA/reauth/log correlation/audit immutability/DR drill pending |
| Production/backup/recovery | production Compose, TLS gateway template, scripts/docs | Config validation, static production image/nginx validation | Implemented config; full TLS deployment and isolated restore not executed |
| University integration/branding/policy | explicit approvals and limitations | No fabricated endpoints/credentials | Externally blocked; independent work continues |

## Sprint coverage

Sprint 1 p2-6's thirteen required proposal sections are present in `proposal/project-proposal.md`, including two real comparable systems and consulted sources. University/product/repository are known. Actual member roster/student IDs and applicable course deadline remain absent; no contributor assignments or university approvals are fabricated.

Sprint 2 p11's eleven deliverables map to: pinned stack; `architecture/system-architecture.md`; `ui-ux/design-system.md` and historical local wireframe; feature-organized source; `database/erd.md` and MySQL migrations; `api/api-reference.md`/generated schema; architecture caching section; source tree; four executed real browser flows; backend/frontend tests; README and `reports/sprint-2-report.md`. The p9 security criteria have implemented controls and explicit production gaps. The p10 actual teamwork/contribution requirement can only reference genuine Git history; roster still needed. No complete-project or institutional deployment claim follows from Sprint 2 coverage.
