# Version-one scope and acceptance criteria

Recorded November 26, 2026. The user confirmed a university student ticketing system, **university support staff and administrator** as handling roles, and delegated remaining version-one decisions with “do as much as you can.” The following are explicit implementation choices under that direction, not facts extracted from the assignment examples. They can be revised after review.

## Roles and boundaries

- **Student:** sign in, create a ticket, list/read their own tickets and replies, reply to an active ticket, close or reopen their own ticket.
- **Support:** read the shared university queue, claim/release tickets, reply, and update ticket status. Support cannot administer accounts or categories.
- **Administrator:** all support actions plus account/category administration through Django's administrator console.
- Accounts are provisioned by an administrator. There is no public registration or asserted university SSO integration. Staff and administrators cannot be created by public API input.
- This is one university deployment, with no tenant or university membership inference. No student may read another student's tickets, counts, or messages.

## Functional acceptance criteria

| ID | Workflow and acceptance criteria |
| --- | --- |
| FR-01 | A provisioned active account can sign in/out using a session. Invalid credentials return a safe error. Unauthenticated API access is denied except CSRF bootstrap, health, and documentation. Passwords use Django hashing. |
| FR-02 | An administrator creates/updates users and assigns exactly one role; only an administrator can enter the admin console. Accounts can be disabled. |
| FR-03 | An administrator manages named categories with an active flag. Ticket creation offers active categories only; existing tickets retain inactive category history. Referenced categories cannot be deleted. |
| FR-04 | A student submits a ticket with a required trimmed title (maximum 160), description (maximum 10,000), active category, and low/normal/high priority. The server sets creator, status `open`, timestamps, and empty assignee. Persist it in MySQL and show it in the student's list/detail after creation. |
| FR-05 | Students list only their tickets; support/admin list all tickets. Search title/description, filter status/priority/category, paginate, and order by recent update. Return no other student's ticket existence through direct ID access. |
| FR-06 | Ticket detail displays category, priority, status, creator, assignee, timestamps, and chronological public replies. There are no internal/private staff notes in this version. |
| FR-07 | The creator or support/admin posts a nonblank reply (maximum 10,000) to a nonclosed ticket. The UI refreshes detail/list data after success. Closed tickets reject replies until reopened. |
| FR-08 | Support/admin can claim an unassigned ticket; claiming moves an open ticket to `in_progress`. Only its assignee or an administrator may release an assigned ticket. Competing claims must not silently overwrite an assignee. |
| FR-09 | Support/admin may set a nonclosed ticket to `open`, `in_progress`, `waiting_student`, or `resolved`, and may close it. The creator can close their own nonclosed ticket or reopen their own closed/resolved ticket to `open`. Other student status transitions are forbidden. Closed tickets must reopen to `open` before another active status. Record status/assignment/reply events for review. |
| FR-10 | Role-aware dashboard shows counts within the same visibility rules as the queue. No student receives global ticket metrics. |
| FR-11 | User-facing forms show validation errors, loading/error/empty states, and accessible labels. Queue/detail/create/login/navigation work on mobile and desktop. |
| FR-12 | Browser-accessible OpenAPI documentation describes implemented contracts. Model/service/API/auth/permission/validation tests execute against MySQL 8.0; frontend tests and an actual browser workflow verify the core slice. |

## Initial vertical slice

Implement FR-04 + FR-05 + FR-06 first with FR-01 access protection: student login -> create form -> validated DRF request -> service/ORM -> MySQL -> response -> refreshed queue/detail. Then add collaboration/status/assignment in bounded tasks. Infrastructure health alone is not a completed core feature.

## Excluded from version one

University SSO, public self-registration, payments, email/SMS delivery, attachments, rich text/HTML, internal notes, SLA automation, real-time sockets, multi-university tenancy, and production hosting. None is required by a supplied functional specification; each would add security, operational, or external-service requirements.

## Unavailable metadata

University name, actual team members/student IDs, instructor identity, and current submission deadline remain unavailable. Use labeled documentation placeholders only. Interface defaults to English; no university branding or institutional identity is claimed.
