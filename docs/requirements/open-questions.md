# Application specification and open questions

Updated: November 26, 2026 (Asia/Tehran).

## Confirmed from the user

| Fact | User-provided information |
| --- | --- |
| Application concept | Ticketing system |
| Target audience | Students at a specific university (university not named) |
| Handling roles | University support staff and administrator |
| Scope discretion | User requested “do as much as you can”; documented implementation choices are in `scope.md` |
| Required stack | Django/DRF, React JavaScript, MySQL 8.0, Docker Compose |
| Delivery | Actual implementation, executed tests, granular commits, feature branches integrated into `main`, GitHub pushes |

The assignment's sample clinic and ticket examples do not supply additional approved functionality. The user delegated unspecified implementation details; [version-one scope](scope.md) records the selected lifecycle and permissions explicitly.

## Clarifications and resolution

1. **Ticket recipients and roles:** Who receives and answers tickets? Are there university support staff, department staff, administrators, or another group? What can each role read and change? Can any student see another student's tickets?
2. **Core workflows and business rules:** What must ticket submission contain, how are recipients/categories selected, how do replies work, what statuses exist, who changes them, and who closes/reopens a ticket? Which features are required in version one versus explicitly excluded?
3. **Account provisioning:** Do students register, receive accounts, or use an existing university identity provider? How is eligibility at the university established? Do not implement unrestricted registration or an assumed SSO integration without an answer.

The user answered the role question and delegated the remaining scope decisions. The implementation proceeds with administrator-provisioned accounts, a private student queue, a shared support queue, public replies within each ticket, and the lifecycle in [scope](scope.md). No further clarification is required to build this bounded version. The numbered questions above preserve the original discovery record; they are resolved by these explicitly documented choices, subject to later user revision.

## Nonblocking information for final documentation

- University/project display name and preferred interface language/direction.
- Team members, student IDs if the course requires them, actual responsibilities, and instructor/course metadata.
- Applicable submission year and current deadlines. S1 page 6 says 9 Aban without a year; S2 provides no date.
- Deployment destination, real domain name, and production TLS/identity/email credentials, if deployment is requested.

Use explicitly labeled unavailable values only where the final documentation requires these facts. Never fabricate team participation, citations, live deployment, or a Figma file.

## Acceptance criteria gate

The [scope](scope.md) now defines FR-01 through FR-12 and selects the first UI -> API -> business logic -> MySQL -> UI slice. Update [traceability](traceability.md) with implementation files and executed evidence as work completes.
