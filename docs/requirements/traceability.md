# Requirement traceability matrix

Sources: [complete PDF review](source-review.md); the user's master request and subsequent answers. Status at November 26, 2026: concept, audience, and handling roles confirmed; remaining version-one decisions delegated and explicitly recorded in [scope](scope.md). Implementation evidence will be added as tasks complete. Earlier `Blocked` entries below describe the initial discovery gap; workflow/role gaps are now resolved by the recorded scope; unavailable real-world metadata remains blocked.

**Status meanings:** `Captured` means analyzed, not delivered. `Pending` means not implemented. `Blocked` means essential project information is missing. `Verified` requires actual file/runtime/test evidence. Future locations below are explicitly planned and are not links to nonexistent deliverables.

## Sprint 1 proposal

| ID | Requirement | Source | Planned evidence | Status |
| --- | --- | --- | --- | --- |
| S1-01 | Project title, actual members, repository | S1 p2, section 1 | `docs/proposal/project-proposal.md`, section 1 | Blocked: title/roster |
| S1-02 | Explain application purpose and user activities | S1 p2-3, section 2 | Proposal section 2 | Blocked: workflow |
| S1-03 | Existing problem, impact, current solution limitations | S1 p3, section 3 | Proposal section 3 | Blocked: specific university problem |
| S1-04 | Main objective and realistic supporting goals | S1 p3, section 4 | Proposal section 4 | Blocked: acceptance criteria |
| S1-05 | Actual user groups and needs | S1 p3-4, section 5 | Proposal section 5 and permissions matrix | Blocked: handling roles |
| S1-06 | Main features, explanations, core/optional distinction | S1 p4, section 6 | Proposal section 6, workflow acceptance criteria | Blocked: feature scope |
| S1-07 | At least two real similar systems; compare features, strengths, weaknesses, differentiation | S1 p4-5, section 7 | Proposal section 7 with consulted sources | Pending |
| S1-08 | Platform, implementation approach, technology rationale | S1 p5, section 8 | Proposal section 8, architecture document | Pending |
| S1-09 | Explicit inclusions, exclusions, real limitations | S1 p5, section 9 | Proposal section 9 | Blocked: scope |
| S1-10 | Phases and known team responsibilities | S1 p6, section 10 | Proposal section 10 and task tracker | Pending; people not supplied |
| S1-11 | One/two paragraphs summarizing problem, solution, value | S1 p6, section 11 | Proposal section 11 | Blocked: goals |
| S1-12 | Sources actually used; internet title/link, access date recommended | S1 p6, section 12 | Proposal section 12 | Pending |
| S1-13 | Deadline: one week, 9 Aban; year unspecified | S1 p6, section 13 | Proposal section 13; confirm applicable dates | Captured; year/current deadline unknown |

## Sprint 2 deliverables and cross-cutting requirements

| ID | Requirement | Source | Planned evidence / verification | Status |
| --- | --- | --- | --- | --- |
| S2-01 | Chosen stack with justification | S2 p1-3, p11 | Architecture technology decisions | Pending |
| S2-02 | Architecture explanation, boundaries, responsibilities, rationale | S2 p3-5 | Architecture document | Pending |
| S2-03 | Architecture diagram and communication | S2 p5, p11 | Mermaid component/deployment diagram matching code | Pending |
| S2-04 | Main-screen design, flows, wireframes, reviewable local file or real design link | S2 p5-6, p11-12 | `docs/ui-ux/` and README reference | Blocked: workflows |
| S2-05 | Design system, responsive/accessibility support, loading/error/empty states | S2 p5-6 | Design tokens, components, interaction/browser checks | Pending |
| S2-06 | Meaningful frontend/backend/docs structure and domain modules | S2 p6-7, p11 | Source tree and responsibility documentation | Pending |
| S2-07 | Clean code, SoC, SOLID, DRY, KISS, YAGNI; justified patterns | S2 p8 | Small feature modules and review | Pending |
| S2-08 | Entities, relationships, PK/FK, indexes, ERD, initial schema/migrations | S2 p2, p8, p11 | `docs/database/`, ORM models/migrations checked against MySQL | Blocked: business rules |
| S2-09 | Main endpoints, methods, requests, responses, status/access rules | S2 p8-9, p11 | `docs/api/`, generated OpenAPI, contract tests | Blocked: workflows/roles |
| S2-10 | Caching need, candidate data, TTL, hit/miss, invalidation and staleness; Redis optional | S2 p2-3, p11 | Architecture caching decision and applicable tests | Blocked: data/read patterns |
| S2-11 | Organized real frontend and backend source | S2 p11 | `frontend/`, `backend/`, builds and startup | Pending |
| S2-12 | Real integrated working prototype / vertical slice | S2 p1, p10-11 | Ticket workflow through UI -> API -> MySQL -> UI, executed end-to-end test | Blocked: core workflow |
| S2-13 | At least one automated test for a real core feature | S2 p9, p11 | Executed domain tests; infrastructure tests alone do not satisfy this | Blocked: core workflow |
| S2-14 | README setup/run instructions and design reference | S2 p11-12 | README verified from clean container setup | Pending |
| S2-15 | Sprint report, tasks, actual division of work, verifiable contributions | S2 p10-11 | `docs/reports/`, task tracker, real Git history | Pending |
| S2-16 | Authentication/authorization, validation, secure passwords, sessions/tokens, env secrets | S2 p9 | Backend permissions, security settings, denied-access/validation tests | Pending; role/account rules blocked |
| S2-17 | Git/shared repository, small traceable tasks, branch integration | S2 p3, p10 | Commit/merge/push history; task statuses and real owners | Captured; original repository inspected |
| S2-18 | All deliverables stored in repository | S2 p12 | Tracked files and README document index | Pending |

