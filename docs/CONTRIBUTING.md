# Contributing to NEXXA

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Development Order

Follow the implementation order in `docs/PRODUCTION.md`. Build and stabilize the foundations before moving to later phases.

## Code Principles

NEXXA code should be:

- modular
- readable
- typed where the language supports it
- isolated from provider-specific details
- testable
- explicit about errors
- securely configured
- free of hardcoded secrets

## Commit Style

Use concise, descriptive commit messages. Examples:

```text
feat: add server health endpoint
feat: add provider abstraction
feat: add spotify provider
feat: add library import
fix: handle expired provider token
test: add import matching cases
docs: update provider specification
```

## Change Discipline

Keep unrelated changes separate.

- Do not mix unrelated features into one change.
- Do not redesign the frontend while fixing an unrelated backend issue.
- Do not introduce functionality from a future phase without a clear architectural reason and appropriate review.

## Provider Changes

Provider implementations should remain isolated from the core domain and application logic. Changes to an external service should not require rewriting normalized NEXXA entities or unrelated business rules.

## Security

If a secret is accidentally committed or exposed, treat it as compromised immediately and rotate it.
