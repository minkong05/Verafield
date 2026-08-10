# packages/shared_types

Data models and schemas shared between `apps/field-collector`, `apps/mill-dashboard`, and `backend/` — so a household/plot/document/evidence-pack record has exactly one shape, defined once, not re-declared per app.

## Why this exists

`apps/field-collector` captures records offline and syncs them to `backend/routes`, which validates against these same shapes; `apps/mill-dashboard` reads status shaped by these same models. Without a shared package, the mobile app, the dashboard, and the backend would each maintain their own copy of "what a household record looks like," and they will drift.

## Expected contents

Type/schema definitions mirroring `backend/db`'s core entities (Household, Plot, Document, Consent, VerificationResult, EvidencePack) — not the database schema itself, just the wire/API shape.

## Depends on

Nothing — this is the lowest-level package. Everything else depends on it.
