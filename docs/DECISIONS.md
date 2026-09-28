# NEXXA Architecture Decisions

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## ADR-001 — Product Name

The product name is:

**NEXXA**

No tagline is defined.

## ADR-002 — Independent Product

NEXXA is developed as an independent product with its own architecture, interface, implementation, and branding.

## ADR-003 — Provider Abstraction

Spotify, YouTube, YouTube Music, and JioSaavn are isolated behind provider interfaces.

**Reason:** External services change independently and should not dictate the internal NEXXA architecture.

## ADR-004 — Normalized Library

NEXXA maintains its own internal track, artist, and album identities.

External IDs remain provider-specific mappings.

## ADR-005 — Universal Import

Library import is read-oriented.

The original external library is not modified during import.

## ADR-006 — Phase Gating

Development follows `docs/PRODUCTION.md`.

Future phases should not be implemented early without an explicit architectural reason and review.

## ADR-007 — Backend First

The stable server, domain, and provider foundation should exist before the complete frontend is built.

This reduces unnecessary architectural rewrites.
