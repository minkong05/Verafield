# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TAPAK: an EUDR (EU Deforestation Regulation) upstream evidence-preparation service for independent oil-palm smallholders in Sabah and Sarawak, Malaysia. `docs/business_plan.md` has the full pitch, `docs/tech.md` (§6) is the technical-feasibility writeup this repo is scaffolded from, `docs/eudr.md` is the consolidated regulation text, and `docs/roadmap/00-overview.md` is the MVP build order this codebase should track.

The repo is a monorepo skeleton: `apps/` (two deployables), `backend/` (one API service), `packages/` (shared types). Only `backend/` and `packages/shared_types/` have real code today — `apps/field-collector` and `apps/mill-dashboard` have no chosen stack yet, and everything under `backend/services/` and `backend/db/` is README-only (no implementation). Check each folder's README before assuming an interface exists.

## Commands

```bash
# First-time setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Lint / format (backend/ and packages/shared_types/ only — the only Python code)
ruff check .            # lint
ruff check . --fix      # lint, auto-fix
ruff format .           # format
ruff format --check .   # what CI runs

# Tests
pytest                  # backend/tests/, mirrors the module under test (e.g. routes/health.py -> tests/test_health.py)
pytest -k name          # run tests matching "name"
# Tests use FastAPI's TestClient directly — no Docker/Postgres needed for tests that exist today.

# Stack (Postgres + FastAPI backend)
docker compose up -d --build   # rebuild + start; needed after pyproject.toml/Dockerfile/backend code changes
docker compose logs -f backend
docker compose down            # stop (keeps data volume)
docker compose down -v         # stop + wipe Postgres volume
curl http://localhost:8000/health   # {"status":"ok"}
```

Before opening a PR: `ruff check .` clean, `ruff format .` run, `pytest` passes, and if `pyproject.toml`/`Dockerfile`/`backend/`/`packages/` changed, `docker compose up -d --build` still works and `/health` still returns ok. Full detail (troubleshooting Docker, adding a dependency) is in [`DEV.md`](DEV.md).

## Architecture

`docs/tech.md` §6.1 defines a 5-layer architecture (Collection, Verification, Rules, Output, Interface). This repo implements those layers across folders rather than naming folders after them 1:1 — each README states which layer it corresponds to. One API service, not five microservices, is a deliberate call for a small pre-MVP team (not something tech.md itself prescribes).

**Request flow:** `apps/field-collector` captures a record offline → syncs to a `backend/routes/` endpoint → route calls `backend/services/rules_engine` and/or `backend/services/verification_engine` (routes stay thin — validate, delegate, shape response; no business logic here) → result written via `backend/db/` → once cleared, `backend/services/evidence_pack` assembles a pack → `apps/mill-dashboard` reads updated status through another `routes/` endpoint. Neither app talks to `services/` or `db/` directly — only through `routes/`.

**`backend/services/`, one folder per domain:**
- `rules_engine` — the Land Document Playbook: versioned rules mapping state + land type to which documents satisfy Article 9(1)(h). Core in-house IP (tech.md §6.3.1/§4.7), MVP scope is Sabah/Sarawak only. Every household record stores which rule version it was assessed under.
- `verification_engine` — cross-checks collected data against itself and satellite imagery (deforestation check + the Five-Point Field Check: GPS, photo geotag, land area, MPOB licence, yield); flags anomalies to a human review queue rather than passing silently. Threshold values are calibration data tuned against real households, not hardcoded constants.
- `evidence_pack` — assembles already-verified records into the Annex II-mapped buyer pack (PDF + GeoJSON). Assembly/formatting only — never re-collects or re-verifies, and refuses to generate a pack if any household in the batch has an unresolved flag.
- `national_integration` — read-only consumption of Malaysia's SIMS/GeoSAWIT/e-MSPO, keyed on MPOB licence number. Never writes back to those systems, never touches the EU's Article 33 submission system. No other service blocks on this shipping first (verification_engine can use manual data entry as an interim).
- `renewal` — schedules annual re-verification (EUDR ongoing due-diligence obligations); re-triggers `verification_engine`/`evidence_pack`, doesn't duplicate their logic.

**`backend/db/`:** multi-tenant isolation is enforced at the query/schema level, not hidden in UI — a mill's query must never be able to structurally return another mill's rows. This is a hard rule, not a preference. Retention is five years (EUDR Articles 9(1), 4(3), 12(5)) then scheduled deletion; original document scans stay in Malaysia, only the assembled evidence pack that a mill chooses to send crosses the border.

**`packages/shared_types/`:** the lowest-level package (depends on nothing) — wire/API shapes shared by both apps and the backend, mirroring `backend/db`'s core entities (Household, Plot, Document, Consent, VerificationResult, EvidencePack) so the three codebases don't drift on what a record looks like.

**Docker build context:** the backend image builds with the **repo root** as context (not `backend/`), so it can copy `pyproject.toml`, `backend/`, and `packages/` in — keep that in mind when adding files the backend needs at build time.

## Working with the roadmap docs

`docs/roadmap/01` through `09` are ordered by dependency (see the graph in `00-overview.md`), not by priority — 01 (Gap Assessment Report) ships as a manual process before any code, 05 depends on 02–04 producing raw signals, 06 depends on 05 clearing a record, 09 depends on 06 already existing once. When implementing a feature, check its roadmap doc and upstream dependencies first. These docs are MVP-scope only (2026-12-30 EUDR deadline) — post-MVP expansion (Peninsular Malaysia rulebook, multi-mill scaling, a second commodity) is explicitly out of scope; don't pull business-plan content into implementation decisions beyond what tech.md and the roadmap already scope in.
