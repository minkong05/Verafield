# Developer Guide

This is the day-to-day reference for working on the TAPAK backend: linting with Ruff, running the stack with Docker Compose, running tests, and what to check before opening a PR. For what the project *is* and how the folders are organized, read [`README.md`](README.md) first — this doc assumes you've already skimmed that.

The backend and shared types use Python. `apps/mill-dashboard` is a React + TypeScript application; `apps/field-collector` remains a future deployable.

## First-time setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

`pip install -e ".[dev]"` installs the app's runtime dependencies (FastAPI, Uvicorn, SQLAlchemy, psycopg) plus dev tools (`ruff`, `pytest`, `httpx`), all declared in [`pyproject.toml`](pyproject.toml). Re-run it any time `pyproject.toml`'s dependency lists change.

## Previewing the mill dashboard

The dashboard uses mock data by default, so the backend and database do not need to be running.

```bash
cd apps/mill-dashboard
npm install
npm run dev
```

Open `http://localhost:5173` in a browser. See [`apps/mill-dashboard/README.md`](apps/mill-dashboard/README.md) for live backend configuration and integration details.

## Working with Ruff

Ruff does both linting and formatting; its config lives under `[tool.ruff]` in `pyproject.toml` and applies to `backend/` and `packages/shared_types/`.

```bash
ruff check .          # lint — reports problems
ruff check . --fix    # lint — auto-fixes what's safe to fix
ruff format .         # formats files in place
ruff format --check . # formatting check without changing anything (what CI would run)
```

Run `ruff check .` and `ruff format .` before committing — a clean `ruff check .` is the bar for any change in `backend/` or `packages/shared_types/`.

