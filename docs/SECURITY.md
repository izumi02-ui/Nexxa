# NEXXA Security

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Secret Management

Never commit:

- Spotify Client Secret
- API keys
- OAuth secrets
- database passwords
- signing secrets
- real `.env` files

Use environment variables during development and a secure secret-management solution in production.

## OAuth

Protect provider access and refresh tokens.

Do not unnecessarily send provider tokens to the client.

## Authentication

Authentication must use secure password, session, or token handling as appropriate to the implementation.

Passwords must never be stored in plaintext.

## Authorization

Every protected resource must verify:

1. the user is authenticated
2. the user owns or is permitted to access the resource
3. the required permission is present

## Rate Limiting

Protect high-risk or expensive endpoints such as:

- authentication
- search
- import
- downloads
- provider proxy operations

## Logging

Never log:

- passwords
- access tokens
- refresh tokens
- API secrets
- authorization headers

## CORS

Production CORS must use an explicit allowlist.

Do not use unrestricted origins in production.

## Upload / Download Security

Validate:

- file type
- file size
- path
- storage ownership

Never allow user-controlled paths to escape the application's storage directory.

## Pre-Production Security Checklist

- [ ] secret scan
- [ ] dependency audit
- [ ] OAuth audit
- [ ] authentication audit
- [ ] authorization audit
- [ ] CORS audit
- [ ] rate-limit audit
- [ ] file handling audit
- [ ] logging audit
