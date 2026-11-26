# University Support Desk — Sprint 1 proposal

**Document status:** implementation-aligned proposal, updated November 26, 2026 (Asia/Tehran). This proposal uses [the version-one scope](../requirements/scope.md). The university name, group roster, and student IDs were not supplied and remain explicit placeholders.

## 1. Project Information (مشخصات پروژه)

- **Project title:** University Support Desk — Student Ticketing System
- **University:** `[University name — to be supplied]`
- **Group members:** `[Names and student IDs — to be supplied]`
- **Repository:** https://github.com/abolfazlhadinezhad/softwareEngineeringProject
- **Branch policy:** `main` is integrated; feature branches are pushed and merged after checks.

## 2. Project Overview (معرفی و توضیح کلی پروژه)

University students need a dependable way to ask for help from support staff and follow what happens after they submit a request. University Support Desk keeps each student's requests and replies in one private workspace. Students sign in with an administrator-provisioned account, submit a categorized request with a priority, read the conversation, and close or reopen their own ticket. Support staff use a shared queue to search, filter, claim, reply to, and move requests through a small lifecycle. An administrator manages accounts and categories through a protected administration console.

The first release focuses on a clear request-to-resolution workflow. It deliberately excludes university SSO, public registration, email/SMS delivery, attachments, rich text, and multi-university tenancy until those integrations and policies are specified. The application is a Dockerized modular monolith with Django/DRF, React JavaScript, and MySQL 8.0.

## 3. Problem Statement (بیان مسئله)

When student support requests are spread across informal messages or disconnected channels, the student may not know whether the request was received, who owns it, or what information is still needed. Support staff also lack a shared, searchable queue and a consistent status history. This creates avoidable follow-up, duplicated work, and weak accountability for closure.

The proposed system gives every request an owner, category, priority, status, conversation, and activity history. Students see only their own records; support staff see the shared queue. Server-side authorization and MySQL transactions protect privacy and prevent competing claims from overwriting each other.

## 4. Project Objectives (اهداف پروژه)

**Main objective:** provide a secure, usable workflow for students to submit and follow university support requests.

Supporting objectives:

1. Reduce uncertainty by showing status, assignee, timestamps, and replies in one ticket detail view.
2. Give support staff a searchable, filterable queue and safe claim/release operations.
3. Protect student privacy through session authentication, role-based access, and object-level visibility checks.
4. Preserve an auditable status, assignment, creation, and reply event history.
5. Deliver a reproducible Docker environment, API documentation, tests, and maintainable source structure.

## 5. Target Users (کاربران هدف)

| User | Needs and allowed actions |
| --- | --- |
| Student | Sign in; submit a title, description, active category, and priority; list/read/reply to own tickets; close or reopen own tickets. Cannot see another student's records or staff-only transitions. |
| University support staff | Read the shared queue; search/filter; claim/release tickets; reply; change status; close and reopen tickets. Cannot manage accounts/categories or enter Django admin. |
| Administrator | All support actions plus provision/disable accounts, assign roles, and manage active categories in the protected Django admin console. |

## 6. Key Features (قابلیت‌های اصلی نرم‌افزار)

| Feature | Version-one behavior |
| --- | --- |
| Session sign-in | Administrator-provisioned accounts; CSRF-protected login/logout; secure password hashing. |
| Private student workspace | Student queue/detail queries are scoped to the authenticated creator. |
| Ticket submission | Required bounded title/description, active category, and low/normal/high priority; initial status `open`. |
| Shared support queue | Support/admin can search title/description, filter status/priority/category, paginate, and order by recent update. |
| Conversation | Plain-text chronological replies, with closed-ticket guard. |
| Assignment | Support claims an unassigned request; competing claims return a conflict. Assignee or administrator can release. |
| Lifecycle | `open`, `in_progress`, `waiting_student`, `resolved`, and `closed`; student close/reopen and staff status controls follow documented rules. |
| Activity history | Creation, reply, claim/release, status, close, and reopen events are visible on ticket detail. |
| Administration | Django admin manages users and categories; referenced categories are deactivated rather than deleted. |
| Responsive interface | Accessible labels, keyboard focus, loading/error/empty states, and mobile layout. |

## 7. Similar Systems (بررسی نمونه‌های مشابه)

The comparisons establish design context; they are not copied specifications.

