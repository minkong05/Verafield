# backend/db

Schema, migrations, and the multi-tenant isolation rules that keep one mill from ever seeing another mill's supplier data.

## Core entities

Implemented:
- **Mill** — the tenant root: one row per onboarded mill, so the `mill_id` every other table carries resolves to a named, licensed operator (`mill`). The one table with **no `mill_id` column and no `UNIQUE(id, mill_id)`** — `mills.id` *is* the mill id, so children reference it with a plain single-column FK that is already the whole tenant key; there is no tenant above a mill. `households.mill_id` and `batches.mill_id` (the two tenant roots) carry that FK with **RESTRICT, not CASCADE**: deleting a mill must never cascade away a five-year evidence trail. `mpob_licence_number` is unique — the anti-duplicate-tenant guard — and is the *mill's own* licence, unrelated to `NationalSystemsLookup.mpob_licence_number`, which is the *household's*.
- **User** — an authenticating principal under one of two kinds: an admin (TAPAK staff, `mill_id IS NULL`) or a mill user bound to exactly one mill (`auth`). `ck_users_role_mill_id` enforces that pairing in the schema rather than in application code. Not a tenant table despite carrying `mill_id`: it sits alongside `mills` at the root, so no `UNIQUE(id, mill_id)` and no child composes a key with it. `password_hash` is Argon2id and is exposed by no schema; `is_active` is the revocation mechanism, re-read on every request.
- **Household** — smallholder profile (`gap_assessment`). Land type/state live on `LandOwnershipAssessment`, not `Household` itself — see below.
- **GapAssessment / GapAssessmentItem** — per-household checklist status across the six EUDR evidence categories (`gap_assessment`).
- **LandDocumentRule / LandDocumentRuleRequirement** — the versioned Land Document Playbook: global reference data (no `mill_id`) keyed on `(rule_version, state, land_type)`, returning the required documents and any hard-fail conditions (`rules_engine`).
- **LandOwnershipAssessment / LandOwnershipDocument** — per-household record of the declared state/land type, the exact `LandDocumentRule` it was resolved against, the documents collected, and the computed pass/fail/needs-follow-up outcome (`rules_engine`). One per household for MVP, mirroring `GapAssessment`.
- **LabourDeclaration** — per-household signed labour-arrangement, no-child-labour, and land-dispute declaration; `collected_at`/`collected_by` are client-supplied, not server-stamped, since capture happens on-site and offline and syncs later (`labour_declaration`). One per household for MVP.
- **ConsentRecord** — dual-track PDPA/GDPR consent instrument: identity-minimised `mykad_last4`, data-processing consent, and a separate credit-referral opt-in line, all dated by one `collected_at` (`labour_declaration`). Stored as its own table, separate from other household data, given its sensitivity. One per household for MVP.
- **Plot** — a household's land parcel: polygon (JSONB array of `[lon, lat]` pairs, WGS84 to ≥6 decimal places per Article 2(28)), centroid, `area_ha`, and client-supplied collection metadata (`verification_engine`). Deliberately **one household → many plots**, the one MVP entity so far without a `UniqueConstraint("household_id", ...)` — a smallholder can farm more than one non-contiguous parcel. Stored as plain `Numeric`/`JSONB` columns, not a PostGIS geometry type: no spatial queries are needed for MVP, only storage/round-trip toward the eventual GeoJSON evidence-pack output.
- **DeforestationCheck** — per-plot forest three-threshold test (Article 2(4)) plus a before/after 31 Dec 2020 land-cover comparison, recorded by a GIS specialist and resolved to a computed compliant/non_compliant/needs_review status (`verification_engine`). One per plot for MVP, mirroring `GapAssessment`'s "one per X" pattern. `reviewed_at` is server-stamped (unlike `Plot.collected_at`), since the specialist's review happens off-site against imagery, not on-site against GPS/photo signals.

Expected, not yet finalized:
- **VerificationResult** — per-signal pass/flag status from `services/verification_engine`'s Five-Point Field Check (Feature 05), five-year retention (Articles 9(1), 4(3), 12(5)).
- **EvidencePack** — generated batch output from `services/evidence_pack`.

## Hard rule

Multi-tenant isolation is enforced at the query/schema level, not just hidden in `apps/mill-dashboard`'s UI — a mill's query can never structurally return another mill's rows.

Three tables are documented exceptions to the `mill_id` + `UNIQUE(id, mill_id)` + composite-FK pattern, and none is a bug to copy: `LandDocumentRule`/`LandDocumentRuleRequirement` are global reference data and have no `mill_id` at all; `Plot` has no `UniqueConstraint("household_id", ...)` because a household legitimately has many plots; and `Mill`/`User` sit at the root, above any tenant.

Identity and authorization sit on top of that isolation and are separate from it: the schema stops a row attaching to the wrong tenant, `mills` makes a tenant a real identified thing, and `backend/routes/dependencies.py`'s `authorize_mill` decides whether a given caller may act as it. See `backend/services/mill` and `backend/services/auth`.

## Retention

Five years per Articles 9(1), 4(3), 12(5), then deletion on a documented schedule (tech.md §6.4). Original document scans stay in Malaysia; only the assembled evidence pack a mill chooses to send crosses the border.
