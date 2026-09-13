# PI-038 — Consent & Revocation

## Purpose

Make provider access explicitly granted, time-bounded when desired, and immediately revocable by the person who owns the Personal Intelligence.

## Core rule

**No consent means no provider access.**

Consent is scoped to:
- subject/person
- provider
- task type
- optional expiration

Revocation removes the grant from the active registry.

## Architecture

`Person → Consent Grant → Authorization Gate → Provider`

Revocation:

`Person → Revoke → Consent Registry → Future requests denied`

## Security properties

- Consent is explicit rather than inferred from prior use.
- Consent is scoped rather than universal.
- Expired grants are inactive.
- Revocation removes the active grant.
- The consent layer does not itself transmit data or execute tasks.
- Provider credentials remain outside the repository.

## Important boundary

Consent is not the same thing as data classification or provider capability. A request must satisfy all relevant layers:

**Consent + Provider Policy + Data Boundary + Permissions + Resource/Quota Constraints**

## Next step

PI-039 should combine consent, provider policy, data boundary, permissions, and audit records into one explainable **Authorization Decision Record** so every external action has a traceable reason.
