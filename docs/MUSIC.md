# NEXXA Music System

## Core Player

The player must support:

- play
- pause
- seek
- previous
- next
- queue
- shuffle
- repeat
- playback state
- duration
- artwork
- track metadata

---

## Queue

Queue operations:

- add track
- remove track
- reorder
- clear
- play next
- play later
- save queue as playlist

---

## Mini Player

The mini player should remain available while navigating the application.

It should expose the most important playback controls without taking over the complete screen.

---

## Full Player

The full player should provide:

- artwork
- title
- artist
- progress
- playback controls
- queue access
- lyrics access
- additional track actions

---

## Background Playback

Android should support background playback using a platform-compatible audio architecture.

Media notification controls should expose:

- previous
- play/pause
- next

where supported.

---

## Local Music

NEXXA should support local music indexing where platform permissions and runtime capabilities allow it.

Local tracks must be represented through the same normalized internal track model where possible.

---

## Source Resolution

Metadata and playback source are separate.

```text
NEXXA Track
     |
     v
Source Resolver
     |
     +---- Spotify mapping
     +---- YouTube mapping
     +---- JioSaavn mapping
     +---- Local file
```

---

## Audio Quality

NEXXA must report actual available quality when known.

Do not display:

```text
320 kbps
```

unless the selected source actually provides that quality.

---

## Downloads

Download states:

```text
QUEUED
DOWNLOADING
COMPLETED
FAILED
CANCELLED
DELETED
```

Offline playback must use the locally stored source and metadata.

---

## History

History should record meaningful playback events.

Avoid creating thousands of duplicate history records from repeated player state updates.
