# NEXXA Testing Strategy

## Unit Tests

Test:

- metadata normalization
- title matching
- artist matching
- duplicate detection
- queue operations
- provider capabilities
- import state transitions

---

# Integration Tests

Test:

- database
- API routes
- authentication
- provider adapters
- OAuth callbacks
- import pipeline
- download pipeline

---

# Import Tests

Required cases:

- empty library
- large library
- duplicate tracks
- unmatched tracks
- uncertain matches
- provider timeout
- expired OAuth token
- interrupted import
- retry
- partial failure

---

# Player Tests

Test:

- play
- pause
- seek
- next
- previous
- queue
- shuffle
- repeat
- state restoration

---

# Mobile Tests

Test:

- background playback
- notifications
- permissions
- offline mode
- rotation/layout
- low-memory behavior

---

# Definition of Done

A feature is complete only when:

- success path works
- failure path works
- tests exist
- logs are useful
- security impact is reviewed
- documentation is updated
