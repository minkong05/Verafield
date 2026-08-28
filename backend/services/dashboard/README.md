# backend/services/dashboard

Read-only aggregation: computes each of a mill's households' current compliance status — cleared, pending, or frozen — from records Features 01, 05, and 06 already wrote. No new table, no writes, nothing recomputed and stored; every call re-derives status from the latest rows.

## Roadmap feature

[`07-supplier-mill-dashboard`](../../../docs/roadmap/07-supplier-mill-dashboard.md)

## What it owns

The mill-facing status view only — not a data source in its own right. `pending` is the default for any household with no cleared/frozen signal yet (a household is visible here from the moment `gap_assessment.service.create_household` runs, even before a `GapAssessment` exists). `frozen` looks only at Feature 05's `FieldVerificationCheck`/`YieldLicenceCheck` (not Feature 04's `DeforestationCheck`, and not Feature 09 renewal, which isn't implemented yet) and takes priority over `cleared` so a stale evidence pack never masks a newly-raised flag. `cleared` means "an `EvidencePack` exists covering this household" — a historical fact about what Feature 06 produced, deliberately not the same question as `verification_engine.service.household_is_cleared` (Feature 06's forward-looking "may a pack be generated right now" gate), which can diverge from this after generation if a later re-check flips a plot back to `needs_review`.

## Interface

Called by `backend/routes/dashboard.py`. Every lookup is scoped by `mill_id` explicitly, on top of `backend/db`'s own composite-foreign-key tenant isolation (`backend/db/README.md`'s hard rule).
