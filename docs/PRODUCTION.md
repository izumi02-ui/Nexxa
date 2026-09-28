# NEXXA Production Plan

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

This document defines the recommended implementation order for NEXXA.

# PHASE 0 — DOCUMENTATION & ARCHITECTURE

## Objective

Finalize the product specification and architecture before building the production server.

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
- FEATURE_RESEARCH.md

## Rule

Do not begin production server implementation until the Phase 0 architecture and requirements have been reviewed.

# PHASE 1 — SERVER FOUNDATION

## Objective

Create a clean and stable NEXXA backend.

## Required work

### Project Structure

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

All environment-specific values must come from configuration or environment variables.

Examples:

```text
DATABASE_URL
SECRET_KEY
SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET
YOUTUBE_CONFIGURATION
JIOSAAVN_CONFIGURATION
```

Actual variable names will be finalized during implementation.

### Health

Implement:

```http
GET /api/v1/health
```

The endpoint must provide a useful service-health response.

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

### Error Handling

Use a consistent API error structure.

### Logging

Use structured logs.

Do not log secrets or tokens.

### Security Foundation

Implement the foundation for:

- authentication
- authorization
- CORS
- rate limiting strategy
- secure configuration

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

## Required Concepts

### Track Identity

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

### Playback State

Track:

- current track
- position
- duration
- playing/paused
- queue
- shuffle
- repeat

### Search Abstraction

Search must not be directly tied to one provider.

# PHASE 3 — PROVIDER INTEGRATIONS

Implement providers independently.

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

Unsupported operations must return explicit unsupported-capability behavior.

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

Only implement downloads from sources where the actual source and applicable terms technically permit the operation.

# PHASE 7 — LYRICS / RADIO / RECOMMENDATIONS

Implement:

- lyrics abstraction
- synced lyrics where available
- radio
- artist radio
- playlist radio
- recommendations
- trending

External or unstable services must be isolated behind adapters.

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

# STRICT PHASE RULE

Do not implement Phase 8 UI while Phase 1 server foundations are broken.

Do not implement Phase 5 import before provider interfaces and library models are stable.

Do not implement production deployment before security and QA are complete.
