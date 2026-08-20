# backend/services/renewal

Tracks each household's annual renewal due date and lapsed status, as EUDR's ongoing due diligence obligations require (Articles 10(4), 12(2)) — compliance isn't a one-time event.

## Roadmap feature

[`09-annual-renewal-workflow`](../../../docs/roadmap/09-annual-renewal-workflow.md)

## What it owns

No new database table — like `dashboard` (Feature 07), this is a pure computation layer over records other features already wrote. A household's renewal due date is one year (leap-day-safe) from the `generated_at` of the most recent `EvidencePack` (Feature 06) covering any of its plots; a household with no evidence pack yet has no due date and is never lapsed. `service.household_renewal_is_lapsed` is the one function this exposes to other services.

Renewal doesn't call `verification_engine`/`evidence_pack` itself. A renewal is *enacted* by a compliance analyst or field officer re-running the existing Feature 02–06 onboarding endpoints against the same household — producing a fresh `EvidencePack`, which naturally advances `generated_at` and un-lapses the household. This service only tracks the due date and exposes it; it does not trigger or perform re-verification.

## Interface

- `GET /mills/{mill_id}/households/{household_id}/renewal-status` — a single household's due date and lapsed flag.
- `GET /mills/{mill_id}/renewal-status` — every household at a mill, for a compliance analyst tracking renewals due.

`backend/services/dashboard/service.py`'s `compute_household_status` calls `renewal.service.household_renewal_is_lapsed` directly: a household with an evidence pack whose renewal has lapsed shows `frozen`, not a stale `cleared`.
