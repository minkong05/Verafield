# backend/services/national_integration

Read-only consumption of Malaysia's existing national systems — SIMS, GeoSAWIT, e-MSPO — keyed on MPOB licence number. Never rebuilds what already exists.

## Roadmap feature

[`08-national-system-integration`](../../../docs/roadmap/08-national-system-integration.md)

## Governing rule (tech.md §6.2)

Where a national system reaches, consume it. Where it doesn't, fill the gap elsewhere in this project. This service is **read-only** by design — never writes back to SIMS/GeoSAWIT/e-MSPO, and never touches the EU's own Article 33 submission system (that stays with the EU importer).

## Interface

Called by `backend/services/verification_engine` (licence coverage, yield benchmarking) and `backend/services/evidence_pack` (certification status as complementary evidence). No other service blocks on this one shipping first — `verification_engine` can use manual data entry as an interim measure.
