# PI-034 — Personal Data Boundary & Minimization

## Purpose

Turn the principle that personal data is sacred into an enforceable boundary between the Personal Intelligence and outside providers.

## Core rule

**A provider receives only the information required for the task, authorized for that provider, and compatible with the task's purpose.**

## Policy layers

1. **Sensitivity** — normal, sensitive, secret, or other explicit classes.
2. **Purpose** — why the information is being used.
3. **Provider authorization** — what that provider is allowed to receive.
4. **Privacy level** — high-privacy tasks remain local-only.
5. **Minimization** — unnecessary fields are excluded rather than transmitted.

## Architecture

`Task → Data Boundary → Minimized Payload → Provider`

The boundary sits before provider execution. Routing chooses *where* work goes; the data boundary determines *what* crosses that boundary.

## Important safety property

The boundary does not grant access. It only evaluates whether information may cross an already-authorized provider boundary. Credentials and provider permissions remain separate concerns.

## Unknown data

Unknown or unclassified information should not automatically become safe to transmit. Future versions should support explicit classification and a default-deny policy for sensitive fields where classification is absent.

## High-privacy behavior

High-privacy tasks are local-only. If no authorized local provider is available, the system should defer or request human intervention rather than silently sending the data elsewhere.

## Next step

PI-035 should connect the data boundary to **provider-specific policy profiles**, allowing the Personal Intelligence to know exactly what each provider may receive and under what conditions.
