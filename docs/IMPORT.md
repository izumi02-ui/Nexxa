# NEXXA Universal Library Import

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Objective

NEXXA can connect supported music services and import the library data that those services officially make available through the applicable permissions and integrations.

## Import Flow

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

## Spotify Import

Depending on current official permissions and API access, supported categories may include:

- playlists
- playlist tracks
- saved/liked tracks
- albums and library metadata
- artists and library metadata
- other user-library information officially exposed by the API

NEXXA must never claim access to information that the current API does not expose.

## YouTube Import

Depending on the selected official integration and permissions, supported categories may include:

- playlists
- accessible liked or saved content
- subscriptions or channels where supported
- other accessible library data

## YouTube Music Import

YouTube Music library functionality should only be exposed after the provider implementation verifies what can be read reliably.

## Metadata Matching

Matching signals should include, where available:

1. provider ID
2. ISRC
3. normalized title
4. normalized artist
5. album
6. duration

Potential matches should be kept separate from confident matches.

## Example Result

```text
Discovered: 2,430 tracks
Confident matches: 2,301
Possible matches: 82
Unmatched: 47
Duplicates: 19
```

## Duplicate Detection

If multiple providers contain the same logical track:

```text
NEXXA Track
   |
   +---- Spotify ID
   |
   +---- YouTube ID
```

The normalized internal track should be reused when the match is sufficiently confident.

## Import Preview

Before importing, show:

- total discovered
- matched
- possible
- unmatched
- duplicates
- playlists found

The user should understand the result before confirming the import.

## Import Safety

Import is read-oriented. It must not automatically:

- delete external tracks
- unlike external tracks
- delete external playlists
- unsubscribe
- modify external libraries

Any future write operation must be implemented separately, explicitly supported by the provider, and confirmed by the user.

## Import Reliability

Large imports must be resumable.

Store information such as:

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

## Meaning of "Entire Library"

"Entire library" means all library data that the connected service officially exposes through the available permissions and the implemented provider.

NEXXA must never represent private or unsupported data as accessible.
