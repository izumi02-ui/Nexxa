# NEXXA Backend

The NEXXA backend is the server-side foundation for the NEXXA music application.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

## Architecture

The backend is organized into separate layers for:

- API routes
- Configuration
- Database access
- Domain models
- Services
- Provider integrations
- Authentication
- Logging
- Error handling
- Validation

Provider-specific behavior must remain isolated from the core NEXXA music domain.

## Development Order

The backend is being developed according to the phases defined in:

`docs/ROADMAP.md`

Phase 1 establishes the server foundation before implementing:

- Core music functionality
- Provider integrations
- Library functionality
- Import
- Offline functionality
- Discovery
- Frontend
- Android/PWA
- Production deployment

## Phase 1 Scope

Phase 1 establishes:

- Backend project structure
- Configuration
- Environment handling
- Logging
- Health endpoint
- API versioning
- Database connection
- Database migrations
- Request validation
- Error handling
- Provider interfaces
- Authentication foundation

Later phases build on this foundation without bypassing these boundaries.