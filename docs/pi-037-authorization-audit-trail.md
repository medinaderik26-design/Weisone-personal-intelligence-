# PI-037 — Authorization Audit Trail

## Purpose

Make provider authorization decisions explainable and reviewable.

The Personal Intelligence should be able to answer:

> What did you allow? What did you deny? Which provider was involved? Why?

## Recorded decision

Each authorization event records:

- task ID
- provider
- allowed or denied
- reason
- timestamp
- optional decision details

## Architecture

`Authorization Gate → AuthorizationAuditLog → Review / Accountability`

The audit trail records decisions; it does not grant permission and does not execute work.

## Safety

The reference implementation is append-only through its public API. It returns copies when reading collections so callers cannot mutate the internal log accidentally.

Future durable implementations should address retention, access control, integrity protection, and encryption where appropriate.

## Privacy

Audit records should contain decision metadata rather than copies of sensitive user content. The audit system should explain *why* a request was allowed or denied without becoming a second uncontrolled personal-data store.

## Next step

PI-038 should add a **Consent & Revocation Layer** so the person can explicitly grant, withdraw, and review provider/tool permissions over time.
