# NEXXA Development Rules

## Phase Rule

Always follow:

```text
docs/PRODUCTION.md
```

Do not skip foundations.

---

## Code Principles

- modular
- readable
- typed
- provider-isolated
- testable
- explicit errors
- secure configuration
- no hardcoded secrets

---

## Commit Style

Examples:

```text
feat: add server health endpoint
feat: add provider abstraction
feat: add spotify provider
feat: add library import
fix: handle expired provider token
test: add import matching cases
docs: update provider specification
```

---

## Change Discipline

Do not mix unrelated features into one change.

Do not redesign the frontend while fixing a backend bug.

Do not add future-phase functionality just because it is convenient.

---

## Provider Changes

A provider implementation should remain isolated from core domain logic.

---

## Security

Any secret accidentally exposed in code must be treated as compromised and rotated.
