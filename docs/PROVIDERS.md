# NEXXA Providers

## 1. Spotify

### Known responsibilities

Spotify can provide metadata/library functionality such as:

- OAuth authorization
- user playlists
- playlist tracks
- search
- track details
- featured playlists
- supported user library metadata

### Known API base

```text
https://api.spotify.com/v1
```

### OAuth endpoints

```text
https://accounts.spotify.com/authorize
https://accounts.spotify.com/api/token
```

### Important rule

Spotify credentials belong on the server.

Never place the Spotify Client Secret inside:
- frontend JavaScript
- Android source
- public repository
- client bundle

Spotify should not be treated as a raw audio-stream source simply because a user connected Spotify.

---

# 2. YouTube

NEXXA may use a YouTube provider for:

- search
- metadata
- playlists
- supported source resolution

The exact implementation must be isolated because YouTube access mechanisms and restrictions can change.

Do not assume that a third-party extraction technique is equivalent to the official YouTube API.

---

# 3. YouTube Music

YouTube Music is treated as a separate provider.

Potential responsibilities include:

- search
- browse
- metadata
- albums
- artists
- playlists
- queue/next behavior
- radio/shuffle behavior
- lyrics-related discovery where technically available

The implementation must be isolated because YouTube Music request patterns differ from normal YouTube.

---

# 4. JioSaavn

Potential provider responsibilities:

- launch/home data
- top searches
- song search
- album search
- artist search
- playlist search
- song details
- album details
- playlist details
- recommendations
- radio/stations

Known reference host:

```text
www.jiosaavn.com
```

NEXXA must verify current availability before implementation.

---

# Provider Capability System

Every provider should expose a capability object.

Example:

```json
{
  "search": true,
  "track_details": true,
  "albums": true,
  "artists": true,
  "playlists": true,
  "library_import": false,
  "playback_resolution": false,
  "lyrics": false,
  "radio": false,
  "recommendations": false
}
```

The application must check capabilities before exposing a feature.

---

# Provider Errors

Map external errors to NEXXA errors.

Examples:

```text
AUTH_REQUIRED
AUTH_EXPIRED
RATE_LIMITED
NOT_FOUND
UNSUPPORTED
PROVIDER_UNAVAILABLE
PROVIDER_TIMEOUT
SOURCE_UNAVAILABLE
```

Never expose raw provider stack traces to users.
