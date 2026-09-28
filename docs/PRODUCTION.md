# NEXXA Production Plan

This document is the authoritative implementation order for NEXXA.

# PHASE 0 — DOCUMENTATION & ARCHITECTURE

## Objective

Finalize the complete product specification before building the actual production server.

## Required documents

- README.md
- ARCHITECTURE.md
- PROVIDERS.md
- MUSIC.md
- IMPORT.md
- DATABASE.md
- API.md
- SECURITY.md
- FRONTEND.md
- MOBILE.md
- TESTING.md
- DEPLOYMENT.md
- ROADMAP.md
- DECISIONS.md
- BLACKHOLE_REFERENCE.md

## Rule

No production server implementation begins before Phase 0 is reviewed.

---

# PHASE 1 — SERVER FOUNDATION

## Objective

Create a clean and stable NEXXA backend.

## Required work

### Project structure

Create separate modules for:

- configuration
- API
- database
- models
- services
- providers
- authentication
- utilities
- logging
- errors

### Configuration

All environment-specific values must come from configuration/environment variables.

Examples:

```text
DATABASE_URL
SECRET_KEY
SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET
YOUTUBE_CONFIGURATION
JIOSAAVN_CONFIGURATION
```

Actual variables will be finalized during implementation.

### Health

Implement:

```http
GET /api/v1/health
```

The endpoint must provide a useful service health response.

### Database

Set up:

- connection
- migrations
- base models
- transaction handling

### API

Use versioning:

```text
/api/v1
```

### Error handling

Use a consistent API error structure.

### Logging

Use structured logs.

Do not log secrets or tokens.

### Security foundation

Implement the foundation for:

- authentication
- authorization
- CORS
- rate limiting strategy
- secure configuration

---

# PHASE 2 — CORE MUSIC ENGINE

## Objective

Build NEXXA's internal music domain independently of external providers.

## Models

- Track
- Artist
- Album
- Playlist
- Queue
- History
- Favorite
- PlaybackState

## Required concepts

### Track identity

A NEXXA Track is an internal normalized object.

Provider IDs are stored separately.

### Queue

Support:

- add
- remove
- reorder
- clear
- play next
- play later

### Playback state

Track:

- current track
- position
- duration
- playing/paused
- queue
- shuffle
- repeat

### Search abstraction

Search must not be directly tied to one provider.

---

# PHASE 3 — PROVIDER INTEGRATIONS

Implement providers separately.

Order:

1. Spotify
2. YouTube
3. YouTube Music
4. JioSaavn

Each provider must expose capabilities.

Example:

```json
{
  "search": true,
  "track": true,
  "album": true,
  "artist": true,
  "playlist": true,
  "library_import": false,
  "playback_resolution": false,
  "lyrics": false,
  "radio": false
}
```

Unsupported operations must return explicit unsupported capability behavior.

---

# PHASE 4 — LIBRARY

Implement:

- favorites
- playlists
- history
- albums
- artists
- local music
- metadata normalization
- duplicate detection
- provider mapping
- library indexing

---

# PHASE 5 — UNIVERSAL LIBRARY IMPORT

Implement:

```text
Connect
   ↓
Authenticate
   ↓
Discover
   ↓
Paginate
   ↓
Normalize
   ↓
Match
   ↓
Preview
   ↓
Import
   ↓
Report
```

Import must be safe and traceable.

---

# PHASE 6 — DOWNLOADS & OFFLINE

Implement:

- download manager
- job state
- storage management
- offline index
- retries
- cancellation
- cleanup
- storage limits

Only implement downloads from sources where the actual source and its terms technically permit the operation.

---

# PHASE 7 — LYRICS / RADIO / RECOMMENDATIONS

Implement:

- lyrics abstraction
- synced lyrics where available
- radio
- artist radio
- playlist radio
- recommendations
- trending

External/unstable services must be isolated behind adapters.

---

# PHASE 8 — WEB FRONTEND

Implement:

- app shell
- navigation
- home
- search
- player
- queue
- library
- playlists
- favorites
- imports
- downloads
- lyrics
- radio
- settings
- account

---

# PHASE 9 — ANDROID / PWA

Implement:

- Android responsive layout
- background playback
- media notifications
- media buttons where supported
- permissions
- storage
- offline state
- installable PWA where supported

---

# PHASE 10 — SECURITY / QA / PERFORMANCE

Perform:

- secret audit
- dependency audit
- authentication audit
- authorization audit
- rate-limit review
- CORS review
- provider failure testing
- import stress testing
- mobile testing
- performance testing
- accessibility testing

---

# PHASE 11 — PRODUCTION DEPLOYMENT

Implement:

- production environment
- HTTPS
- database
- storage
- monitoring
- structured logs
- backups
- deployment pipeline
- rollback procedure

---

# STRICT PHASE RULE

Never implement Phase 8 UI while Phase 1 server foundations are broken.

Never implement Phase 5 import before the provider interfaces and library models are stable.

Never implement production deployment before security and QA.
