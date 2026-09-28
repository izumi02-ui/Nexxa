# NEXXA Feature Research

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

This document preserves the feature and technology research that informed NEXXA's original product scope. It is a planning reference, not an implementation specification for any third-party project.

Every feature described here must be re-evaluated against current APIs, permissions, terms, reliability, and technical constraints before implementation.

## Feature Inventory

### Player

- online playback
- offline playback
- high-quality audio where the source provides it
- queue
- shuffle
- repeat
- background playback
- media and notification controls
- mini player
- local music
- sleep timer
- portrait and landscape behavior

### Discovery

- song search
- album search
- artist search
- playlist search
- trending
- suggestions
- recommendations
- radio and stations

### Library

- favorites
- playlists
- history
- albums
- artists
- local library
- cache

## Spotify Integration Research

The researched feature surface included:

- Spotify OAuth
- user playlists
- playlist tracks
- search
- track details
- featured playlists
- playlist pagination

Reference OAuth scopes included:

```text
user-read-private
user-read-email
playlist-read-private
playlist-read-collaborative
```

Reference endpoints included:

```text
/me/playlists
/playlists/{id}/tracks
/search
/tracks/{id}
/browse/featured-playlists
```

Reference API base:

```text
https://api.spotify.com/v1
```

OAuth endpoints:

```text
https://accounts.spotify.com/authorize
https://accounts.spotify.com/api/token
```

These values describe the researched integration surface and must be verified against the current provider documentation before implementation.

## JioSaavn Integration Research

The researched feature surface included operations corresponding to:

```text
webapi.getLaunchData
content.getTopSearches
webapi.get
webradio.createFeaturedStation
webradio.createArtistStation
webradio.createEntityStation
webradio.getSong
song.getDetails
playlist.getDetails
content.getAlbumDetails
search.getResults
search.getAlbumResults
search.getArtistResults
search.getPlaylistResults
reco.getreco
```

Some operations were noted as unused in the original research and should not be assumed to be required.

Reference host:

```text
www.jiosaavn.com
```

## YouTube Integration Research

The researched integration surface included a YouTube extraction/library layer for:

- search
- playlists
- metadata
- stream manifests
- audio-only stream discovery

It also referenced Google suggestions:

```text
https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=...
```

Legacy or commented alternative-service references were found during research. They should not be treated as active integrations without independent verification.

## YouTube Music Integration Research

The researched integration included YouTube Music request patterns under:

```text
https://music.youtube.com/youtubei/v1/
```

The feature surface included areas for:

- search
- browse
- player
- playlist
- album
- artist
- video
- channel
- lyrics
- next/watch queue
- radio and shuffle behavior

These request patterns are distinct from the official YouTube Data API and must be evaluated separately before implementation.

## Other Reference Components

The research also covered:

- local audio playback libraries
- metadata and tagging libraries
- lyric support
- local storage
- permissions
- network connectivity detection
- image caching
- file picking
- sharing
- URL launching
- release and version checking

## Implementation Rule

Before implementing a researched feature, verify:

- current availability
- authentication requirements
- rate limits
- applicable terms
- supported operations
- reliability
- technical constraints

A previously observed capability should never be treated as permanently available without current verification.
