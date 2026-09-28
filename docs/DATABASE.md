# NEXXA Database

## Core Tables / Entities

### User

Represents a NEXXA user.

### Account

Authentication/account information.

### ProviderConnection

Stores a user's connection to a provider.

### Track

Normalized internal track.

### Artist

Normalized artist.

### Album

Normalized album.

### Playlist

NEXXA playlist.

### PlaylistTrack

Relationship between playlist and track.

### Favorite

User's favorite tracks.

### HistoryEntry

Playback history.

### Queue

Current or saved queue state.

### Download

Download job and local file information.

### Lyrics

Lyrics metadata/content reference.

### ImportJob

One import operation.

### ImportItem

One item inside an import.

### ProviderMetadata

Provider-specific metadata.

### CacheEntry

Cached external data.

### Setting

User/application settings.

---

# Provider Mapping

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

---

# Important Database Rules

Use:

- foreign keys
- unique constraints
- indexes
- timestamps
- transactions

Do not store duplicate normalized entities without a reason.

---

# Import Transactions

Small atomic operations should use database transactions.

Large imports should use resumable job state rather than one enormous transaction.

---

# Deletion

User-facing deletion must distinguish:

- removing from NEXXA library
- deleting downloaded file
- removing provider mapping
- deleting playlist relationship

Never accidentally interpret one as another.
