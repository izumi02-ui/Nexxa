# NEXXA Architecture

## Architecture Principle

NEXXA must remain provider-independent.

The internal application should not care whether a track originated from Spotify, YouTube, YouTube Music, JioSaavn or local storage.

---

## High-Level Architecture

```text
                  NEXXA CLIENT
              Android / Web / PWA
                       |
                       v
                 NEXXA API
                       |
       +---------------+----------------+
       |               |                |
   Auth Service    Music Service    Library
       |               |                |
       +---------------+----------------+
                       |
                 Provider Layer
                       |
       +---------------+----------------+
       |          |          |          |
    Spotify   YouTube   YouTube Music JioSaavn
                       |
                       v
              Database / Cache
                       |
                       v
                   Storage
```

---

## Backend Layers

### API Layer

Responsible for:

- HTTP
- request validation
- authentication checks
- response serialization

### Service Layer

Responsible for application logic.

Examples:

- MusicService
- LibraryService
- ImportService
- DownloadService

### Domain Layer

Contains NEXXA's normalized entities.

### Provider Layer

Contains external-service implementations.

### Persistence Layer

Contains:

- database
- cache
- storage

---

## Provider Isolation

Do not write:

```text
Spotify API call directly inside playlist business logic
```

Instead:

```text
Playlist Service
      |
Provider Interface
      |
Spotify Provider
```

This allows providers to be replaced without rewriting the application.

---

## Track Identity

A track can exist on multiple services.

Example:

```text
NEXXA Track ID: 10042

Spotify:
abc123

YouTube:
xyz987

JioSaavn:
saavn456
```

These are mappings to one normalized NEXXA identity when matching is sufficiently confident.

---

## Failure Isolation

A failed provider must not crash the entire NEXXA server.

Example:

```text
Spotify DOWN
     |
     +---- YouTube still works
     +---- JioSaavn still works
     +---- Local library still works
```

---

## Background Jobs

Use background jobs for long operations:

- large imports
- downloads
- metadata processing
- cache rebuilds

Do not hold a normal HTTP request open for a huge library import.

---

## API Versioning

First API:

```text
/api/v1
```

Breaking changes should use a new version instead of silently changing the old contract.
