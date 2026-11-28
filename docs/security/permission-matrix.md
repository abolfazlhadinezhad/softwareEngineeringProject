# Implemented permission matrix

Backend querysets and services enforce these rules. Role account types select login experience and baseline student/admin behavior; configurable `AccessRole.permissions` and `RoleAssignment.department` extend staff permissions. Scopes are explicit individual departments, not implicitly inherited by descendants.

| Capability | Guest | Student | Agent membership | Manager membership | System admin |
| --- | --- | --- | --- | --- | --- |
| Public published help/FAQ/announcements/directory | Yes | Yes | Yes | Yes | Yes |
| Create ticket | No | Own; category determines department/priority | No | No | No |
| Read ticket | No | Own | Authorized department/assignment | Own departments | All normal records |
| Read restricted/confidential ticket | No | Own | Explicit permission in scope or unexpired ticket grant | Same, no implicit manager access | Same, no routine bypass |
| Reply/claim/internal note | No | Reply own, no notes/claim | Scoped | Scoped | Visible records only |
| Resolve/close/reopen | No | Confirm/reopen eligible own ticket | Scoped state machine | Scoped state machine | Visible records/state machine |
| Transfer/export/priority permission | No | No | Explicit role needed | Department baseline | Visible records |
| Department reports | No | No | Explicit role | Own departments | University aggregate |
| Content publishing | No | No | Explicit role | Explicit role | Yes |
| Configure units/forms/calendars | No | No | Explicit role | Explicit role | Yes |
| Manage role definitions/assignments | No | No | Global explicit role | Global explicit role | Yes |
| Student import/activation issuance | No | No | Global explicit role | Global explicit role | Yes |
| Settings/audit/system health | No | No | Global explicit role | Global explicit role | Yes |

Granular catalog: `GET /api/v1/manage/permissions/`. Defaults are implemented in `apps/portal/permissions.py`. Manager baseline contains view/reply/assign/resolve/close/reopen/internal-note/transfer/priority/export/department-report permissions. The priority capability is reserved; a manager adjustment endpoint is not yet implemented. Configurable role definitions do not confer Django maintenance-console permissions.

Lists, details, metrics, notifications, attachments and exports all re-evaluate visibility. Exports add `ticket.export`; university aggregate reports expose counts/durations without granting ticket-content access. Note bodies/internal events never enter student serializers; notification previews contain generic messages only. Confidential detail/download access is audited. Emergency grants require a justified expiring record, but an approval/reauthentication UI and comprehensive list-access audit remain backlog work.

Planned distinct specialist, supervisor, KB-editor and report-viewer configurations use the catalog; predefined presets for every master-prompt role are not yet seeded. MFA, sensitive-operation reauthentication, role-change active-session revocation and audit tamper-resistant archival remain production gates.
