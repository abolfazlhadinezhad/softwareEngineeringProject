# BNUT persistent progress and continuation ledger

Updated 2026-11-28. Full master scope remains the target; this session delivers a tested milestone, not the complete platform. See requirements/acceptance-criteria.md, traceability-matrix.md and reports/implementation-2026-11-28.md.

| Requirement/task | Implementation status | Relevant files | Test status | Commit evidence | Remaining limitations |
| --- | --- | --- | --- | --- | --- |
| Audit existing project/history/PDFs | Verified | reports/existing-project-audit.md; requirements/source-review.md | Code/history read; all 18 PDF pages read | 3a6746f, f492caa | Team roster/deadline absent |
| Preserve prior dirty session/browser work | Verified | accounts tests/seed; AuthProvider; e2e | Baseline 17 backend/7 frontend, then expanded checks | b626f19 | Original dirty changes preserved and reviewed |
| Department hierarchy/scoped roles | Core verified | portal/models.py, permissions.py, serializers.py/views.py | Scope/IDOR/confidential/admin creation tests | 36e3b42, 96df33f | No descendant inheritance, full presets/lockout policy/user CRUD |
| Guarded ticket lifecycle/ownership | Core verified | ticketing/services.py, models.py, serializers.py/views.py | Backend and complete browser flow | 36e3b42, 328f81f | Five states; extended lifecycle/idempotent submit/stale-version guards pending |
| Manual assignment/transfer/internal notes | Verified core | ticketing/services.py; TicketDetailPage | Conflicting claim, history/scope transfer, note privacy | 36e3b42, 328f81f | Auto-assignment, collaboration tasks, templates absent |
| Public Persian help/directory/notices | Core verified | portal/search.py/views.py; PublicPages.jsx | API search/publication and mobile browser | 96df33f, 7cf02ca | Article/FAQ feedback, scheduling/moderation/search analytics incomplete |
| Redis/Celery/Beat/Nginx | Verified development | Compose; config/celery.py; portal/tasks.py; nginx | Build/up/health/ping and scheduled tasks observed | 8b4deb7, 7b698fa | Full production operational hardening pending |
| Secure activation/password/profile | Core verified | portal/identity.py; accounts; AccountPages/LoginPage | CSRF/token expiry/reuse/password tests | 447b7eb, d6f8d58 | MFA/reauth/reset/session management required before real enrollment |
| Student import preview/commit | CSV verified | identity.py; ImportBatch; AccountPages | Preview/duplicate/atomic/idempotency tests | 447b7eb, 45e7ef1 | XLSX/import purge and complete account management absent |
| Versioned dynamic forms | Core verified | portal/forms.py; RequestForm; DynamicFields; wizard; form builder | Backend snapshots/conditional requirements + frontend + browser | 36e3b42, 328f81f, d6f8d58 | File/read-only student fields, immutable form-version rows/richer builder pending |
| Business-hour SLA and monitoring | Core verified | portal/sla.py/tasks.py; calendar/policy models | Weekend/holiday/after-hour, duplicate alerts/closure tests | 36e3b42, 8b4deb7, 45e7ef1 | Configurable multilevel escalation, escalation review UI and all pause cases incomplete |
| Private attachments | Core verified | ticketing/attachments.py; TicketAttachment; private volume | MIME/signature/ownership tests and browser upload/denial | 8ed052c, ee5097a | Antivirus/quarantine/Office/S3 absent |
| In-app notifications/feedback | Core verified | portal/views.py/models.py; AccountPages; detail | Real workflow and duplicate task tests | 96df33f, 328f81f, 45e7ef1 | External adapters/delivery history/event coverage incomplete |
| Staff/manager/admin portals | Core verified | PortalDashboard/AppShell/AdminResource/SystemPages | Staff/manager/admin browser checks | d6f8d58, 01a46b5, ee5097a | Configuration relations use numeric IDs; full dedicated task/policy/user screens incomplete |
| Real metrics/CSV export/settings/health | Basic implemented | portal/analytics.py/operations.py; UI | Live manager metrics/health; scope tests | 01a46b5 | Report filters/percentiles/compliance formulas/async Excel/PDF incomplete |
| Persian RTL/accessibility | Core verified | bnut.css, ui.jsx, Vazirmatn, all new pages | 390px public browser, labels/focus/form tests, ESLint/build | 013b73b, 7cf02ca, 328f81f | Full WCAG/mobile staff/admin/mixed-direction assessment pending |
| Dependency/code quality/CI | Locally verified; hosted status separate | pinned requirements/package-lock, Ruff/ESLint/Prettier, ci.yml | Ruff/npm audit/pip-audit pass; DRF patched | 7b698fa | Hosted run must be observed; full secret/container/security scan pending |
| Production/backup/recovery | Config implemented; externally unverified | prod Compose/TLS configs; backup/restore scripts/docs | Compose config and frontend image/nginx validated | 76557d6, 75514e8 | Full TLS stack, backup/isolated restore drill not executed |
| Proposal/sprints/API/ERD/security docs | Updated | docs; README | Matches milestone, historical contradictions superseded | f492caa, 4a2ee6b, 955ea79 | Full wireframe refresh, all proposed doc filenames/coverage not complete |
| Git integration/push | See final report addendum | Git refs; implementation report | To record after actual push | Current Git history | No force push/history rewrite/destructive reset |

## Exact next implementation tasks

1. Identity release gate: add encrypted MFA enrollment/recovery and administrator step-up verification; password reset with approved delivery adapter; account-specific login locks/activity records; explicit logout-all/admin revocation. Extend accounts/portal identity services and MySQL security tests. Do not use Profile as an unencrypted credential store.
2. Complete React student/employee management and activation issuance screen (currently maintenance user creation and activation API only); XLSX validated preview using shared importer; scheduled privacy-safe import purge after approved retention.
3. Routing: implement stored manual/least-active/round-robin strategies with eligible membership/availability/confidentiality filtering, department locks and unassigned-manager notifications. Currently strategy fields are stored only. Add MySQL concurrency tests and operational UI.
4. Extend the ticket state machine with approved draft/submitted/unassigned/assigned/internal-wait/escalation/rejection/cancellation behavior; implement version preconditions and create idempotency keys; preserve old statuses/data and add backward-compatible migrations.
5. Configure escalation trigger/recipient/level policies, prevent loops and track resolution; add manager escalation/SLA queues. Add response templates, drafts, collaborations, saved filters/tags/bookmarks, safe bulk operations.
6. Content: related/restricted article selectors, feedback deduplication, publication review/scheduling, FAQ popularity, article attachments, sanitized ticket-to-knowledge proposals and privacy-safe search gaps.
7. Reporting: define exact SLA denominators/working-vs-elapsed durations; add date/org filters and larger database aggregates; async report jobs and authorized formula-safe XLSX/PDF; do not invent statistics.
8. Production hardening: antivirus quarantine/storage abstraction, approved policy/retention enforcement, grant approval/emergency access/independent complaint routing, immutable audit archival, request/task correlation and structured logs, resource limits/load measurements, comprehensive automated security/secret/container scans.
9. Complete all remaining required screens and cross-browser/keyboard/RTL/responsive/WCAG validation; update reviewable wireframes from real routes. Test all requested end-to-end scenarios separately.
10. Run isolated backup/restore rehearsal and full TLS production Compose verification with test credentials/certificates; deploy only with explicit server-specific authorization and approved institutional controls.

No further university integration credentials are necessary to continue items 1-9 using synthetic/local adapters. Do not call the whole project complete until every master acceptance criterion has real evidence.

