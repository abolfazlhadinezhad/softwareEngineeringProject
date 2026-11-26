# API contract

Base URL: `/api`. All application endpoints require an authenticated Django session except `GET /health/`, `GET /auth/csrf/`, `POST /auth/login/`, and schema/docs endpoints. Mutating browser requests require the CSRF token returned by `/auth/csrf/`. JSON errors use `{ "error": { "status": number, "details": object } }`.

The live schema is generated from source at [`/api/schema/`](http://localhost:8000/api/schema/) and Swagger UI at [`/api/docs/`](http://localhost:8000/api/docs/) when Compose is running. This table describes the version-one contract; schema output is authoritative if a representation changes.

## Authentication

| Method | Path | Request | Response / codes |
| --- | --- | --- | --- |
| GET | `/auth/csrf/` | none | `{csrfToken}`; 200; `Cache-Control: no-store` |
| POST | `/auth/login/` | `{username, password}` | Public user representation; 200; 400 validation; 403 invalid/disabled credentials; 429 throttle. CSRF required. |
| GET | `/auth/me/` | none | User representation; 200; 403 unauthenticated. |
| POST | `/auth/logout/` | none | 204; 403 unauthenticated/CSRF failure. |

User representation: `{id, username, first_name, last_name, role}`. Passwords, session identifiers, permissions, and secrets are never returned.

## Ticket resources

Ticket list representation: `id`, `title`, `status`, `priority`, `category {id,name}`, `created_by {id,username}`, `assignee {id,username}|null`, `created_at`, `updated_at`. Ticket detail adds `description`, chronological `replies`, and reverse chronological `events`.

| Method | Path | Access and request | Success / failure |
| --- | --- | --- | --- |
| GET | `/categories/` | Any signed-in user; active categories only | 200 list; 403 unauthenticated. |
| GET | `/tickets/` | Student sees own tickets; support/admin see all. Query: `search`, `status`, `priority`, `category`, `page`. | 200 paginated `{count,next,previous,results}`; 400 invalid filter; 403 unauthenticated. |
| POST | `/tickets/` | Student only. `{title<=160,description<=10000,category,priority}`. Server sets creator/open/timestamps. | 201 detail; 400 validation/inactive category; 403 staff. |
| GET | `/tickets/{id}/` | Same visibility as list; no existence disclosure to another student. | 200 detail; 403 unauthenticated; 404 unavailable. |
| POST | `/tickets/{id}/reply/` | Creator/support/admin; `{body<=10000}`; closed tickets rejected. | 201 reply; 400 validation/closed; 403/404. |
| POST | `/tickets/{id}/claim/` | Support/admin; unassigned, nonclosed. | 200 detail; 400 closed; 403 role; 404; 409 competing assignee. |
| POST | `/tickets/{id}/release/` | Assignee or admin; support cannot release another staff member's assignment. | 200 detail; 403/404. |
| POST | `/tickets/{id}/status/` | Support/admin; `{status}`. Closed can only move to `open`. | 200 detail; 400 invalid transition; 403/404. |
| POST | `/tickets/{id}/close/` | Creator for own ticket or support/admin. | 200 detail; 403/404. |
| POST | `/tickets/{id}/reopen/` | Creator for own closed ticket or support/admin. | 200 detail; 400 if not closed; 403/404. |
| GET | `/metrics/` | Visibility-scoped dashboard counts. | 200 `{all,active,closed,by_status}`; 403. |

## HTTP and data rules

- `400` is input/state validation, `403` is authentication/role/object authorization, `404` is an unavailable ticket, `409` is a concurrent claim conflict, and `429` is rate limiting.
- Titles/descriptions/replies are plain text and trimmed server-side. HTML is not accepted or rendered.
- Category deletion is not exposed; administrators deactivate categories in Django admin. Existing tickets retain their category.
- `created_at`/`updated_at` are ISO-8601 timezone-aware values. The UI formats them for the viewer; persistence remains authoritative in MySQL.
- List queries are role-scoped before filters and pagination. Metrics use the same scope. No endpoint accepts client-supplied `created_by`, `assignee`, role, status history, or event actor.
