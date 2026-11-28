# Assignment source review

Reviewed: November 26, 2026 (Asia/Tehran). All 18 PDF pages were read as extracted text and inspected as rendered images, including tables and the example directory tree. Page numbers below refer to the source PDFs.

## Source register

| ID | File at repository root | Pages | SHA-256 |
| --- | --- | --- | --- |
| S1 | `__اسپرینت_اول_پروژه_مهندسی_نرم_افزار_4051_.pdf` | 6 | `89720bc60f1a226f261e9a30f8a0ee5a3cce94ecc4f6195252328a4422e68803` |
| S2 | `__مستندات_اسپرینت_دوم_پروژه_مهندسی_نرم_افزار_.pdf` | 12 | `6474d38ae49c29243c028b85d2f2dcf001d28b8cf829a22cac799a41e29a2fbd` |

These are university assignment guidelines, not an approved application specification. The 2026-11-28 master request supplies BNUT identity and a much broader platform scope. Both source PDFs were independently re-extracted and read completely in this session; the page findings below remain valid. Team metadata and the applicable course deadline remain unavailable. Current implementation scope is tracked in [traceability-matrix.md](traceability-matrix.md).

## Sprint 1: page-by-page findings

| Page | Required content and interpretation |
| --- | --- |
| 1 | Each group selects its own idea and prepares a proposal explaining what, why, users, features, and approach. Code, a full database design, and UML are not required for Sprint 1. |
| 2 | Proposal supports idea approval. Project Information must identify a descriptive title, all group members, and repository. Project Overview must explain purpose, domain, and user activities. Clinic appointment management is explicitly an example. |
| 3 | Problem Statement explains the existing problem, consequences, and shortcomings of current solutions. Objectives need a main goal and realistic supporting goals. Target Users must identify groups and needs. |
| 4 | Example role/need table: patient, doctor, receptionist, administrator. Example feature table: registration/login, doctor listing, appointment reservation/cancellation, management panel. These do not define this application's roles or features. Separate core and optional scope. Similar Systems requires at least two actual comparable systems. |
| 5 | Similar Systems must compare capabilities, strengths, weaknesses, and differentiation/inspiration. Online-store comparison is another example. Proposed Solution describes platform, approach, technologies, and reasons. React/Django/PostgreSQL are illustrative choices. Scope & Limitations identifies inclusions, exclusions, and real constraints. |
| 6 | Initial Project Plan needs stages and may include known responsibilities; the four-sprint table is illustrative. Conclusion summarizes value without introducing new scope. References must identify sources actually consulted (title/link; access date recommended). Deadline is stated as one week, until **9 Aban (۹ آبان)**, without an explicit calendar year. Confirm the applicable course deadline; do not assign a Gregorian date or treat it as a new future deadline. |

### Exact proposal section sequence

Use these headings when drafting the actual proposal after the business scope is established:

1. مشخصات پروژه (Project Information)
2. معرفی و توضیح کلی پروژه (Project Overview)
3. بیان مسئله (Problem Statement)
4. اهداف پروژه (Project Objectives)
5. کاربران هدف (Target Users)
6. قابلیت‌های اصلی نرم‌افزار (Key Features)
7. بررسی نمونه‌های مشابه (Similar Systems)
8. راهکار پیشنهادی و نحوه اجرای پروژه (Proposed Solution)
9. محدوده و محدودیت‌های پروژه (Scope & Limitations)
10. برنامه اولیه انجام پروژه (Initial Project Plan)
11. نتیجه‌گیری (Conclusion)
12. منابع و مراجع (References)
13. ددلاین (Deadline)

## Sprint 2: page-by-page findings

| Page | Required content and interpretation |
| --- | --- |
| 1 | Architecture and initial development; at least one real executable feature, not necessarily all features. Justify frontend/backend/database/tool choices. Frontend concerns include reusable components, routing, forms, API communication, and state. |
| 2 | Distinguish client state from server state. Explain caching/refetch/invalidation if used. Backend covers REST, authentication, authorization, validation, dependency management, and errors; separate business logic from controllers. Database covers relationships, keys, indexes, migrations, and ORM. |
| 3 | Caching analysis must address selected data, TTL, hit/miss, cache-aside, invalidation, and updates if a cache is used. Redis is optional; the strategy explanation is required. Git and a shared repository are mandatory. Design the architecture before main development. |
| 4 | Explain responsibility and dependency boundaries. Full Clean Architecture, microservices, event-driven architecture, message brokers, and `TicketCreated` are explanatory options, not required infrastructure or application features. |
| 5 | Supply an architecture diagram with component responsibilities, communication, and rationale. Define user flows and wireframes before implementing main screens. Figma or comparable reviewable artifacts are acceptable. Establish an initial design system. |
| 6 | Responsive design, accessibility, reusable components, and loading/error/empty states. Initial designs of main screens and a reviewable design link/file are required; a clickable prototype is recommended. Organize code by responsibilities/features. |
| 7 | Example frontend/backend/docs tree includes `auth`, `users`, and `tickets`; the PDF explicitly calls this a suggestion. Adapt structure to the framework and actual requirements. Do not create needless directories or layers. |
| 8 | Apply separation of concerns, SOLID, DRY, KISS, YAGNI, and patterns only for real problems. Define entities, relationships, keys, ERD, initial schema, and API methods/inputs/outputs/status/access rules before core implementation. |
| 9 | OpenAPI/Swagger or Postman recommended; consistent API contracts. Security includes authentication, authorization, input validation, secure passwords, sessions/tokens, secrets via environment variables, and access prevention. At least one automated test for a real core feature is required. Linting/formatting/CI are recommended. |
| 10 | Divide work into small traceable tasks with outputs, statuses, and actual owners when known. Use a task tracker and proper Git; feature branches and PR/MR integration are recommended. Contributions must be verifiable, never fabricated. The eight-stage roadmap is a recommendation. |
| 11 | Prefer a first complete vertical slice: frontend -> API -> business logic -> database -> response. Mandatory deliverable table lists eleven rows: stack, architecture diagram, UI/UX, structure, database design, API docs, caching strategy, source, working prototype, automated testing, README/report. Architecture explanation is also explicitly required by pages 3-5. |
| 12 | Keep documents in the repository; include actual design reference and setup/run instructions in README. Redis, Docker, and CI/CD are optional in the PDF, but Docker is mandatory under the user's request. Concludes with maintainability, user-centered design, and avoiding unnecessary complexity. No Sprint 2 submission date is stated. |

## Source precedence and decisions

- The user's required stack is Python/Django/DRF, React **JavaScript**, MySQL **8.0**, Docker/Compose, and Git/GitHub. Do not substitute PostgreSQL, SQLite, TypeScript, or another framework from the examples.
- Prefer a modular monolith; define domain modules only after confirming responsibilities and workflows.
- Docker is mandatory, even though optional in S2. All application dependencies and tests run in containers; PDF inspection tools are document-analysis utilities, not application runtime dependencies.
- Redis is mandatory in the current master request; see the implemented bounded public cache/task strategy in architecture.
- BNUT identity is supplied. Team roster, student IDs, deadlines, official departments/integrations and institutional approvals must not be invented.
- A health endpoint or infrastructure status page cannot satisfy the real core-feature requirement.

See [traceability](traceability.md) and [open questions](open-questions.md).
