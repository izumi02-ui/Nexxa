# NEXXA Android / PWA

## Android Priorities

- background playback
- notification controls
- lock-screen controls where supported
- media buttons where supported
- local audio
- storage
- permissions
- responsive UI

---

# Permissions

Request permissions only when the user starts a feature requiring them.

Do not request every permission during onboarding.

---

# Performance

NEXXA must account for low-end Android devices.

Use:

- adaptive rendering
- reduced visual effects
- capped device pixel ratio where appropriate
- paused expensive effects when hidden
- pagination
- caching
- limited polling
- efficient lists

---

# PWA

Where browser capabilities permit:

- installable application
- cached application shell
- responsive player
- persistent state
- offline metadata

The application must detect unsupported browser capabilities.
