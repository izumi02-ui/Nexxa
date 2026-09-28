# BlackHole Reference Inventory

This document records the feature and technology inventory researched from the BlackHole Music project.

It is a reference document for NEXXA, not a copy of BlackHole implementation.

---

# Feature Inventory

## Player

- online playback
- offline playback
- high-quality audio where the source provides it
- queue
- shuffle
- repeat
- background playback
- media/notification controls
- mini player
- local music
- sleep timer
- portrait/landscape behavior

## Discovery

- song search
- album search
- artist search
- playlist search
- trending
- suggestions
- recommendations
- radio/stations

## Library

- favorites
- playlists
- history
- albums
- artists
- local library
- cache

## Spotify

The researched implementation included:

- Spotify OAuth
- user playlists
- playlist tracks
- search
- track details
- featured playlists
- playlist pagination

Reference OAuth scopes observed:

```text
user-read-private
user-read-email
playlist-read-private
playlist-read-collaborative
```

Reference endpoints observed included:

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

---

# JioSaavn

The researched implementation included operations corresponding to:

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

Some source comments indicated certain operations were not currently used.

Reference host:

```text
www.jiosaavn.com
```

---

# YouTube

The researched implementation used a YouTube extraction/library layer for:

- search
- playlists
- metadata
- stream manifests
- audio-only stream discovery

It also referenced Google suggestions:

```text
https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=...
```

Legacy/commented Invidious references were observed in the source but must not be treated as active provider integrations without verification.

---

# YouTube Music

The researched implementation contained YouTube Music internal request patterns under:

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
- radio/shuffle behavior

These are not the same thing as using the official YouTube Data API.

---

# Other Reference Components

The researched project also contained:

- local audio playback libraries
- metadata/tagging libraries
- lyric support
- local storage
- permissions
- network connectivity detection
- image caching
- file picking
- sharing
- URL launching
- GitHub release/version checking

---

# NEXXA Rule

Every reference feature must be re-evaluated before implementation.

For each provider verify:

- current availability
- authentication
- rate limits
- terms
- supported operations
- reliability
- technical constraints

Never assume that a feature observed in BlackHole remains officially supported upstream.
