# backend/services/gap_assessment

Intake logic: creating a household record and recording its per-category checklist status (present / missing / needs_verification) across the six fixed EUDR evidence categories.

## Roadmap feature

[`01-gap-assessment-report`](../../../docs/roadmap/01-gap-assessment-report.md)

## What it owns

The intake step upstream of `rules_engine` and `verification_engine`, not a wrapper around either — it records what a field officer observed on-site; it does not evaluate document validity against a rulebook (Feature 02) or cross-check signals for fraud (Feature 05). No scoring or risk-weighting happens here — a human reads the checklist and judges, per the roadmap doc's explicit MVP scope. A household has at most one gap assessment for MVP; re-assessment/versioning is a later addition.

## Interface

Called by `backend/routes` (household + gap-assessment endpoints). Every lookup is scoped by `mill_id` explicitly, on top of `backend/db`'s own composite-foreign-key tenant isolation (`backend/db/README.md`'s hard rule).
