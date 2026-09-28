# NEXXA Universal Library Import

## Objective

Allow users to connect supported music services and import their accessible library into NEXXA.

This is a major NEXXA feature.

---

# Import Flow

```text
1. Connect service
       ↓
2. Authenticate
       ↓
3. Discover library
       ↓
4. Fetch pages
       ↓
5. Normalize metadata
       ↓
6. Match tracks
       ↓
7. Detect duplicates
       ↓
8. Show preview
       ↓
9. User confirms
       ↓
10. Import
       ↓
11. Generate report
```

---

# Spotify Import

Potential categories depend on current official permissions/API access:

- playlists
- playlist tracks
- saved/liked tracks where officially accessible
- albums/library metadata where officially accessible
- artists/library metadata where officially accessible
- other user-library information supported by the API

NEXXA must not claim access to information the API does not expose.

---

# YouTube Import

Potential categories depend on the selected official integration and permissions:

- playlists
- accessible liked/saved content
- subscriptions/channels where supported
- other accessible library data

---

# YouTube Music Import

YouTube Music library functionality must be exposed only after the actual provider implementation verifies what can be reliably read.

---

# Metadata Matching

Matching signals should include:

1. provider ID
2. ISRC, when available
3. normalized title
4. normalized artist
5. album
6. duration

Potential matches must be separated from confident matches.

---

# Example

```text
Discovered: 2,430 tracks
Confident matches: 2,301
Possible matches: 82
Unmatched: 47
Duplicates: 19
```

---

# Duplicate Detection

If Spotify and YouTube contain the same logical track:

```text
NEXXA Track
   |
   +---- Spotify ID
   |
   +---- YouTube ID
```

Do not create unnecessary duplicate internal tracks.

---

# Import Preview

Before importing, show:

- total discovered
- matched
- possible
- unmatched
- duplicates
- playlists found

The user should know what will happen before confirmation.

---

# Import Safety

Import is read-oriented.

NEXXA must not automatically:

- delete external tracks
- unlike external tracks
- delete external playlists
- unsubscribe
- modify external libraries

unless a separate future feature explicitly performs a supported write operation after user confirmation.

---

# Import Reliability

Large imports must be resumable.

The system should store:

```text
ImportJob
ImportItem
status
provider
external_id
match
error
```

If an import fails at item 1,900 of 2,500, it should not necessarily restart from zero.

---

# Meaning of "Entire Library"

"Entire library" means all library data that the connected service officially exposes to NEXXA through the available permissions and the implemented provider.

NEXXA must never fake access to private or unsupported data.
