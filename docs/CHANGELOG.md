# NEXXA Changelog

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Unreleased

### Project Initialization

- Product name finalized as NEXXA.
- No tagline is defined.
- Initial product scope documented.
- Phase-gated production plan documented.
- Music architecture documented.
- Provider architecture documented.
- Universal library import documented.
- Database plan documented.
- API plan documented.
- Security plan documented.
- Frontend plan documented.
- Android/PWA plan documented.
- Testing plan documented.
- Deployment plan documented.
- Feature research consolidated into `docs/FEATURE_RESEARCH.md`.

---

### Phase 0 — Documentation

- Completed product scope documentation.
- Completed architecture documentation.
- Completed provider architecture documentation.
- Completed music architecture documentation.
- Completed import architecture documentation.
- Completed database documentation.
- Completed API documentation.
- Completed security documentation.
- Completed frontend documentation.
- Completed mobile documentation.
- Completed testing documentation.
- Completed deployment documentation.
- Completed architecture/engineering decisions.
- Completed feature research consolidation.

---

### Phase 1 — Server Foundation

- Completed backend project foundation.
- Completed configuration system.
- Completed environment system.
- Completed logging foundation.
- Completed health endpoint.
- Completed API versioning.
- Completed database foundation.
- Completed migration system.
- Completed request validation.
- Completed error handling foundation.
- Completed provider interfaces.
- Completed authentication foundation.

---

### Phase 2 — Core Music

- Completed track model and core track handling.
- Completed artist model.
- Completed album model.
- Completed playlist functionality.
- Completed queue functionality.
- Completed playback state.
- Completed search abstraction.
- Completed source resolution.
- Completed metadata normalization.

---

### Phase 3 — Providers

- Completed Spotify provider integration.
- Completed YouTube provider integration.
- Completed YouTube Music provider integration.
- Apple Music provider remains planned and is not yet implemented.

---

### Phase 4 — Library

#### Favorites

- Favorites functionality completed.

#### Playlists

- Playlist library functionality completed.

#### History

- Added `HistoryEntry` database model.
- Added history database migration `0003_create_history`.
- Added history request and response schemas.
- Added history create service.
- Added history list service.
- Added history delete service.
- Added history clear service.
- Added authenticated history routes.
- Added per-user history ownership and isolation.
- Added history input validation.
- Added history service tests.
- Added authenticated history route tests.
- Added cross-user isolation tests.
- Added history validation and edge-case tests.
- Added history API route registration tests.

#### Albums

- Added album creation functionality.
- Added album retrieval functionality.
- Added album listing functionality.
- Added album tracks endpoint.
- Added album validation.
- Added album service tests.
- Added album API tests.
- Added album validation tests.
- Added album API route registration tests.
- Added album database documentation.
- Added album API documentation.

#### Recommendations

- Added recommendation service.
- Added recommendation API route.
- Added authenticated user context for recommendations.
- Added user-specific listening-history recommendation context.
- Added user-specific favorite recommendation context.
- Added user-specific playlist recommendation context.
- Added per-user recommendation generation.
- Added cross-user recommendation isolation tests.
- Added recommendation service tests.
- Added recommendation API tests.
- Added recommendation API documentation.
- Added recommendation database relationship documentation.

---

Only record actual project changes here.
