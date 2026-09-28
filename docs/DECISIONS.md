# NEXXA Architecture Decisions

## ADR-001 — Product Name

The product name is:

**NEXXA**

There is no tagline.

---

## ADR-002 — Original Product

NEXXA is its own product.

BlackHole is used as a feature/reference source only.

---

## ADR-003 — Provider Abstraction

Spotify, YouTube, YouTube Music and JioSaavn are isolated behind provider interfaces.

Reason:

Providers change independently and should not control the internal NEXXA architecture.

---

## ADR-004 — Normalized Library

NEXXA maintains its own internal track/artist/album identities.

External IDs remain provider-specific mappings.

---

## ADR-005 — Universal Import

Library import is read-oriented.

The original external library is not modified during import.

---

## ADR-006 — Phase Gating

Development follows `docs/PRODUCTION.md`.

Future phases must not be implemented early without explicit approval.

---

## ADR-007 — Backend First

The stable server/domain/provider foundation must exist before the complete frontend is built.

This reduces architectural rewrites.
