# backend/services/evidence_pack

The One-Click Buyer Pack, tech.md's Asset Three (§6.3.3): assembles cleared household records into the Annex II-mapped, ready-to-submit evidence file (PDF + GeoJSON) per shipment batch.

## Roadmap feature

[`06-evidence-pack-generator`](../../../docs/roadmap/06-evidence-pack-generator.md)

## What it owns

Only assembly and formatting — it reads already-verified records, it never re-collects or re-verifies. Refuses to generate a pack if any household in the batch has an unresolved flag from `verification_engine`.

## Interface

Triggered via `backend/routes` (from `apps/mill-dashboard` or on `backend/services/renewal`'s schedule). Reads cleared records from `backend/db`. Its output updates the status `apps/mill-dashboard` displays.
