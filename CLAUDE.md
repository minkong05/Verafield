# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TAPAK: an EUDR (EU Deforestation Regulation) upstream evidence-preparation service for independent oil-palm smallholders in Sabah and Sarawak, Malaysia. `docs/business_plan.md` has the full pitch, `docs/tech.md` (§6) is the technical-feasibility writeup this repo is scaffolded from, `docs/eudr.md` is the consolidated regulation text, and `docs/roadmap/00-overview.md` is the MVP build order this codebase should track.

The repo is a monorepo skeleton: `apps/` (two deployables), `backend/` (one API service), `packages/` (shared types). Only `backend/` and `packages/shared_types/` have real code today — `apps/field-collector` and `apps/mill-dashboard` have no chosen stack yet. Under `backend/services/` and `backend/db/`, `gap_assessment` (roadmap feature 01), `rules_engine` (feature 02), `labour_declaration` (feature 03), `verification_engine` (feature 04's deforestation check plus feature 05's Five-Point Field Check), `evidence_pack` (feature 06), and `dashboard` (feature 07) are implemented end-to-end; `national_integration` and `renewal` are still README-only. Check each folder's README before assuming an interface exists.

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
# Most tests use FastAPI's TestClient directly and need no database.
# Tests that touch the DB (test_household.py, test_gap_assessment.py, test_rules_engine.py, test_labour_declaration.py, test_verification_engine.py, test_evidence_pack.py, test_evidence_pack_service.py, test_dashboard.py, test_dashboard_service.py, test_db_models.py)
# need Postgres reachable first: `docker compose up -d db`. They run against a separate
# `tapak_test` database, auto-created and migrated with real Alembic migrations (not
# Base.metadata.create_all()), so migration files themselves get exercised. Override with
# TEST_DATABASE_URL; defaults to postgresql+psycopg://tapak:tapak@localhost:5432/tapak_test.

# Migrations (Alembic) — always pass -c backend/alembic.ini, run from repo root
alembic -c backend/alembic.ini revision --autogenerate -m "describe the change"
docker compose up -d db
DATABASE_URL=postgresql+psycopg://tapak:tapak@localhost:5432/tapak alembic -c backend/alembic.ini upgrade head
# New ORM classes must be exported from backend/db/models/__init__.py or autogenerate won't see them.

