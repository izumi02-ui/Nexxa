# NEXXA

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

NEXXA is a cross-platform music application designed to provide a unified music experience across Android, Web/PWA, and compatible desktop environments.

## Primary Goals

NEXXA is planned to provide:

- Online music discovery and playback where technically supported
- Offline and local music playback
- Search
- Queue management
- Shuffle and repeat
- Background playback
- Notification and media controls
- Mini player
- Spotify integration
- YouTube integration
- YouTube Music integration
- JioSaavn integration
- Universal library import
- Playlists
- Favorites
- Playback history
- Downloads and offline library
- Lyrics
- Radio
- Trending content
- Recommendations
- Artists and albums
- Local music
- Cache and storage management
- Sharing
- Personalization
- Update checking

## Product Principles

NEXXA is developed as an independent product with its own architecture, interface, branding, and implementation.

External services and publicly available technical references may be used to evaluate features and integration requirements, but NEXXA's implementation remains its own.

The project must not copy third-party branding, user interfaces, private credentials, exposed provider secrets, protected source code, or undocumented assumptions about external services.

## Development Process

Development is organized into defined phases. The authoritative implementation order is documented in `docs/PRODUCTION.md`.

A later phase should not be implemented before the foundations required by earlier phases are stable.

## Target Platforms

### Android

The primary mobile target, with support for background playback, media controls, local audio, storage, and responsive interaction.

### Web / PWA

A responsive web application with installable PWA support where browser capabilities allow it.

### Desktop

A desktop-compatible web application initially. A dedicated native desktop client may be considered later.

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

## Product Direction

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

The interface should not become a generic statistics dashboard.

## Phase Completion

A phase is complete only after:

1. Implementation is complete.
2. Tests are written and passing.
3. Runtime behavior is verified.
4. Documentation is updated.
5. Known limitations are documented.

Only then should the next phase begin.
