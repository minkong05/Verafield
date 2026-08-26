# Database Tables Reference

Generated from `backend/db/models/`. One example row per table, all drawn from the
same fictional story so the foreign keys actually line up:

- Mill `11111111-1111-1111-1111-111111111111`
- Household `22222222-2222-2222-2222-222222222222` — "Amir bin Yusof", Sabah smallholder
- Plot `33333333-3333-3333-3333-333333333333` — Amir's one registered parcel
- Batch `cccccccc-cccc-cccc-cccc-cccccccccccc` — a shipment the mill sends to a buyer

`mill_id` is a bare UUID everywhere — there is no `Mill` table yet. Every tenant
table also carries `id + mill_id` as a composite unique key and every child
row's FK is `(parent_id, mill_id)`, not just `parent_id`, so a row can never
structurally attach to another mill's parent. `LandDocumentRule` /
`LandDocumentRuleRequirement` are the two exceptions — global reference data
with no `mill_id`.

Most tables cap at **one row per household** (or per plot) for MVP — noted
per table below. `Plot` and `BatchPlot` are the exceptions.

---

## households

Smallholder profile. One mill per household — a smallholder supplying two mills gets two separate rows.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `22222222-2222-2222-2222-222222222222` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| name | varchar(255) | `Amir bin Yusof` |
| postal_address | varchar(500) | `Lot 42, Jalan Kampung Baru, 89000 Keningau` |
| email | varchar(255) | `amir.yusof@example.com` |
| district | varchar(255) | `Keningau` |
| created_at | timestamptz | `2026-01-10 09:00:00+08` |
| updated_at | timestamptz | `2026-01-10 09:00:00+08` |

---

## gap_assessments

Feature 01. One per household — the field officer's initial checklist pass.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `44444444-4444-4444-4444-444444444444` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| assessed_by | varchar(255) | `officer_jamal` |
| assessed_at | timestamptz | `2026-01-12 10:15:00+08` |
| created_at | timestamptz | `2026-01-12 10:15:00+08` |
| updated_at | timestamptz | `2026-01-12 10:15:00+08` |

## gap_assessment_items

One row per `EvidenceCategory` per assessment (6 fixed categories: `product_quantity`, `geolocation`, `land_ownership`, `deforestation_proof`, `labour_consent`, `documentation_pack`).

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `44444444-1111-1111-1111-000000000001` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| gap_assessment_id | uuid, FK → gap_assessments(id, mill_id) | `44444444-4444-4444-4444-444444444444` |
| category | enum(evidence_category) | `land_ownership` |
| status | enum(gap_status): `present` \| `missing` \| `needs_verification` | `present` |
| notes | text, nullable | `Native title sighted, photocopy taken` |
| created_at | timestamptz | `2026-01-12 10:15:00+08` |
| updated_at | timestamptz | `2026-01-12 10:15:00+08` |

---

## land_document_rules

Feature 02, "Land Document Playbook." **Global reference data — no `mill_id`.** One row per `(rule_version, state, land_type)`.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `55555555-5555-5555-5555-555555555555` |
| rule_version | varchar(50) | `sabah-sarawak-v1` |
| state | enum(malaysia_state): `sabah` \| `sarawak` | `sabah` |
| land_type | enum(land_type) | `native_title` |
| created_at | timestamptz | `2025-11-01 00:00:00+08` |

## land_document_rule_requirements

Which documents satisfy a given rule, and whether missing one is a hard fail. **Global reference data — no `mill_id`.**

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `55555555-1111-1111-1111-000000000001` |
| rule_id | uuid, FK → land_document_rules(id) | `55555555-5555-5555-5555-555555555555` |
| document_type | enum(document_type) | `sabah_native_title` |
| is_hard_fail | boolean | `true` |

## land_ownership_assessments

One per household. Stores the officer's declared state/land_type, the exact rule row it resolved against (for audit), and the computed outcome.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `66666666-6666-6666-6666-666666666666` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| state | enum(malaysia_state) | `sabah` |
| land_type | enum(land_type) | `native_title` |
| rule_id | uuid, FK → land_document_rules(id) | `55555555-5555-5555-5555-555555555555` |
| status | enum(land_ownership_status): `cleared` \| `failed` \| `needs_follow_up` | `cleared` |
| assessed_by | varchar(255) | `officer_jamal` |
| assessed_at | timestamptz | `2026-01-13 09:00:00+08` |
| created_at | timestamptz | `2026-01-13 09:00:00+08` |
| updated_at | timestamptz | `2026-01-13 09:00:00+08` |

## land_ownership_documents

Which documents were actually collected for an assessment.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `66666666-1111-1111-1111-000000000001` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| assessment_id | uuid, FK → land_ownership_assessments(id, mill_id) | `66666666-6666-6666-6666-666666666666` |
| document_type | enum(document_type) | `sabah_native_title` |

---

## labour_declarations

