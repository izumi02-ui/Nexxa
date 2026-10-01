# NEXXA API

**Creator:** ROHIT CHAKRABORTY (IZ / IZUMI)

## Base URL

```text
/api/v1
```

The current API router registers the following route groups:

- Health
- Search
- Albums
- Favorites
- Playlists
- History
- Recommendations

---

## Health

### Check API health

```http
GET /api/v1/health
```

Purpose: verify that the NEXXA server is running.

---

## Search

```http
GET /api/v1/search
```

Search requests are validated and handled through the NEXXA search API.

---

## Albums

Album routes are available under:

```http
/api/v1/albums
```

The album API supports the currently implemented album operations.

---

## Favorites

All favorite endpoints require authentication.

### Add favorite

```http
POST /api/v1/favorites
```

Request body:

```json
{
  "track_id": 123
}
```

Returns the created favorite.

### List favorites

```http
GET /api/v1/favorites
```

Returns favorites belonging to the authenticated user.

### Remove favorite

```http
DELETE /api/v1/favorites/{track_id}
```

Returns:

```text
204 No Content
```

If the favorite does not exist:

```text
404 Not Found
```

---

## Playlists

All playlist endpoints require authentication.

### Create playlist

```http
POST /api/v1/playlists
```

Supported playlist fields include:

```json
{
  "name": "My Playlist",
  "description": "My music",
  "artwork_url": "https://example.com/artwork.jpg",
  "is_public": false
}
```

### List playlists

```http
GET /api/v1/playlists
```

Returns playlists belonging to the authenticated user.

### Get playlist

```http
GET /api/v1/playlists/{playlist_id}
```

A playlist belonging to another user is not returned.

### Update playlist

```http
PUT /api/v1/playlists/{playlist_id}
```

### Delete playlist

```http
DELETE /api/v1/playlists/{playlist_id}
```

Returns:

```text
204 No Content
```

---

## Listening History

All history endpoints require authentication.

### Add history entry

```http
POST /api/v1/history
```

Example:

```json
{
  "track_id": 123,
  "position_ms": 45000,
  "duration_ms": 210000
}
```

### Get listening history

```http
GET /api/v1/history
```

Returns listening history belonging to the authenticated user.

### Delete one history entry

```http
DELETE /api/v1/history/{history_id}
```

Returns:

```text
204 No Content
```

### Clear listening history

```http
DELETE /api/v1/history
```

Returns:

```text
204 No Content
```

---

# Recommendations

Recommendations are generated for the authenticated user.

## Get recommendations

```http
GET /api/v1/recommendations
```

### Authentication

A valid authenticated user is required.

The recommendation endpoint receives the authenticated user's ID from the authentication dependency. The client does not supply another user's ID.

### Query parameters

#### `limit`

Number of recommendations to return.

```text
Default: 20
Minimum: 1
Maximum: 100
```

Example:

```http
GET /api/v1/recommendations?limit=20
```

### User-specific recommendation context

The recommendation system uses the authenticated user's own:

- listening history
- favorites
- playlists

The recommendation service receives:

```text
user_id = authenticated_user.id
```

This keeps recommendation generation tied to the current account.

### Cross-user isolation

Recommendation data must not be shared between users.

For example:

```text
User A
 ├── history
 ├── favorites
 ├── playlists
 └── recommendations

User B
 ├── history
 ├── favorites
 ├── playlists
 └── recommendations
```

User A's recommendation context must not be used to generate User B's recommendations.

---

# Authentication

Protected endpoints require valid authentication.

The authenticated user is resolved by the server.

Protected resources include:

- favorites
- playlists
- listening history
- recommendations

---

# Authorization

Authentication alone is not sufficient.

User-owned resources must always be scoped to the authenticated user.

A user may only access their own:

- favorites
- playlists
- history
- recommendation context
- imports
- downloads
- provider connections
- settings

---

# Validation

Every external request must be validated.

Validation includes:

- request body validation
- query parameter validation
- path parameter validation
- authentication validation
- ownership validation

The recommendations endpoint currently validates `limit` with:

```text
1 <= limit <= 100
```

---

# Errors

Use consistent, machine-readable error responses.

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

Common HTTP statuses include:

```text
200 OK
201 Created
204 No Content
401 Unauthorized
404 Not Found
422 Unprocessable Entity
```

---

# Pagination

Large collections should use pagination as their dataset grows.

Relevant collection APIs include:

- search
- playlists
- library
- history
- favorites
- recommendations
- import results

Pagination should be added consistently without breaking existing API contracts.

---

# Current Registered API Groups

The backend currently registers:

```text
/api/v1/health
/api/v1/search
/api/v1/albums
/api/v1/favorites
/api/v1/playlists
/api/v1/history
/api/v1/recommendations
```

---

# Planned API Groups

The following API areas are documented for future implementation and should not be treated as currently implemented unless their routes are registered:

```text
/api/v1/auth
/api/v1/users
/api/v1/tracks
/api/v1/artists
/api/v1/library
/api/v1/import
/api/v1/player
/api/v1/downloads
/api/v1/lyrics
/api/v1/radio
/api/v1/settings
```

---

# API Design Rules

1. Keep API paths under `/api/v1`.
2. Require authentication for user-owned resources.
3. Scope user data by authenticated user ID.
4. Validate all external input.
5. Return appropriate HTTP status codes.
6. Do not expose internal stack traces.
7. Keep recommendation data isolated per account.
8. Keep documentation synchronized with implemented routes.
9. Do not document planned endpoints as implemented.
10. Preserve backward compatibility when extending the API.
