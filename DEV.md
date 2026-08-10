# Developer Guide

This is the day-to-day reference for working on the TAPAK backend: linting with Ruff, running the stack with Docker Compose, running tests, and what to check before opening a PR. For what the project *is* and how the folders are organized, read [`README.md`](README.md) first — this doc assumes you've already skimmed that.

Only `backend/` and `packages/shared_types/` have code today (`apps/field-collector` and `apps/mill-dashboard` don't have a chosen stack yet), so everything below is Python-focused.

## First-time setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

`pip install -e ".[dev]"` installs the app's runtime dependencies (FastAPI, Uvicorn, SQLAlchemy, psycopg) plus dev tools (`ruff`, `pytest`, `httpx`), all declared in [`pyproject.toml`](pyproject.toml). Re-run it any time `pyproject.toml`'s dependency lists change.

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

## Running tests

```bash
pytest          # run the suite
pytest -q       # quieter output
pytest -k name  # run only tests matching "name"
```

Tests live under `backend/tests/`, mirroring the module they test (e.g. `backend/routes/health.py` → `backend/tests/test_health.py`). They run against the FastAPI app directly via `TestClient` — no Docker or a real Postgres instance needed for the tests that exist today. If a test later needs the database, prefer pointing it at a throwaway Postgres (e.g. via `docker compose up -d db`) over mocking the DB — see the note in `backend/db/README.md` about not skipping real behavior at that layer.

You may see a `StarletteDeprecationWarning` about `httpx2` when running tests — that's expected on current FastAPI/Starlette versions and safe to ignore for now.

## Adding a dependency

1. Add it to `dependencies` (runtime) or `[project.optional-dependencies] dev` (dev-only) in `pyproject.toml`.
2. `pip install -e ".[dev]"` locally to pick it up in your venv.
3. `docker compose up -d --build` to bake it into the backend image.

## Before opening a PR

- [ ] `ruff check .` is clean
- [ ] `ruff format .` has been run
- [ ] `pytest` passes
- [ ] If you touched `pyproject.toml`, the `Dockerfile`, or anything under `backend/`/`packages/`: `docker compose up -d --build` succeeds and `curl localhost:8000/health` still returns `{"status":"ok"}`
