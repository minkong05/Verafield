# TAPAK

EUDR upstream evidence-preparation service for independent oil-palm smallholders in Sabah and Sarawak, Malaysia. See `docs/business_plan.md` for the full pitch and `docs/tech.md` for the technical-feasibility writeup this skeleton is built from.

Layout is a standard `apps/` + `backend/` + `packages/` monorepo shape: the two things staff and mills actually run, one API service behind them, and shared types between the two. tech.md's own 5-layer architecture table (§6.1) still exists — it's just implemented across these folders rather than named 1:1 by them; each README below says which layer it corresponds to. `apps/field-collector` (mobile) and `apps/mill-dashboard` (web) don't have a chosen stack or code yet — `backend/` does: Python, FastAPI, and Postgres, scaffolded below so linting and `docker compose up` actually work today. All of this is still easy to revisit with a development partner at Sprint 0.

## Preparation

Prerequisites: **Python 3.11+** and **Docker Desktop** (or Docker Engine + Compose plugin). For day-to-day commands, testing, dependency management, and troubleshooting once you're past first-time setup, see [`DEV.md`](DEV.md).

### 1. Create a virtual environment and install the backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the backend's runtime dependencies (FastAPI, Uvicorn, SQLAlchemy, psycopg) plus dev tools (`ruff`, `pytest`), all declared in [`pyproject.toml`](pyproject.toml).

### 2. Lint / format

```bash
ruff check .        # lint
ruff check . --fix  # lint, auto-fixing what's safe to fix
ruff format .       # format
```

Ruff's rules live under `[tool.ruff]` in `pyproject.toml` — it scans `backend/` and `packages/shared_types/` (the only Python code in the repo).

### 3. Set up environment variables

```bash
cp .env.example .env
```

Defaults are fine for local dev — edit `.env` only if you need different credentials or ports.

### 4. Run everything

```bash
docker compose up -d
```

This builds and starts two containers:

| Service | What it is | Address |
|---|---|---|
| `db` | Postgres 16 | `localhost:5432` |
| `backend` | The FastAPI API (`backend/main.py`) | `localhost:8000` |

Check it worked:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 5. Day-to-day commands

```bash
docker compose logs -f backend   # tail backend logs
docker compose ps                # what's running
docker compose down              # stop everything
docker compose down -v           # stop and wipe the Postgres volume too
docker compose up -d --build     # rebuild the backend image after a dependency change
```

`apps/field-collector` and `apps/mill-dashboard` aren't part of `docker-compose.yml` yet — they'll be added once their own stacks are chosen (see each app's README).

## Directory map

| Directory | Corresponds to (tech.md §6.1) | What it does | Roadmap features |
|---|---|---|---|
| [`apps/field-collector/`](apps/field-collector/README.md) | Layer 1 — Collection | Offline mobile app field officers use on-site | [01](docs/roadmap/01-gap-assessment-report.md), [02](docs/roadmap/02-land-ownership-verification.md), [03](docs/roadmap/03-labour-rights-declaration.md), [04](docs/roadmap/04-deforestation-satellite-check.md) |
| [`apps/mill-dashboard/`](apps/mill-dashboard/README.md) | Layer 4 — Output (mill-facing half) | Web app mills use to see their own supplier compliance status | [07](docs/roadmap/07-supplier-mill-dashboard.md) |
| [`backend/routes/`](backend/routes/README.md) | — | API endpoints both apps talk to | — |
| [`backend/services/rules_engine/`](backend/services/rules_engine/README.md) | Layer 3 — Rules | Land Document Playbook — state tenure rulebook | [02](docs/roadmap/02-land-ownership-verification.md) |
| [`backend/services/verification_engine/`](backend/services/verification_engine/README.md) | Layer 2 — Verification | Five-signal checks, satellite comparison, anomaly queue | [04](docs/roadmap/04-deforestation-satellite-check.md), [05](docs/roadmap/05-five-signal-verification-engine.md) |
| [`backend/services/evidence_pack/`](backend/services/evidence_pack/README.md) | Layer 4 — Output (pack generation) | Assembles the Annex II-mapped evidence pack per batch | [06](docs/roadmap/06-evidence-pack-generator.md) |
| [`backend/services/national_integration/`](backend/services/national_integration/README.md) | Layer 5 — Interface | Read-only SIMS / e-MSPO / GeoSAWIT integration | [08](docs/roadmap/08-national-system-integration.md) |
| [`backend/services/renewal/`](backend/services/renewal/README.md) | Layer 4 — Output (scheduling) | Annual re-verification scheduling | [09](docs/roadmap/09-annual-renewal-workflow.md) |
| [`backend/db/`](backend/db/README.md) | — | Schema, migrations, multi-tenant isolation | — |
| [`packages/shared_types/`](packages/shared_types/README.md) | — | Data models shared by both apps and the backend | — |
| [`docs/`](docs/) | — | Business plan, EUDR regulation text, tech spec, feature roadmap | [00-overview](docs/roadmap/00-overview.md) |

## Where to start

Read [`docs/roadmap/00-overview.md`](docs/roadmap/00-overview.md) for the MVP build order and dependency graph, then [`backend/README.md`](backend/README.md) for how a request actually flows through the system, before writing code in any folder above.
