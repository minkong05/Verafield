# backend

One API service, not five microservices — the right call for a small team pre-MVP (tech.md never proposes splitting these into independently deployed services; that's an implementation choice made here for buildability, not something drawn from the docs).

## Layout

- `routes/` — HTTP API endpoints. What `apps/field-collector` syncs to and `apps/mill-dashboard` reads from. Thin: validates input, calls a service, returns a response.
- `services/` — the actual business logic, one folder per domain: `rules_engine`, `verification_engine`, `evidence_pack`, `national_integration`, `renewal`. See each folder's README.
- `db/` — schema, migrations, and the multi-tenant isolation rules that keep one mill from ever seeing another mill's data.

## Request flow (typical)

`apps/field-collector` captures a record → syncs to a `routes/` endpoint → route calls `services/rules_engine` and/or `services/verification_engine` → result written via `db/` → once cleared, `services/evidence_pack` assembles a pack → `apps/mill-dashboard` reads the updated status through another `routes/` endpoint.

## Tech

tech.md doesn't name a specific backend language/framework — only that verification runs a "versioned rule engine plus satellite imagery comparison service... on managed cloud infrastructure with automated backups and horizontal scaling" (business_plan.md §4.5). This repo scaffolds that as **Python + FastAPI + Postgres** (see root `pyproject.toml`, `Dockerfile`, `docker-compose.yml`) so linting and local runs work now — `backend/main.py` currently exposes only a `/health` route via `routes/health.py`, everything under `services/` and `db/` is still just README notes. Revisit with a development partner at Sprint 0 if this isn't the right call long-term.
