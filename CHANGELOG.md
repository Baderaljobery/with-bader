# Changelog

This file records changes from the point it was introduced; earlier history remains available in
Git and is not reconstructed here.

## Unreleased

### Security

- Added per-IP login/registration and per-user AI-route rate limits with 429 responses.
- Added environment-controlled open/closed registration and CORS origins.
- Delimited retrieved research text as untrusted data in extraction prompts.
- Prevented legacy generated-image paths from escaping their storage directory.
- Required every guest to reference a verified owner after a guarded data check.

### Database and reliability

- Added an Alembic baseline for historical SQL migrations 001-009 and a safe legacy adoption
  command that refuses to stamp drifted schemas.
- Added CI schema-drift detection and consistent bounded pagination for collection endpoints.
- Declared Python 3.13 support and added reproducible frontend/backend quality commands.

### Infrastructure and documentation

- Added PostgreSQL-backed GitHub Actions checks with ffmpeg, frontend checks, and image builds.
- Added production Dockerfiles, a single-server Compose stack, complete environment examples,
  and developer/deployment documentation.