The p11 table has eleven deliverable rows; this matrix separates architecture explanation from its diagram and tracks the additional security, design, and teamwork criteria in the surrounding pages.

## Additional explicit user constraints

| ID | Required outcome | Planned verification | Status |
| --- | --- | --- | --- |
| U-01 | Django + DRF, React JavaScript + Vite, MySQL 8.0; no SQLite substitution | Dependencies, settings, source, live DB version | Pending |
| U-02 | Modular monolith; business services separate from HTTP/serializers/ORM responsibilities | Architecture and implemented feature review | Pending |
| U-03 | All services via `docker compose up --build`; no host application runtimes | Dockerfiles, Compose build/up, logs | Pending |
| U-04 | Frontend/backend/MySQL services; only justified extras | Compose config and service health | Pending |
| U-05 | Wait for healthy DB, reliable migrations, health checks, dependencies/networking | Clean startup, migration checks, readiness checks | Pending |
| U-06 | Environment configuration, `.env.example`, ignored real env/secrets, Docker ignores | Git ignore checks and tracked-file review | Pending |
| U-07 | Persistent MySQL volume, safe rebuild, no destructive volume removal | Persistence check before/after recreation | Pending |
| U-08 | Hot reload and correct frontend/API routing | Bind mounts, Vite proxy and API integration checks | Pending |
| U-09 | ORM schema migrations, constraints, indexes, referential integrity; no duplicate business logic/N+1 | MySQL-backed tests, migration drift checks, query review | Blocked: schema |
| U-10 | Central consistent errors, HTTP status codes, validation, pagination/filtering where applicable | API contract/security/validation tests | Pending |
| U-11 | Authentication, RBAC where roles exist, object access checks, password hashing | Session/auth/permission tests using MySQL | Blocked: roles/accounts |
| U-12 | CSRF/CORS, safe errors, env secrets, secure production settings | Security tests and production config checks | Pending |
| U-13 | Reusable UI, routes, centralized API, forms, state, responsive/accessibility support | Component/form/API/browser tests and build | Pending |
| U-14 | Browser-accessible generated OpenAPI documentation | drf-spectacular schema validation and HTTP checks | Pending |
| U-15 | ERD and API/UI docs match actual source; no fake Figma artifact | Cross-check schema/contracts/screens, README links | Pending |
| U-16 | First actual ticket vertical slice before remaining feature expansion | Executed workflow test, stored acceptance criteria | Blocked: workflow |
| U-17 | Backend models/services/API/auth/validation tests and frontend component/form/integration/workflow tests | Executed test results, no unrun pass claims | Pending |
| U-18 | CI practical, with actual MySQL 8.0 | Workflow and successful run evidence | Pending |
| U-19 | Complete README: purpose, features, stack, architecture, tree, prerequisites, env, Docker, migrations/tests, API URL, database, docs/design, team placeholders | Walk through commands and all 18 requested README topics | Pending |
| U-20 | Small Conventional Commits; updated-main feature branches; push, merge, push main, verify | Git commands and remote refs at each milestone | Pending |
| U-21 | No history rewriting, force push, overwritten user work, unrelated deletion, secret commits, failing-code merge | Status/diff/test review before commits/merges | Captured; workspace initially clean |
| U-22 | Milestone reports include branch, files, commits/hashes, executed checks, merge and push status | `docs/reports/` and user progress reports | Pending |
| U-23 | Actual domain only; no fabricated business rules, people, references, tests, features, or completed deliverables | Confirmed facts and open questions; evidence review | Captured; clarification requested |

## Functional requirements gate

The user confirmed the concept, audience, and roles and delegated the remaining implementation choices. [Scope](scope.md) records FR-01 through FR-12, role permissions, rules, exclusions, and the selected first vertical slice. Each will be mapped to actual implementation and executed tests. See [clarification record](open-questions.md).
