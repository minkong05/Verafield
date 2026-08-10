# backend/services/renewal

Schedules and triggers annual re-verification, as EUDR's ongoing due diligence obligations require (Articles 10(4), 12(2)) — compliance isn't a one-time event.

## Roadmap feature

[`09-annual-renewal-workflow`](../../../docs/roadmap/09-annual-renewal-workflow.md)

## What it owns

Tracks each household's renewal due date (one year from its last evidence pack) and re-triggers `verification_engine` and `evidence_pack` for what needs re-checking — it does not duplicate their logic. Flips a household's dashboard status toward "frozen" if a renewal lapses.

## Interface

Runs on a schedule (calendar-driven for MVP, not continuous monitoring). Calls `backend/services/verification_engine` and `backend/services/evidence_pack`, writes status via `backend/db`.
