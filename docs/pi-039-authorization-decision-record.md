# PI-039 — Authorization Decision Record

## Purpose

Create one explainable record for every provider-bound authorization decision.

## Record answers

- Who is the subject?
- Which task was requested?
- Which provider was considered or selected?
- Was execution allowed?
- Why was it allowed or denied?
- Which fields were allowed across the boundary?
- Which fields were denied?
- Which policy layers contributed to the decision?
- When did the decision occur?

## Architecture

`Consent + Permissions + Provider Policy + Data Boundary + Resource/Quota → Authorization Decision Record → Audit Log`

## Privacy rule

The decision record describes the authorization decision without storing the user's sensitive payload. The record should contain metadata about what happened, not a copy of the private information being protected.

## Explainability

A future Personal Intelligence should be able to explain a decision in plain language from this record, for example:

> Allowed local execution because consent was active, the task was authorized, the data boundary permitted the selected fields, and local resource capacity was available.

Or:

> Denied cloud execution because the task required high privacy and the provider was not authorized for high-privacy data.

## Next step

PI-040 should add **persistent authorization history and revocation propagation**, so consent changes can invalidate future decisions across workers, queues, and provider sessions rather than only changing an in-memory registry.