| System | Relevant strengths | Limitations for this project / differentiation |
| --- | --- | --- |
| [Jira Service Management](https://www.atlassian.com/software/jira/service-management/features) | Request management, queues, routing, self-service, knowledge and broad ITSM workflows. | Enterprise scope and integrations are larger than this course prototype. University Support Desk keeps only the private student request, staff queue, assignment, reply, and status slice; it has no SLA/AI/asset platform. |
| [Zendesk ticketing](https://www.zendesk.com/service/ticketing-system/) | Unified interactions, agent workspace, assignment/routing, workflow automation, and many channels. | Commercial omnichannel automation is outside version one. University Support Desk uses one university deployment, administrator-provisioned accounts, explicit role boundaries, and a small auditable lifecycle. |

These systems motivated a queue, assignment, status, and conversation model. We did not claim institution-specific features from either vendor and will validate actual university needs with course stakeholders.

## 8. Proposed Solution and Execution (راهکار پیشنهادی و نحوه اجرا)

Use a modular monolith: React/Vite serves the responsive browser UI; Django REST Framework exposes session-protected JSON endpoints; services enforce ticket state transitions and use Django ORM transactions; MySQL 8.0 stores relational data; Docker Compose runs frontend, backend, migration, and database services. drf-spectacular provides OpenAPI/Swagger UI. See [architecture](../architecture/architecture.md), [database design](../database/schema.md), and [API documentation](../api/api.md).

Development follows a vertical slice: student login -> create ticket form -> DRF validation -> ticket service -> MySQL -> response -> queue/detail refresh. Tests run in the same Docker/MySQL environment. Redis is not introduced because version-one reads are small and privacy-scoped; the caching decision and invalidation behavior are documented in architecture.

## 9. Scope & Limitations (محدوده و محدودیت‌ها)

**Included:** account sign-in, role permissions, category selection, private student tickets, support queue, replies, assignment, statuses, event history, dashboard counts, pagination/filtering/search, admin console, Dockerized MySQL, OpenAPI, responsive UI, automated tests, and local design artifacts.

**Excluded:** university SSO, public registration, email/SMS/push notifications, attachments, rich text, internal/private staff notes, SLA escalation, payments, real-time sockets, AI, knowledge base, multi-university tenancy, and production deployment.

**Known limitations:** university identity rules, branding, team metadata, roster, and final course dates are unavailable. The first version assumes one university deployment and administrator-provisioned accounts. It is a course prototype, so production operations still require TLS termination, backups, monitoring, secret management, load testing, and a confirmed institutional privacy policy.

## 10. Initial Project Plan (برنامه اولیه انجام پروژه)

| Stage | Activities | Evidence |
| --- | --- | --- |
| Requirements | Read both supplied PDFs, identify concept, record scope and traceability | `docs/requirements/` |
| Foundation | Docker, MySQL health/migration gate, Django/DRF, React/Vite, env handling | Compose checks, commits |
| Vertical slice | Auth, student create/list/detail workflow, MySQL persistence | `apps/accounts`, `apps/ticketing`, UI pages, tests |
| Collaboration | Replies, assignment, status transitions, events, metrics, admin | Service tests/API docs |
| Quality | API schema, frontend tests/build, MySQL test suite, browser smoke checks, CI | `.github/workflows/ci.yml`, reports |
| Documentation | Proposal, architecture, ERD, UI artifact, README, sprint report | `docs/` and README |

Team assignments are `[to be supplied]`; commit history identifies actual implementation evidence and does not invent contributors.

## 11. Conclusion (نتیجه‌گیری)

University Support Desk addresses a concrete coordination problem: students need a visible path from request to response, while support staff need a shared queue and safe ownership. The first release keeps the workflow small enough to test but meaningful enough to demonstrate secure authentication, role-aware access, a real MySQL-backed vertical slice, and maintainable software engineering practices.

## 12. References (منابع و مراجع)

1. NIT 4051, *Sprint 1 Software Engineering Project Documentation*, supplied PDF, six pages, repository root, reviewed November 26, 2026.
2. NIT 4051, *Sprint 2 Software Engineering Project Documentation*, supplied PDF, twelve pages, repository root, reviewed November 26, 2026.
3. Atlassian, [Jira Service Management Features](https://www.atlassian.com/software/jira/service-management/features), accessed November 26, 2026.
4. Zendesk, [AI-powered ticketing system](https://www.zendesk.com/service/ticketing-system/), accessed November 26, 2026.
5. Django, [Database documentation](https://docs.djangoproject.com/en/5.2/ref/databases/), accessed November 26, 2026.
6. Docker, [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/), accessed November 26, 2026.

## 13. Deadline (ددلاین)

Sprint 1 source page 6 describes a one-week submission window ending at **9 Aban (۹ آبان)**, but it does not state a calendar year. The applicable course year/deadline is `[to be supplied]`; this document does not invent a Gregorian conversion or claim that a submission occurred by that date.
