# API reference — BNUT milestone

Base `/api/v1/`. Legacy `/api/auth/`, `/api/tickets/`, `/api/categories/`, `/api/metrics/` remain compatible aliases for existing clients, with the same security rules. New clients use version one. Swagger: `/api/docs/`; machine schema: `/api/schema/`. Schema validation has zero errors, with remaining enum/operation-name warnings documented in test results. General APIViews use object response schemas; exact rich contracts still require fuller serializers.

Session cookies are same-origin. Obtain `GET auth/csrf/`, pass its `csrfToken` as `X-CSRFToken` on mutations. Send JSON except multipart uploads. Errors use `{error:{status,details}}`; validation 400, denied 403, invisible/missing object 404, competing claim 409, throttled 429. Paginated lists use `{count,next,previous,results}` with page size 20. Public content lists described below use bounded arrays where indicated.

| Method and resource | Request / result | Authorization |
| --- | --- | --- |
| GET auth/csrf/ | csrfToken; sets CSRF cookie | Public |
| POST auth/login/ | username, password, optional portal student/staff/admin; returns user/capabilities | Public, CSRF, throttle |
| GET auth/me/ | Current user and capability names | Session |
| POST auth/logout/ | 204 | Session + CSRF |
| POST auth/activate/ | one-use token, new password; success | Public + CSRF/throttle |
| POST auth/password/ | current_password, password | Current session |
| GET/PATCH profile/ | Academic profile read; notification_preferences boolean map write only | Own |
| GET public/ | University display settings, departments, six articles/FAQs, four live notices | Public |
| GET public/articles/ | q normalized Persian; department/category/page filters | Published/public only |
| GET public/articles/{id}/ | Article content, authorized related articles; increments views | Published/public only |
| GET public/faqs/ | Up to 100 published FAQs | Public |
| GET public/departments/ | Active public directory | Public |
| GET public/departments/{id}/ | Unit contact, active categories/forms, public articles/FAQs | Public |
| GET public/announcements/ or {id}/ | Up to 50 current public announcements or detail | Public |
| GET categories/ | Active public department categories and current dynamic form | Session |
| GET tickets/ | Paginated scoped list; status/priority/category/search/ordering | Owner or scoped staff |
| POST tickets/ | title, description, category, form_responses; priority ignored in favor of category policy | Student |
| GET tickets/{id}/ | Conversation, public history, snapshot, deadlines, allowed actions; staff notes only with permission | Object visibility |
| POST tickets/{id}/reply/ | body | Visible object + ticket.reply |
| POST tickets/{id}/claim/ | No fields; current open-ticket claim | ticket.assign |
| POST tickets/{id}/release/ | reason | Assignee or authorized manager + assign |
| POST tickets/{id}/status/ | status, reason where required | Transition-specific permission |
| POST tickets/{id}/close/ | reason for staff; student confirms resolved issue | Eligible state |
| POST tickets/{id}/reopen/ | reason | Policy-limited student or authorized staff |
| POST tickets/{id}/note/ | body; 201 | ticket.add_internal_note |
| POST tickets/{id}/transfer/ | target department/category, reason; confirmation only | ticket.transfer |
| POST tickets/{id}/feedback/ | overall/speed/quality 1..5, solved, optional comment | Owner resolved/closed; once |
| POST tickets/{id}/attachments/ | Multipart file; 10 MiB limit | Visible active ticket + reply |
| GET tickets/{id}/attachments/{attachment_id}/ | Private attachment download | Current visibility |
| GET notifications/ | unread count and latest 100 currently accessible notifications | Own |
| POST notifications/ | id marks one read; empty body marks all read | Own |
| GET dashboard/ | Role-sensitive real counts, queues and authorized performance | Session |
| GET metrics/ | Scoped legacy status counts | Session |
| GET reports/tickets.csv | Up to 5000 authorized rows, formula-safe, no message bodies | ticket.export in scope |
| GET manage/permissions/ | Granular permission catalog | role.manage |
| GET manage/audit/ | Paginated sanitized audit list | audit.view globally |
| GET/PATCH manage/settings/ | Validated branding/contact/closure policy settings | settings.manage globally |
| GET manage/health/ | Boolean MySQL/Redis/worker heartbeat health | settings.manage globally |
| POST manage/users/{id}/activation/ | Raw token once for authorized out-of-band distribution; 24h validity | student.manage or employee.manage |
| GET/POST manage/student-imports/ | Own import history or multipart CSV preview; row errors; first 20 preview rows | student.manage globally |
| POST manage/student-imports/{id}/commit/ | Atomic/idempotent commit of own valid preview | student.manage globally |
| GET health/live/ | Process liveness | Public |
| GET health/ready/ | DB and Redis readiness; 503 if unavailable | Public |

Managed resources support GET list/detail, POST create, PUT/PATCH update and GET `form-metadata/` for validated field metadata. No DELETE is exposed: archive/deactivate records. Resource permissions: departments/categories/forms (`department.manage`); memberships (`employee.manage`); roles/role-assignments (`role.manage` globally); calendars/holidays/sla-policies (`settings.manage` globally); articles/faqs/announcements (`knowledge_base.publish`). Scoped actors can update existing department records but creating a department requires a global grant. Role mutations and changes are audited. RequestForm updates increment its version; old ticket snapshots remain intact. Article updates create a revision.

Example ticket: `{"title":"مشکل اتصال","description":"زمان و شرح رخداد","category":1,"form_responses":{"service":"اینترنت"}}`. No owner/department/assignee/status/deadline inputs are accepted by the create serializer. No secrets or national IDs belong in ticket forms.