**Editor integration:** the [Ruff VS Code extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) (or your editor's Ruff/LSP plugin) can run both on save so you rarely need the CLI mid-edit.

**Changing the rules:** edit `[tool.ruff.lint] select = [...]` in `pyproject.toml`. Current rule sets: `E`/`F` (pyflakes/pycodestyle correctness), `I` (import sorting), `UP` (modernize syntax for the pinned Python version), `B` (bugbear — common footguns), `SIM` (simplification). Add a set only if you're going to fix what it flags, not leave it red.

## Working with Docker Compose

`docker-compose.yml` defines two services:

| Service | Image | Purpose | Port |
|---|---|---|---|
| `db` | `postgres:16-alpine` | The database | `5432` |
| `backend` | built from `backend/Dockerfile` | The FastAPI app (`backend/main.py`) | `8000` |

The backend image is built with the **repo root** as context (not `backend/`) so it can copy `pyproject.toml`, `backend/`, and `packages/` into the image — keep that in mind if you add files the backend needs at build time.

### Everyday commands

```bash
docker compose up -d              # start both services in the background
docker compose up -d --build      # rebuild the backend image first, then start — use after
                                   # changing pyproject.toml deps, the Dockerfile, or backend/ code
                                   # you want baked into the image rather than live-mounted
docker compose ps                 # what's running and its health status
docker compose logs -f backend    # tail backend logs (Ctrl+C to stop tailing, containers keep running)
docker compose logs -f db         # tail Postgres logs
docker compose restart backend    # restart just one service
docker compose down               # stop and remove both containers (data volume persists)
docker compose down -v            # also delete the Postgres volume — full reset, you lose local data
```

### Poking at things directly

```bash
curl http://localhost:8000/health              # should return {"status":"ok"}
docker compose exec backend bash               # shell inside the running backend container
docker compose exec db psql -U tapak -d tapak  # psql prompt inside the running db container
```

### Troubleshooting

- **`Cannot connect to the Docker daemon`** — Docker Desktop isn't running. Start it (`open -a Docker` on macOS) and wait ~20–30s before retrying.
- **`port is already allocated`** — something else on your machine is already using `5432` or `8000`. Stop that process, or change the port mapping in `docker-compose.yml`.
- **Backend container won't start after a dependency change** — you need `--build`; `docker compose up -d` alone reuses the existing image.
- **Stack is in a weird state** — `docker compose down -v` then `docker compose up -d --build` for a clean slate.

## Working with Alembic

Migrations live under `backend/db/migrations/`, configured by `backend/alembic.ini` (kept inside `backend/`, not the repo root, because the Docker build context only copies `backend/` and `packages/` — see `backend/db/README.md`). Always pass `-c backend/alembic.ini` and run from the repo root so the config's relative `script_location` resolves correctly.

```bash
# generate a migration from model changes (needs a reachable Postgres — see below)
alembic -c backend/alembic.ini revision --autogenerate -m "describe the change"

# apply migrations — locally, against docker compose's db service:
docker compose up -d db
DATABASE_URL=postgresql+psycopg://tapak:tapak@localhost:5432/tapak alembic -c backend/alembic.ini upgrade head

# apply migrations inside the running backend container instead (uses the container's own DATABASE_URL from .env):
docker compose exec backend alembic -c backend/alembic.ini upgrade head
```

Migrations are **not** applied automatically on container start — run the command above once after `docker compose up -d --build` and again after every new migration lands.

**Hostname gotcha:** `.env`'s `DATABASE_URL` points at `db` (the Docker Compose network hostname), which only resolves from inside a container. Running Alembic from your host (e.g. to autogenerate a migration) needs `localhost` instead, as shown above.

Autogenerate only detects model changes if every ORM class is registered on `Base.metadata` before Alembic inspects it — `backend/db/migrations/env.py` handles this by importing `backend.db.models`, so a new entity just needs adding to `backend/db/models/__init__.py`'s exports.

## Running tests

```bash
pytest          # run the suite
pytest -q       # quieter output
pytest -k name  # run only tests matching "name"
```

Tests live under `backend/tests/`, mirroring the module they test (e.g. `backend/routes/health.py` → `backend/tests/test_health.py`). Most run against the FastAPI app directly via `TestClient` and don't need a database (`test_health.py`, `test_gap_assessment_service.py`, `test_shared_types_gap_assessment.py`).

Tests that touch the database (`test_household.py`, `test_gap_assessment.py`, `test_rules_engine.py`, `test_labour_declaration.py`, `test_verification_engine.py`, `test_db_models.py`, `test_mill.py`, `test_auth.py`, `test_authz.py`, `test_user.py`, `test_cli.py`) need a reachable Postgres, per the note in `backend/db/README.md` about not mocking the DB layer — start one with `docker compose up -d db` first. They run against a separate `tapak_test` database (auto-created on first run, isolated from whatever's in your local `tapak` dev database), migrated with real Alembic migrations rather than `Base.metadata.create_all()` so the migration files themselves are exercised, not just the ORM models. Point them elsewhere with `TEST_DATABASE_URL` if needed; it defaults to `postgresql+psycopg://tapak:tapak@localhost:5432/tapak_test`.

The shared `client` fixture is authenticated as an admin by default, so the Features 01–09 suites test what they were written to test rather than re-testing authorization in every assertion. `anon_client` (no credential) and `mill_client(mill_id)` (a mill user) exist for the cases that are about authorization; `test_authz.py` is where the mill-user path is actually exercised.

You may see a `StarletteDeprecationWarning` about `httpx2` when running tests — that's expected on current FastAPI/Starlette versions and safe to ignore for now.

## Authentication

Every endpoint except `GET /health` needs a bearer token, so a fresh database
needs one account before the API is usable. `POST /users` itself requires an
admin, so the first one comes from a CLI rather than the API:

```bash
# JWT_SECRET_KEY must be set (it is in .env.example) — it has no default in
# code, and is rejected below 32 bytes per RFC 7518 section 3.2.
python -m backend.cli create-admin --email you@tapak.my --password '<12+ chars>'

# or, to keep the secret out of your shell history:
TAPAK_ADMIN_PASSWORD='<12+ chars>' python -m backend.cli create-admin --email you@tapak.my
```

Then log in and use the token:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@tapak.my","password":"<12+ chars>"}' | jq -r .access_token)

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/mills
```

An admin can reach any mill; a mill user can reach only its own and gets 403
for any other `mill_id` — including one that isn't registered, so it can't
probe which mill ids exist. Generate a real secret per environment with
`openssl rand -hex 32`; the value in `.env.example` is for local dev only.

## Adding a dependency

1. Add it to `dependencies` (runtime) or `[project.optional-dependencies] dev` (dev-only) in `pyproject.toml`.
2. `pip install -e ".[dev]"` locally to pick it up in your venv.
3. `docker compose up -d --build` to bake it into the backend image.

## Before opening a PR

- [ ] `ruff check .` is clean
- [ ] `ruff format .` has been run
- [ ] `pytest` passes
- [ ] If you touched `pyproject.toml`, the `Dockerfile`, or anything under `backend/`/`packages/`: `docker compose up -d --build` succeeds and `curl localhost:8000/health` still returns `{"status":"ok"}`
- [ ] If you added or changed a migration: `docker compose down -v && docker compose up -d --build`, then `docker compose exec backend alembic -c backend/alembic.ini upgrade head` succeeds against a fresh database
