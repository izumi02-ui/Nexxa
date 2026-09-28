# NEXXA Architecture

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Architecture Principle

NEXXA remains independent of individual music providers.

The internal application should not need to know whether a track originated from Spotify, YouTube, YouTube Music, JioSaavn, or local storage.

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

## Backend Layers

### API Layer

Responsible for:

- HTTP handling
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

Contains NEXXA's normalized entities and core business concepts.

### Provider Layer

Contains integrations with external services.

### Persistence Layer

Contains:

- database
- cache
- storage

## Provider Isolation

Provider-specific API calls should remain outside core business logic.

```text
Playlist Service
      |
Provider Interface
      |
Spotify Provider
```

This allows providers to change or be replaced without rewriting the application domain.

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

These external identifiers map to one normalized NEXXA identity when matching is sufficiently confident.

## Failure Isolation

A failed provider should not bring down the entire NEXXA server.

```text
Spotify DOWN
     |
     +---- YouTube still works
     +---- JioSaavn still works
     +---- Local library still works
```

## Background Jobs

Use background jobs for long-running operations such as:

- large imports
- downloads
- metadata processing
- cache rebuilds

Do not keep a normal HTTP request open for a large library import.

## API Versioning

The initial API version is:

```text
/api/v1
```

Breaking changes should use a new API version rather than silently changing an existing contract.
