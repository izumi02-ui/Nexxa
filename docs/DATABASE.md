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

### Playlist

Represents a NEXXA playlist.

### PlaylistTrack

Stores the relationship between a playlist and a track.

### Favorite

Stores a user's favorite tracks.

### HistoryEntry

Stores playback history.

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
