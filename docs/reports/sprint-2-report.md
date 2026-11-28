# Sprint 2 report — BNUT milestone

Updated 2026-11-28. Both PDFs read completely. Current evidence supersedes the earlier minimal prototype report; historical commits remain intact.

| Required deliverable | Evidence | Verification |
| --- | --- | --- |
| Technology stack and rationale | pinned requirements/package lock; architecture/system-architecture.md | Docker builds, required MySQL/Python/Django/React JS stack |
| Architecture diagram | system-architecture.md Mermaid | Matches dev/prod Compose responsibilities |
| UI/UX | ui-ux/design-system.md, original wireframes.html, actual React routes | Persian RTL/browser/mobile checks; full WCAG review pending |
| Project structure | accounts/ticketing/portal; feature-based React | Existing components preserved; domain services separated |
| Database design | database/erd.md, migrations | MySQL 8.0 migration/check/tests; additive UUID backfill |
| API documentation | api/api-reference.md and /api/docs/ | Schema zero errors, four naming warnings |
| Caching strategy | architecture cache section | Public 60s cache/fallback/invalidation; private query isolation |
| Source code | backend/frontend/runtime configuration | Real forms/endpoints, no fake dashboard statistics |
| Working prototype | public/student/staff/manager/admin vertical slices | Four Chromium workflows through real services |
| Automated tests | backend/API/security/SLA/form/import; React unit; E2E | 32 MySQL + 8 frontend + 4 browser passed |
| README and report | README, implementation-2026-11-28.md, backlog | Run/deploy/test/status/limitations recorded |

No actual team roster/contribution allocation or course submission claim is fabricated. All requested production features are not complete. Git integration/push and hosted CI observations are recorded in the implementation report after execution. Deployment credentials/university policies remain external dependencies. Local successful checks do not imply a successful hosted CI run.

