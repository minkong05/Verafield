# backend/services/national_integration

A compliance analyst's manually-entered snapshot of what Malaysia's SIMS, GeoSAWIT, and e-MSPO show for a household's MPOB licence number, standing in for a live read-only feed into those three systems.

## Roadmap feature

[`08-national-system-integration`](../../../docs/roadmap/08-national-system-integration.md)

## Governing rule (tech.md §6.2)

Where a national system reaches, consume it. Where it doesn't, fill the gap elsewhere in this project. This service is **read-only** by design — never writes back to SIMS/GeoSAWIT/e-MSPO, and never touches the EU's own Article 33 submission system (that stays with the EU importer).

## What it owns

`NationalSystemsLookup` — one per household for MVP (mirrors `verification_engine`'s `YieldLicenceCheck`, since an MPOB licence number is household-level, not per-plot). tech.md gives no protocol/auth/data-format detail for SIMS, GeoSAWIT, or e-MSPO and schedules the real read-only integration for Sprint 4 (M9–M12), after pilot go-live — so for MVP this mirrors the same "manual entry standing in for a live feed" pattern already used for `DeforestationCheck` (GIS-specialist imagery review) and `YieldLicenceCheck` (manually-entered MPOB licence area):

- `mpob_licence_number` / `sims_transaction_volume_kg` / `geosawit_mapping_exists` / `geosawit_reference` / `emspo_certification_status` are all entered by the analyst from what they see in the respective government portal.
- `declared_area_ha` is a snapshot of the household's total `Plot.area_ha` at lookup time, computed the same way `YieldLicenceCheck.declared_area_ha` is.
- The one cross-validation the roadmap doc scopes in — SIMS transaction volume against area-derived expected yield — is computed as `volume_yield_mismatch` and resolved to a `cleared`/`needs_review` `status` (reusing `FieldVerificationStatus`) by `service.compute_status`. GeoSAWIT mapping and e-MSPO certification status are citation-only fields with no computed mismatch, per the roadmap doc's scope ("existing mapping reuse," "certification/declaration status citation" — not cross-validation).

## Interface

Called by `backend/routes/national_integration.py`, one `POST`/`GET` pair at `/mills/{mill_id}/households/{household_id}/national-systems-lookup`. Every query scoped by `mill_id`, same defense-in-depth pattern as every other service.

**Deliberately standalone for now**: `verification_engine` and `evidence_pack` do not consume `NationalSystemsLookup` yet, even though `verification_engine/README.md` already anticipates it ("MPOB licence/yield data from `backend/services/national_integration` (or manual entry until that ships)"). Wiring `YieldLicenceCheck`/evidence-pack citations to read from this table instead of their own manual-entry fields is future work, not part of this feature's first cut.

## Implementation status

- **`NationalSystemsLookup`** — implemented. `_MAX_VOLUME_YIELD_BENCHMARK_MULTIPLE` in `service.py` is a placeholder MVP threshold, not yet calibrated against a real household cohort — same caveat as `verification_engine`'s Feature 05 thresholds.