# Stack (Postgres + FastAPI backend)
docker compose up -d --build   # rebuild + start; needed after pyproject.toml/Dockerfile/backend code changes
docker compose logs -f backend
docker compose down            # stop (keeps data volume)
docker compose down -v         # stop + wipe Postgres volume
curl http://localhost:8000/health   # {"status":"ok"}
# Migrations are NOT applied automatically on container start — run the alembic upgrade
# command above once after `--build` and again after every new migration lands.
```

Before opening a PR: `ruff check .` clean, `ruff format .` run, `pytest` passes, and if `pyproject.toml`/`Dockerfile`/`backend/`/`packages/` changed, `docker compose up -d --build` still works and `/health` still returns ok. If you added/changed a migration, also verify it applies cleanly against a fresh database. CI (`.github/workflows/ci.yml`) runs these same three jobs (lint, test against a Postgres service container, docker-build) on every push/PR to `main`/`dev`. Full detail (troubleshooting Docker, adding a dependency) is in [`DEV.md`](DEV.md).

## Architecture

`docs/tech.md` §6.1 defines a 5-layer architecture (Collection, Verification, Rules, Output, Interface). This repo implements those layers across folders rather than naming folders after them 1:1 — each README states which layer it corresponds to. One API service, not five microservices, is a deliberate call for a small pre-MVP team (not something tech.md itself prescribes).

**Request flow:** `apps/field-collector` captures a record offline → syncs to a `backend/routes/` endpoint → route calls `backend/services/rules_engine` and/or `backend/services/verification_engine` (routes stay thin — validate, delegate, shape response; no business logic here) → result written via `backend/db/` → once cleared, `backend/services/evidence_pack` assembles a pack → `apps/mill-dashboard` reads updated status through another `routes/` endpoint. Neither app talks to `services/` or `db/` directly — only through `routes/`.

**`backend/services/`, one folder per domain:**
- `gap_assessment` (implemented) — intake logic: creates a household record and its per-category checklist status (present / missing / needs_verification) across six fixed EUDR evidence categories. The step upstream of `rules_engine`/`verification_engine` — records what a field officer observed, doesn't evaluate document validity or cross-check for fraud. No scoring/risk-weighting for MVP; a human reads the checklist. One gap assessment per household for MVP.
- `rules_engine` (implemented) — the Land Document Playbook: versioned rules (`LandDocumentRule`, keyed on `(rule_version, state, land_type)`) mapping state + land type to which documents satisfy Article 9(1)(h), including which are hard-fail if missing. Core in-house IP (tech.md §6.3.1/§4.7), MVP scope is Sabah/Sarawak only — current version is `sabah-sarawak-v1` (`CURRENT_RULE_VERSION` in `service.py`). Submitting a household's collected documents against the matching rule produces a `LandOwnershipAssessment` with a computed `cleared`/`failed`/`needs_follow_up` status; every assessment stores the exact rule row it was resolved against for later audit. One assessment per household for MVP, same shape as `gap_assessment`.
- `labour_declaration` (implemented) — on-site `LabourDeclaration` (labour arrangement, no-child-labour confirmation, land-dispute status) and `ConsentRecord` (identity-minimised `mykad_last4`, data-processing + credit-referral consent) per household, both signed via a shared `SignatureMethod` enum. `collected_at`/`collected_by` are client-supplied, not server-stamped, since capture happens on-site and offline (`apps/field-collector`) and syncs later — Feature 05 cross-checks this timestamp against other on-site signals (GPS check-in, photo geotag), so a sync-time server stamp would misfire. No computed status field, unlike `rules_engine`: a compliance analyst reviews the declaration by hand. One of each record per household for MVP.
- `verification_engine` (implemented) — cross-checks collected data against itself and satellite imagery (deforestation check + the Five-Point Field Check: GPS, photo geotag, land area, MPOB licence, yield); flags anomalies to a human review queue rather than passing silently. Threshold values are calibration data tuned against real households, not hardcoded constants. Feature 04: `Plot` (a household's land parcel — polygon, centroid, area; one household may have *many* plots, the one MVP entity without a "one per household" constraint) and `DeforestationCheck` (one per plot — a forest three-threshold test against Article 2(4) plus a before/after 31 Dec 2020 land-cover comparison, resolved by `compute_status` to a `compliant`/`non_compliant`/`needs_review` status). MVP is manual GIS-specialist data entry, not a live satellite-imagery API integration — the specialist supplies the measurements, the system computes the outcome, same division of labour as `rules_engine`. Feature 05: `FieldVerificationCheck` (one per plot — GNSS check-in and photo-EXIF coordinates/timestamps compared against the plot's own recorded centroid/collected_at, plus system-computed area vs. the area stated on the title) and `YieldLicenceCheck` (one per household — MPOB licence area vs. the household's total declared plot area, plus annual output ÷ area vs. the regional yield benchmark); both resolved by `compute_field_verification_status`/`compute_yield_licence_status` to a `cleared`/`needs_review` status — no terminal failure state, since a mismatch always routes to human review rather than failing outright. MPOB licence area and annual output are manual entry pending Feature 08 (`national_integration`).
- `evidence_pack` (implemented) — assembles already-verified records into the Annex II-mapped buyer pack (structured JSON + GeoJSON, not a rendered PDF for MVP). Assembly/formatting only — never re-collects or re-verifies. `Batch`/`BatchPlot` compose a shipment from one or more plots (possibly spanning multiple households, since a batch is fundamentally cross-household, not a household sub-resource — routed at `/mills/{mill_id}/batches`, not nested under `/households/{household_id}/...`); `EvidencePack` (one per batch) snapshots the assembled Annex II mapping and GeoJSON once at generation time. Generation is gated by `verification_engine.service.household_is_cleared` — refuses to proceed if any household referenced by the batch's plots has an unresolved Feature 05 flag or a `LandOwnershipAssessment` that isn't `cleared` (the literal source of the pack's Art 9(1)(h) field). No `Mill` entity exists yet, so recipient contact info and batch product fields (description, trade name, HS code, net mass) are manual entry directly on `Batch`, same as `mill_id` being a bare UUID everywhere else.
- `dashboard` (implemented) — the mill-facing live status view (tech.md Table 42's second differentiator): a pure read/aggregation layer over records Features 01, 05, and 06 already wrote, no new table and no writes. Computes a `cleared`/`pending`/`frozen` `MillDashboardStatus` per household via `compute_household_status`, exposed at `GET /mills/{mill_id}/dashboard`. `pending` is the default, visible from the moment the `Household` row exists (not gated on a `GapAssessment`). `frozen` looks only at Feature 05's `FieldVerificationCheck`/`YieldLicenceCheck` being `needs_review` (not Feature 04's `DeforestationCheck`, and not Feature 09 renewal, which isn't implemented) and takes priority over `cleared`, so a stale evidence pack never masks a newly-raised flag. `cleared` means an `EvidencePack` exists covering the household — a historical fact about what Feature 06 produced, deliberately distinct from `verification_engine.service.household_is_cleared` (that function's forward-looking "may a pack be generated right now" gate, which can diverge from this after generation if a later re-check flips a plot back to `needs_review`).
- `national_integration` — read-only consumption of Malaysia's SIMS/GeoSAWIT/e-MSPO, keyed on MPOB licence number. Never writes back to those systems, never touches the EU's Article 33 submission system. No other service blocks on this shipping first (verification_engine can use manual data entry as an interim).
- `renewal` — schedules annual re-verification (EUDR ongoing due-diligence obligations); re-triggers `verification_engine`/`evidence_pack`, doesn't duplicate their logic.

**`backend/db/`:** multi-tenant isolation is enforced at the query/schema level, not hidden in UI — a mill's query must never be able to structurally return another mill's rows. This is a hard rule, not a preference. The implemented pattern (see `backend/db/models/household.py`, `gap_assessment.py`, `rules_engine.py`, `labour_declaration.py`, `plot.py`, `verification_engine.py`, `evidence_pack.py`): every *tenant* table carries its own `mill_id` column plus a `UNIQUE(id, mill_id)` constraint, and every child table's foreign key is a composite `ForeignKeyConstraint` on `(parent_id, mill_id)` rather than just `parent_id` — so a row can never be linked to a parent belonging to a different mill at the schema level, not just by convention in application code. Service functions additionally filter every query by `mill_id` explicitly (defense in depth on top of the schema constraint). Two deliberate exceptions to the rest of the pattern: `LandDocumentRule`/`LandDocumentRuleRequirement` are global reference data (the rulebook itself, not a mill's data), so they have no `mill_id` at all — don't add one; and `Plot` has no `UNIQUE(household_id, ...)` constraint, since a household can have *many* plots (every other tenant entity is capped at one row per household for MVP) — don't treat either absence elsewhere as a bug to copy. `BatchPlot` (`evidence_pack.py`) is the first join table with two independent composite-FK parents (`batches` and `plots`), since a shipment batch draws from potentially many plots across many households. Routes carry `mill_id` in the URL path (e.g. `/mills/{mill_id}/households/{household_id}/gap-assessment`), not inferred from auth context yet — that'll need revisiting once auth exists. Retention is five years (EUDR Articles 9(1), 4(3), 12(5)) then scheduled deletion; original document scans stay in Malaysia, only the assembled evidence pack that a mill chooses to send crosses the border.

**`packages/shared_types/`:** the lowest-level package (depends on nothing) — wire/API shapes shared by both apps and the backend, mirroring `backend/db`'s core entities (Household, Plot, Document, Consent, VerificationResult, EvidencePack) so the three codebases don't drift on what a record looks like. Implemented so far (features 01–07): `enums.py` (`EvidenceCategory`, `GapStatus`, `MalaysiaState`, `LandType`, `DocumentType`, `LandOwnershipStatus`, `SignatureMethod`, `DeforestationStatus`, `FieldVerificationStatus`, `NoMixingStatus`, `MillDashboardStatus`), `household.py` (`HouseholdCreate` now requires `postal_address`/`email`/`district`, added for feature 06's Annex II mapping), `gap_assessment.py`, `rules_engine.py`, `labour_declaration.py`, `plot.py`, `verification_engine.py`, `evidence_pack.py`, `dashboard.py` (`MillDashboardSupplier` — manually constructed, not `from_attributes`, since dashboard status has no single backing ORM row).

## Working with the roadmap docs

`docs/roadmap/01` through `09` are ordered by dependency (see the graph in `00-overview.md`), not by priority — 01 (Gap Assessment Report) ships as a manual process before any code, 05 depends on 02–04 producing raw signals, 06 depends on 05 clearing a record, 09 depends on 06 already existing once. When implementing a feature, check its roadmap doc and upstream dependencies first. These docs are MVP-scope only (2026-12-30 EUDR deadline) — post-MVP expansion (Peninsular Malaysia rulebook, multi-mill scaling, a second commodity) is explicitly out of scope; don't pull business-plan content into implementation decisions beyond what tech.md and the roadmap already scope in.
