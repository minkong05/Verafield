# packages/shared_types

Data models and schemas shared between `apps/field-collector`, `apps/mill-dashboard`, and `backend/` — so a household/plot/document/evidence-pack record has exactly one shape, defined once, not re-declared per app.

## Why this exists

`apps/field-collector` captures records offline and syncs them to `backend/routes`, which validates against these same shapes; `apps/mill-dashboard` reads status shaped by these same models. Without a shared package, the mobile app, the dashboard, and the backend would each maintain their own copy of "what a household record looks like," and they will drift.

## Expected contents

Type/schema definitions mirroring `backend/db`'s core entities (Household, Plot, Document, Consent, VerificationResult, EvidencePack) — not the database schema itself, just the wire/API shape.

**Implemented so far** (Features 01–04: Gap Assessment Report, Land & Ownership Verification, Labour & Rights Declaration, Deforestation Satellite Check): `enums.py` (`EvidenceCategory`, `GapStatus`, `MalaysiaState`, `LandType`, `DocumentType`, `LandOwnershipStatus`, `SignatureMethod`, `DeforestationStatus`), `household.py`, `gap_assessment.py`, `rules_engine.py`, `labour_declaration.py`, `plot.py`, `verification_engine.py`.

## Depends on

Nothing — this is the lowest-level package. Everything else depends on it.

## Two entries worth knowing about

- `mill.py` is the only module here whose read model has **no `mill_id` field** — `Mill.id` *is* the mill id.
- `auth.py`'s `User` lists every field it exposes explicitly rather than mirroring the ORM row, so `from_attributes` can never surface `password_hash`. Don't refactor it into a wildcard.
