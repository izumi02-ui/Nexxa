# NEXXA API

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Base Version

```text
/api/v1
```

## Initial Endpoint

```http
GET /api/v1/health
```

Purpose: verify that the NEXXA server is running.

## Planned Route Groups

```text
/api/v1/auth
/api/v1/users
/api/v1/search
/api/v1/tracks
/api/v1/albums
/api/v1/artists
/api/v1/playlists
/api/v1/library
/api/v1/import
/api/v1/player
/api/v1/downloads
/api/v1/lyrics
/api/v1/radio
/api/v1/recommendations
/api/v1/settings
```

## API Principles

### Validation

Every external request must be validated.

### Errors

Use consistent, machine-readable error codes.

Example:

```json
{
  "error": {
    "code": "PROVIDER_TIMEOUT",
    "message": "The music provider did not respond in time."
  }
}
```

Do not expose internal stack traces.

### Pagination

Large lists must use pagination.

Examples:

- search
- playlists
- library
- history
- import results

### Authentication

Protected endpoints require valid authentication.

### Authorization

Authentication alone is not sufficient.

A user may only access their own:

- playlists
- favorites
- history
- imports
- downloads
- provider connections
- settings
