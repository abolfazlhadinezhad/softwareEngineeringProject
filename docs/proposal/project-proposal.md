# BNUT — Sprint 1 project proposal

Updated 2026-11-28. This proposal supersedes the earlier generic prototype scope. It distinguishes the complete intended platform from the implemented development milestone.

## 1. مشخصات پروژه (Project Information)

Title: سامانه جامع پاسخگویی و پشتیبانی دانشجویان دانشگاه صنعتی نوشیروانی بابل.
University: Babol Noshirvani University of Technology (BNUT).
Repository: https://github.com/abolfazlhadinezhad/softwareEngineeringProject.
Actual group names/student IDs/responsibilities: not supplied; no team roster is invented.

## 2. معرفی و توضیح کلی پروژه (Project Overview)

A Persian-first web platform helps students find public answers, submit private university requests and follow accountable departmental handling. Staff respond within authorized organizational scope; managers monitor their departments; administrators configure services and monitor actual operational data. The current milestone connects public help, student tickets, private communication, scoped staff workflows and React configuration to MySQL.

## 3. بیان مسئله (Problem Statement)

Dispersed support channels can leave students uncertain about receipt, ownership and resolution. Unclear routing and repetitive questions can increase follow-up and hide overdue work. These are design motivations to validate with university stakeholders, not claims from an invented institutional survey. Centralized help, visible ownership, privacy controls and recorded deadlines provide a testable proposed response.

## 4. اهداف پروژه (Project Objectives)

Main objective: provide a secure, maintainable path from student question to accountable resolution. Supporting objectives: answer-first self-service; configurable organizational routing; private auditable conversations; prevention of forgotten requests; measurable response/resolution times; accessible Persian interfaces; production-oriented operational controls. Full production acceptance remains future work.

## 5. کاربران هدف (Target Users)

| Group | Need |
| --- | --- |
| Guest | Read public help/directory/announcements without an account |
| Student | Activate university-issued account; submit/follow own requests; feedback |
| Agent/specialist | Act on permitted queues/assignments; respond and record internal work |
| Department manager | Manage permitted workload and inspect performance |
| Supervisor/report viewer | Authorized aggregates without routine sensitive-content access |
| Content editor | Prepare/review/publish public or restricted help |
| System/super administrator | Configure identities, units, permissions and operational policy |

The current account types are student/support/admin with configurable permission roles/scopes; every suggested role preset is not yet implemented.

## 6. قابلیت‌های اصلی نرم‌افزار (Key Features)

Implemented core: public Persian help search/FAQ/notices/directory; student wizard/dynamic forms and snapshots; owned ticket list/conversation/private files; manual claim/release/transfer/internal notes; guarded five-state lifecycle; confirmation/reopening/feedback; role-aware real metrics; React resource configuration; CSV preview/atomic import and one-use activation; in-app notifications; working-hour SLA deadlines, scheduled warnings/breaches/closure.

Remaining required scope includes complete identity MFA/reset/session controls, automated routing, broader lifecycle/collaboration, fully configurable escalation, all user-management screens, advanced reports/async exports, Excel import and comprehensive production validation. See living backlog; required master features are not silently reclassified as optional.

## 7. بررسی نمونه‌های مشابه (Similar Systems)

| System | Observed relevant capabilities | Design assessment for BNUT |
| --- | --- | --- |
| [Jira Service Management](https://www.atlassian.com/software/jira/service-management/features) | Request and knowledge management; broader IT service workflows | Its breadth offers useful patterns; institution-specific identity/privacy and Persian student flows still require deliberate local design. This is an assessment, not a claim that Jira cannot be configured for universities. |
| [Zendesk ticketing](https://www.zendesk.com/service/ticketing-system/) | Unified support channels, agent workspace, routing and reporting | Useful conversation/queue patterns; BNUT currently focuses on a single university web channel and explicit organizational privacy. No claim of equivalent feature completeness is made. |

Official vendor pages consulted 2026-11-28; comparison uses their described features, not invented benchmarks or research results.

## 8. راهکار پیشنهادی و نحوه اجرا (Proposed Solution)

Modular monolith with Django/DRF/ORM/MySQL 8.0, React JavaScript/Vite/Router/TanStack Query, Docker/Compose, Redis, Celery/Beat, Nginx/Gunicorn and OpenAPI. Relational constraints and transactions fit organizational ownership/history; React supports reusable Persian interfaces; Redis has bounded public cache/task/throttle roles; Celery performs scheduled monitoring. All application runtimes/tests run in containers. See current architecture and stack pins for exact implementation.

## 9. محدوده و محدودیت‌های پروژه (Scope & Limitations)

Target scope is the supplied master platform for one university. The delivered milestone is partial and locally tested, not an institutionally deployed system. No public self-registration, national-ID default credentials, real student records, unofficial university APIs, unapproved external delivery or official branding are introduced. Missing institutional decisions, real integration details, team metadata and production environment constrain final rollout. Model drafts alone are not functional deliverables.

## 10. برنامه اولیه انجام پروژه (Initial Project Plan)

Audit/preserve existing code -> infrastructure/identity/scope -> configurable organizations -> tested ticket vertical slice -> public/student/staff/admin interfaces -> SLA/reporting -> hardening -> final testing/documentation/integration. Current work spans the core of these phases; precise incomplete tasks/files/checks/commit evidence are in `docs/backlog.md`. Actual people assignments remain to be supplied; Git records genuine work.

## 11. نتیجه‌گیری (Conclusion)

BNUT support aims to make guidance and request handling clearer while protecting private student communication. The implemented milestone provides a real tested foundation and an explicit path to the remaining institutional and production requirements.

## 12. منابع و مراجع (References)

Supplied root Sprint 1 PDF (6 pages) and Sprint 2 PDF (12 pages), fully read 2026-11-28; source hashes/page findings in requirements/source-review.md.
[Jira Service Management features](https://www.atlassian.com/software/jira/service-management/features), [Zendesk ticketing](https://www.zendesk.com/service/ticketing-system/), [Django cache documentation](https://docs.djangoproject.com/en/5.2/topics/cache/), [Celery Django integration](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html), [DRF release notes](https://www.django-rest-framework.org/community/release-notes/), consulted 2026-11-28.

## 13. ددلاین (Deadline)

Sprint 1 page 6 specifies a one-week window ending 9 Aban without a calendar year. The applicable course deadline is not supplied. No Gregorian conversion or claim of timely submission is invented.

