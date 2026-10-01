# NEXXA Database

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Core Tables / Entities

### User

Represents a NEXXA user.

### Account

Stores authentication and account information.

### ProviderConnection

Stores a user's connection to an external provider.

### Track

Represents a normalized internal track.

### Artist

Represents a normalized artist.

### Album

Represents a normalized album.

Album metadata includes the album title, owning artist, optional artwork URL, and optional release date.

The album-to-artist relationship is represented by `artist_id`.

Tracks may reference an album through `album_id`, allowing an album to expose its associated tracks without duplicating track records.

### Playlist

Represents a NEXXA playlist owned by a user.

A playlist is scoped to its owning user and must not be used as another user's recommendation context.

### PlaylistTrack

Stores the relationship between a playlist and a track.

This relationship connects a user's playlist data to normalized tracks.

### Favorite

Stores a user's favorite tracks.

Favorites are scoped to the authenticated user.

### HistoryEntry

Stores playback history.

History entries are scoped to the user who generated them and provide listening-history context for that user's recommendations.

### Queue

Stores current or saved queue state.

### Download

Stores download job and local file information.

### Lyrics

Stores lyrics metadata or a content reference.

### ImportJob

Represents one library import operation.

### ImportItem

Represents one item within an import.

### ProviderMetadata

Stores provider-specific metadata.

### CacheEntry

Stores cached external data.

### Setting

Stores user or application settings.

## Phase 4 — Recommendation Relationships

Recommendations are generated from the authenticated user's own data.

The recommendation context is based on these relationships:

```text
User
 ├── HistoryEntry ──> Track
 ├── Favorite ──────> Track
 └── Playlist
       └── PlaylistTrack ──> Track
```

### Recommendation user context

The authenticated user's ID is the ownership boundary for recommendation generation.

```text
authenticated_user.id
        │
        ├── HistoryEntry.user_id
        ├── Favorite.user_id
        └── Playlist.user_id
```

The recommendation service uses this user identity to collect that user's listening history, favorites, and playlists.

### Recommendation isolation

Recommendation context must remain isolated between accounts.

```text
User A
 ├── History A
 ├── Favorites A
 ├── Playlists A
 └── Recommendations A

User B
 ├── History B
 ├── Favorites B
 ├── Playlists B
 └── Recommendations B
```

User A's history, favorites, or playlists must never become recommendation context for User B.

The client must not be able to select another user's recommendation context by supplying a different user ID.

### Normalized track relationships

History, favorites, and playlist entries reference the normalized `Track` entity rather than creating duplicate track records.

```text
User
  │
  ├── HistoryEntry ──> Track
  │
  ├── Favorite ──────> Track
  │
  └── Playlist
        │
        └── PlaylistTrack ──> Track
```

This allows recommendation generation to combine multiple user signals around the same normalized track records.

## Provider Mapping

A provider mapping should contain:

```text
internal_entity_id
provider
external_id
external_url
```

Example:

```text
Track 10042
Spotify -> 7abc...
YouTube -> Xyz...
JioSaavn -> 123...
```

## Database Rules

Use:

- foreign keys
- unique constraints
- indexes
- timestamps
- transactions

Avoid duplicate normalized entities unless there is a defined reason to keep them separate.

User-owned tables must preserve ownership boundaries through the authenticated user's identity.

## Import Transactions

Small atomic operations should use database transactions.

Large imports should use resumable job state rather than one enormous transaction.

## Deletion Semantics

User-facing deletion must distinguish between:

- removing an item from the NEXXA library
- deleting a downloaded file
- removing a provider mapping
- deleting a playlist relationship

One operation must never be interpreted as another.
