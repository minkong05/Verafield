# backend/services/evidence_pack

The One-Click Buyer Pack, tech.md's Asset Three (§6.3.3): assembles cleared household records into the Annex II-mapped, ready-to-submit evidence file (structured JSON + GeoJSON) per shipment batch.

## Roadmap feature

[`06-evidence-pack-generator`](../../../docs/roadmap/06-evidence-pack-generator.md)

## What it owns

Only assembly and formatting — it reads already-verified records, it never re-collects or re-verifies. `Batch`/`BatchPlot` compose a shipment from one or more plots (possibly spanning several households); generating a batch's `EvidencePack` refuses to proceed if any household referenced by the batch has an unresolved flag, via `backend.services.verification_engine.service.household_is_cleared`. Output is a `JSONB` Annex-II-mapped structure plus a hand-built GeoJSON `FeatureCollection` — no PDF rendering for MVP, no new spatial/document-generation dependency.

## Interface

Triggered via `backend/routes` (`/mills/{mill_id}/batches`, from `apps/mill-dashboard` or on `backend/services/renewal`'s schedule). Reads cleared records from `backend/db` (`Household`, `Plot`, `LandOwnershipAssessment`, `DeforestationCheck`) and the clearance gate from `backend/services/verification_engine`. Its output updates the status `apps/mill-dashboard` displays.

## Implementation status

- **`Batch`** (Feature 06) — implemented. A mill-scoped shipment batch: manual-entry product (description, trade name, HS code, net mass) and recipient (name/postal address/email) fields, since no `Mill` table exists yet (`mill_id` is a bare UUID everywhere in this codebase). Immutable after creation. `no_mixing_status` (Art 10(2)(j)) is computed once at creation from the batch's distinct plot count.
- **`BatchPlot`** (Feature 06) — implemented. Join row linking a `Batch` to a `Plot`, carrying that plot's harvest date for this batch (Art 9(1)(d)'s production date — not on `Plot` itself, since a plot is harvested repeatedly). The first join table in this codebase with two independent composite-FK parents.
- **`EvidencePack`** (Feature 06) — implemented. One per batch: `assembled_data` (the Annex II/Article 9(1) mapping per tech.md Table 42) and `geojson` (one `Feature` per plot in the batch), both snapshots computed once at generation time by `service.generate_evidence_pack` and never recomputed on read.
