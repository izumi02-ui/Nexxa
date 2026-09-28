# NEXXA

## Product Identity

**Product Name:** NEXXA

**Tagline:** None

NEXXA is a cross-platform music application designed to provide a unified music experience across Android, Web/PWA and compatible desktop environments.

NEXXA is being designed around the feature set researched from the BlackHole Music application, but NEXXA will have its own architecture, UI, branding and implementation.

---

## Primary Goals

NEXXA should provide:

- Online music discovery and playback where technically supported
- Offline/local music playback
- Search
- Queue management
- Shuffle and repeat
- Background playback
- Notification/media controls
- Mini player
- Spotify integration
- YouTube integration
- YouTube Music integration
- JioSaavn integration
- Universal library import
- Playlists
- Favorites
- History
- Downloads/offline library
- Lyrics
- Radio
- Trending content
- Recommendations
- Artists
- Albums
- Local music
- Cache/storage management
- Sharing
- Personalization
- Update checking

---

## Important Product Rule

NEXXA is not a clone of BlackHole.

BlackHole is used as a reference for feature discovery and architecture research. NEXXA must implement its own system.

Do not copy:
- BlackHole branding
- BlackHole UI identity
- private credentials
- exposed provider secrets
- source code without appropriate rights
- undocumented assumptions about third-party services

---

## Development Rule

NEXXA is developed phase-by-phase.

The authoritative phase order is in:

`docs/PRODUCTION.md`

A future phase must not be implemented early unless explicitly approved.

---

## Target Platforms

### Android

Primary mobile target.

### Web / PWA

Responsive web application with installable PWA support where browser capabilities allow it.

### Desktop

Desktop-compatible web application initially. A dedicated native desktop client may be considered later.

---

## Core Architecture

```text
NEXXA Client
    |
    v
NEXXA API
    |
    +---- Authentication
    |
    +---- Music Services
    |
    +---- Library
    |
    +---- Import
    |
    +---- Downloads
    |
    +---- Lyrics
    |
    +---- Recommendations
    |
    v
Provider Layer
    |
    +---- Spotify
    +---- YouTube
    +---- YouTube Music
    +---- JioSaavn
    |
    v
Database / Cache / Storage
```

---

## Product Philosophy

NEXXA should feel:

- fast
- clean
- premium
- dark
- modern
- music-first
- reliable
- responsive
- useful rather than decorative

The interface must not become a generic statistics dashboard.

---

## Phase Completion Rule

A phase is complete only after:

1. Implementation is complete.
2. Tests are written and passing.
3. Runtime behavior is verified.
4. Documentation is updated.
5. Known limitations are documented.

Only then should the next phase begin.
