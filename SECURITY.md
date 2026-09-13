# Security

This repository is public. Security is a design boundary, not a later feature.

## Never Commit

- API keys
- access tokens
- passwords
- private keys
- session cookies
- personal account credentials
- private customer data
- raw personal memory stores
- proprietary Wison Kernel/Glyphin source unless intentionally released

## Permission Model

Every external tool and provider should have an explicit capability boundary.

Example capabilities:

```text
GitHub: read / write / admin
Files: read / write / delete
Email: read / draft / send
Calendar: read / create / modify
```

Default should be least privilege.

## Data Boundary

Personal Intelligence should expose only the minimum information required for a task. Provider access should be scoped by purpose and revocable.

## Local-First Principle

Sensitive continuity data should be capable of remaining local. Cloud providers should receive only data permitted by the active policy.

## Incident Response

If a secret is exposed:

1. Revoke it immediately.
2. Rotate the credential.
3. Remove it from active source history where appropriate.
4. Audit related access.
5. Document the incident.
6. Add a regression check if possible.
