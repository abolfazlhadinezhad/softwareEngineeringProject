# Implemented database relationships

MySQL 8.0/InnoDB/utf8mb4. Model source and committed migrations are authoritative. This diagram includes all domain models currently migrated; draft tables without operational workflows are identified below.

```mermaid
erDiagram
  User ||--o| Profile : identifies
  User ||--o{ Activation : activates
  Department o|--o{ Department : parent
  User ||--o{ Membership : joins
  Department ||--o{ Membership : contains
  User ||--o{ RoleAssignment : receives
  AccessRole ||--o{ RoleAssignment : grants
  Department o|--o{ RoleAssignment : scopes
  Department o|--o{ Category : owns
  Category o|--o{ Category : parent
  Department ||--o{ RequestForm : owns
  RequestForm o|--o{ Category : configures
  BusinessCalendar ||--o{ Holiday : excludes
  BusinessCalendar ||--o{ SLAPolicy : governs
  SLAPolicy o|--o{ Category : targets
  User ||--o{ Ticket : creates
  User o|--o{ Ticket : assigned
  Department o|--o{ Ticket : receives
  Category ||--o{ Ticket : classifies
  Ticket ||--o{ Reply : conversation
  User ||--o{ Reply : authors
  Ticket ||--o{ InternalNote : staff_only
  User ||--o{ InternalNote : authors
  Ticket ||--o{ TicketAttachment : protects
  User ||--o{ TicketAttachment : uploads
  Ticket ||--o{ TicketEvent : history
  User o|--o{ TicketEvent : acts
  Ticket ||--o| Feedback : evaluates
  Ticket ||--o{ AccessGrant : permits
  User ||--o{ AccessGrant : receives
  Ticket ||--o{ Escalation : breaches
  User ||--o{ Notification : receives
  Ticket o|--o{ Notification : references
  Department o|--o{ Article : owns
  User o|--o{ Article : authors
  Article }o--o{ Article : related
  Article ||--o{ ArticleRevision : revisions
  User o|--o{ ArticleRevision : edits
  Department o|--o{ FAQ : owns
  Article o|--o{ FAQ : explains
  Department o|--o{ Announcement : publishes
  User o|--o{ AuditLog : acts
  Department o|--o{ AuditLog : scope
  User ||--o{ ImportBatch : previews
  Department ||--o{ ResponseTemplate : owns
  SiteSettings { bigint id PK }
  SearchGap { bigint id PK }
```

Ticket has unique UUID tracking number, protected creator/category/department, nullable assignee, constrained status/priority, immutable JSON form snapshot/responses, SLA timestamps and a version counter. Compound indexes support creator/recent, status/recent, category/recent, department/status/recent and assignee/status queries. Separate deadline indexes support monitoring. Existing tickets receive individual UUIDs through a staged nullable/backfill/unique migration; existing organizationally unclassified records remain visible to their student and normal-record administrators until classified.

Membership is unique per user/department; holidays per calendar/date; escalation per ticket/trigger/level; feedback per ticket; notification idempotency keys and activation digests are unique. Organizational/content management APIs support updates/deactivation, not destructive deletion. Events/audits have no mutation API. Django's own auth groups/permissions, sessions and migration tables remain framework infrastructure.

ResponseTemplate and SearchGap currently have schema only. AccessGrant can be provisioned by maintenance ORM but has no emergency-access approval UI. Assignment strategies are stored but only manual claim is operational. Do not equate these tables with completed product features.