Feature 03. One per household. `collected_at`/`collected_by` are client-supplied (captured offline on-site), not server-stamped.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `77777777-7777-7777-7777-777777777777` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| labour_arrangement_description | text | `Family labour only, no hired workers` |
| no_child_labour_confirmed | boolean | `true` |
| has_land_dispute | boolean | `false` |
| land_dispute_notes | text, nullable | `NULL` |
| signature_method | enum(signature_method): `signature` \| `thumbprint` | `thumbprint` |
| collected_by | varchar(255) | `officer_jamal` |
| collected_at | timestamptz | `2026-01-14 11:30:00+08` |
| created_at | timestamptz | `2026-01-14 12:00:00+08` |
| updated_at | timestamptz | `2026-01-14 12:00:00+08` |

## consent_records

One per household. Identity-minimised — only the last 4 MyKad digits are stored.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `88888888-8888-8888-8888-888888888888` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| mykad_last4 | varchar(4) | `4821` |
| credit_referral_consent_given | boolean | `true` |
| signature_method | enum(signature_method) | `thumbprint` |
| collected_by | varchar(255) | `officer_jamal` |
| collected_at | timestamptz | `2026-01-14 11:35:00+08` |
| created_at | timestamptz | `2026-01-14 12:00:00+08` |
| updated_at | timestamptz | `2026-01-14 12:00:00+08` |

---

## plots

Feature 04. A household's land parcel. **Not capped at one per household** — a household may have many plots. `polygon` is plain JSONB `[lon, lat]` pairs, not PostGIS.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `33333333-3333-3333-3333-333333333333` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| polygon | jsonb | `[[116.401,5.334],[116.402,5.334],[116.402,5.335],[116.401,5.335]]` |
| centroid_lat | numeric(8,6) | `5.334500` |
| centroid_lon | numeric(9,6) | `116.401500` |
| area_ha | numeric(10,4) | `2.4500` |
| collected_by | varchar(255) | `officer_jamal` |
| collected_at | timestamptz | `2026-01-11 08:45:00+08` |
| created_at | timestamptz | `2026-01-11 09:00:00+08` |
| updated_at | timestamptz | `2026-01-11 09:00:00+08` |

## deforestation_checks

Feature 04. One per plot. Manual GIS-specialist entry; `status` is computed once at create time.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `99999999-9999-9999-9999-999999999999` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| plot_id | uuid, FK → plots(id, mill_id) | `33333333-3333-3333-3333-333333333333` |
| forest_area_ha | numeric(10,4) | `0.3000` |
| tree_height_m | numeric(5,2) | `4.50` |
| canopy_cover_pct | numeric(5,2) | `12.00` |
| predominantly_agricultural_or_urban | boolean | `true` |
| pre_2020_imagery_date | date | `2020-06-15` |
| post_2020_imagery_date | date | `2025-11-01` |
| forest_loss_detected | boolean | `false` |
| review_inconclusive | boolean | `false` |
| reviewed_by | varchar(255) | `gis_specialist_lin` |
| reviewed_at | timestamptz | `2026-01-16 14:00:00+08` |
| status | enum(deforestation_status): `compliant` \| `non_compliant` \| `needs_review` | `compliant` |
| created_at | timestamptz | `2026-01-16 14:00:00+08` |
| updated_at | timestamptz | `2026-01-16 14:00:00+08` |

## field_verification_checks

Feature 05 (part of the Five-Point Field Check). One per plot. Compares on-site GNSS/photo capture against the plot's own recorded centroid/area.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| plot_id | uuid, FK → plots(id, mill_id) | `33333333-3333-3333-3333-333333333333` |
| gnss_checkin_lat | numeric(8,6) | `5.334510` |
| gnss_checkin_lon | numeric(9,6) | `116.401490` |
| gnss_checkin_at | timestamptz | `2026-01-11 08:40:00+08` |
| photo_lat | numeric(8,6) | `5.334520` |
| photo_lon | numeric(9,6) | `116.401480` |
| photo_taken_at | timestamptz | `2026-01-11 08:42:00+08` |
| title_area_ha | numeric(10,4) | `2.5000` |
| checkin_mismatch | boolean | `false` |
| photo_mismatch | boolean | `false` |
| area_mismatch | boolean | `false` |
| status | enum(field_verification_status): `cleared` \| `needs_review` | `cleared` |
| recorded_by | varchar(255) | `officer_jamal` |
| recorded_at | timestamptz | `2026-01-16 15:00:00+08` |
| created_at | timestamptz | `2026-01-16 15:00:00+08` |
| updated_at | timestamptz | `2026-01-16 15:00:00+08` |

## yield_licence_checks

Feature 05 (part of the Five-Point Field Check). One per household. `declared_area_ha` is a stored snapshot (sum of the household's plots at check time), not recomputed live.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| mpob_licensed_area_ha | numeric(10,4) | `2.5000` |
| declared_area_ha | numeric(10,4) | `2.4500` |
| annual_output_kg | numeric(12,2) | `9800.00` |
| regional_yield_benchmark_kg_per_ha | numeric(10,2) | `4000.00` |
| licence_mismatch | boolean | `false` |
| yield_mismatch | boolean | `false` |
| status | enum(field_verification_status) | `cleared` |
| recorded_by | varchar(255) | `officer_jamal` |
| recorded_at | timestamptz | `2026-01-16 15:10:00+08` |
| created_at | timestamptz | `2026-01-16 15:10:00+08` |
| updated_at | timestamptz | `2026-01-16 15:10:00+08` |

---

## batches

Feature 06. A mill's shipment batch, drawing from one or more plots (possibly across households). No `Mill` table, so recipient/product fields are manual entry. Immutable after creation.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `cccccccc-cccc-cccc-cccc-cccccccccccc` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| product_description | varchar(255) | `Crude Palm Oil` |
| trade_name | varchar(255) | `CPO Grade A` |
| hs_code | varchar(20) | `1511.10` |
| net_mass_kg | numeric(12,2) | `18000.00` |
| recipient_name | varchar(255) | `EuroFats B.V.` |
| recipient_postal_address | varchar(500) | `Havenweg 12, 3115 HC Schiedam, Netherlands` |
| recipient_email | varchar(255) | `compliance@eurofats.example` |
| no_mixing_status | enum(no_mixing_status): `single_source` \| `mixed_sources` | `single_source` |
| created_by | varchar(255) | `mill_ops_wei` |
| created_at | timestamptz | `2026-02-01 10:00:00+08` |
| updated_at | timestamptz | `2026-02-01 10:00:00+08` |

## batch_plots

Join table: a plot's contribution to a batch, plus the harvest date for that contribution. **Not capped at one row per plot** — a plot can feed many batches over time.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `dddddddd-dddd-dddd-dddd-dddddddddddd` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| batch_id | uuid, FK → batches(id, mill_id) | `cccccccc-cccc-cccc-cccc-cccccccccccc` |
| plot_id | uuid, FK → plots(id, mill_id) | `33333333-3333-3333-3333-333333333333` |
| harvest_date | date | `2026-01-28` |
| created_at | timestamptz | `2026-02-01 10:00:00+08` |

## evidence_packs

Feature 06. One per batch. `assembled_data`/`geojson` are snapshots taken once at generation time, gated on every referenced household being cleared.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| batch_id | uuid, FK → batches(id, mill_id) | `cccccccc-cccc-cccc-cccc-cccccccccccc` |
| assembled_data | jsonb | `{"annex_ii": {"operator": "EuroFats B.V.", "commodity": "palm oil", ...}}` |
| geojson | jsonb | `{"type": "FeatureCollection", "features": [...]}` |
| generated_by | varchar(255) | `mill_ops_wei` |
| generated_at | timestamptz | `2026-02-01 11:00:00+08` |
| created_at | timestamptz | `2026-02-01 11:00:00+08` |

---

## national_systems_lookups

Feature 08. One per household. Analyst's manual snapshot of SIMS/GeoSAWIT/e-MSPO, keyed on MPOB licence number. Never writes back to those systems.

| Column | Type | Example |
|---|---|---|
| id | uuid, PK | `ffffffff-ffff-ffff-ffff-ffffffffffff` |
| mill_id | uuid | `11111111-1111-1111-1111-111111111111` |
| household_id | uuid, FK → households(id, mill_id) | `22222222-2222-2222-2222-222222222222` |
| mpob_licence_number | varchar(64) | `MPOB-SB-2024-118823` |
| sims_transaction_volume_kg | numeric(12,2) | `9800.00` |
| declared_area_ha | numeric(10,4) | `2.4500` |
| regional_yield_benchmark_kg_per_ha | numeric(10,2) | `4000.00` |
| volume_yield_mismatch | boolean | `false` |
| geosawit_mapping_exists | boolean | `true` |
| geosawit_reference | varchar(255), nullable | `GEOSAWIT-REF-99213` |
| emspo_certification_status | varchar(255) | `certified` |
| status | enum(field_verification_status) | `cleared` |
| looked_up_by | varchar(255) | `analyst_farah` |
| looked_up_at | timestamptz | `2026-02-02 09:00:00+08` |
| created_at | timestamptz | `2026-02-02 09:00:00+08` |
| updated_at | timestamptz | `2026-02-02 09:00:00+08` |

---

## Not yet a table

`renewal` (Feature 09) and `dashboard` (Feature 07) are pure computation over
the tables above — no new table, no writes. `renewal` derives a due date from
`evidence_packs.generated_at`; `dashboard` derives `cleared`/`pending`/`frozen`
from `evidence_packs`, `field_verification_checks`, `yield_licence_checks`,
and the renewal computation.
