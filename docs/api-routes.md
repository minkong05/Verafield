# API Routes

All endpoints implemented in `backend/routes/`, registered in `backend/main.py` with no global prefix. Base URL for local dev: `http://localhost:8000`.

Multi-tenant note: `mill_id` is always a path parameter (not inferred from auth — see `CLAUDE.md`), so every URL below must be filled in with a real mill UUID. A `mill_id`/`household_id` pair that doesn't structurally belong together 404s.

---

## Health

| Method | Path | Response | Notes |
|---|---|---|---|
| GET | `/health` | `{"status": "ok"}` | No DB access. |

---

## Households (`gap_assessment` feature)

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| POST | `/mills/{mill_id}/households` | `HouseholdCreate` | `Household` (201) | — |

`HouseholdCreate` fields: `name`, `postal_address`, `email`, `district` (+ whatever else `packages/shared_types/household.py` defines).

---

## Gap Assessment

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| POST | `/mills/{mill_id}/households/{household_id}/gap-assessment` | `GapAssessmentCreate` | `GapAssessment` (201) | 404 household not found · 422 invalid checklist · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/gap-assessment` | — | `GapAssessment` | 404 household or assessment not found |

One per household.

---

## Rules Engine (Land Document Playbook)

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| GET | `/land-ownership-rules/{state}/{land_type}` | — | `LandDocumentRule` | 404 rule not found |
| POST | `/mills/{mill_id}/households/{household_id}/land-ownership-assessment` | `LandOwnershipAssessmentCreate` | `LandOwnershipAssessment` (201) | 404 household not found · 422 no matching rule · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/land-ownership-assessment` | — | `LandOwnershipAssessment` | 404 household or assessment not found |

`state`/`land_type` are the `MalaysiaState`/`LandType` enums. One assessment per household. `read_land_document_rule` has no `mill_id` — it's global reference data.

---

## Labour Declaration

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| POST | `/mills/{mill_id}/households/{household_id}/labour-declaration` | `LabourDeclarationCreate` | `LabourDeclaration` (201) | 404 household not found · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/labour-declaration` | — | `LabourDeclaration` | 404 household or declaration not found |
| POST | `/mills/{mill_id}/households/{household_id}/consent` | `ConsentRecordCreate` | `ConsentRecord` (201) | 404 household not found · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/consent` | — | `ConsentRecord` | 404 household or consent not found |

One of each per household.

---

## Verification Engine (Plots, Deforestation, Field Checks, Yield/Licence)

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| POST | `/mills/{mill_id}/households/{household_id}/plots` | `PlotCreate` | `Plot` (201) | 404 household not found |
| GET | `/mills/{mill_id}/households/{household_id}/plots` | — | `list[Plot]` | 404 household not found |
| GET | `/mills/{mill_id}/households/{household_id}/plots/{plot_id}` | — | `Plot` | 404 household or plot not found |
| POST | `/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check` | `DeforestationCheckCreate` | `DeforestationCheck` (201) | 404 household/plot not found · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check` | — | `DeforestationCheck` | 404 household/plot/check not found |
| POST | `/mills/{mill_id}/households/{household_id}/plots/{plot_id}/field-verification-check` | `FieldVerificationCheckCreate` | `FieldVerificationCheck` (201) | 404 household/plot not found · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/plots/{plot_id}/field-verification-check` | — | `FieldVerificationCheck` | 404 household/plot/check not found |
| POST | `/mills/{mill_id}/households/{household_id}/yield-licence-check` | `YieldLicenceCheckCreate` | `YieldLicenceCheck` (201) | 404 household not found · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/yield-licence-check` | — | `YieldLicenceCheck` | 404 household or check not found |

Cardinality: a household can have **many** plots; each plot has **one** deforestation check and **one** field-verification check; each household has **one** yield-licence check (covers total declared area across all its plots).

---

## Evidence Pack (Batches)

Note the prefix — batches are mill-scoped, not nested under a household (a batch can span multiple households' plots).

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| POST | `/mills/{mill_id}/batches` | `BatchCreate` | `Batch` (201) | 404 plot not found |
| GET | `/mills/{mill_id}/batches` | — | `list[Batch]` | — |
| GET | `/mills/{mill_id}/batches/{batch_id}` | — | `Batch` | 404 batch not found |
| POST | `/mills/{mill_id}/batches/{batch_id}/evidence-pack` | `EvidencePackCreate` | `EvidencePack` (201) | 404 batch not found · 422 a referenced household isn't cleared · 409 already exists |
| GET | `/mills/{mill_id}/batches/{batch_id}/evidence-pack` | — | `EvidencePack` | 404 batch or pack not found |

`create_evidence_pack`'s 422 is the gate from `verification_engine.service.household_is_cleared` — it refuses if any household referenced by the batch's plots has an unresolved flag or a `LandOwnershipAssessment` that isn't `cleared`.

---

## Dashboard (read-only)

| Method | Path | Response | Notes |
|---|---|---|---|
| GET | `/mills/{mill_id}/dashboard` | `list[MillDashboardSupplier]` | No writes; pure aggregation over Gap Assessment / Field Verification / Evidence Pack / Renewal data. Each entry has a `status`: `cleared` / `pending` / `frozen`. |

---

## National Integration

| Method | Path | Request body | Response | Errors |
|---|---|---|---|---|
| POST | `/mills/{mill_id}/households/{household_id}/national-systems-lookup` | `NationalSystemsLookupCreate` | `NationalSystemsLookup` (201) | 404 household not found · 409 already exists |
| GET | `/mills/{mill_id}/households/{household_id}/national-systems-lookup` | — | `NationalSystemsLookup` | 404 household or lookup not found |

Analyst-entered stand-in for SIMS/GeoSAWIT/e-MSPO, keyed on MPOB licence number. One per household.

---

## Renewal (read-only)

| Method | Path | Response | Notes |
|---|---|---|---|
| GET | `/mills/{mill_id}/households/{household_id}/renewal-status` | `RenewalStatus` | 404 household not found |
| GET | `/mills/{mill_id}/renewal-status` | `list[RenewalStatus]` | All households for the mill |

`renewal_due_at` is one year (leap-day-safe) from the household's most recent `EvidencePack.generated_at`; `lapsed` is `true` once that date has passed. No new writes — re-running the evidence-pack endpoint un-lapses a household.

---

## Cross-cutting error conventions

- **404** — a path-referenced resource (mill/household/plot/batch/rule/record) doesn't exist, or exists under a different mill.
- **409** — the target already exists (most domain entities are capped at one row per household/plot for MVP).
- **422** — the payload is structurally valid JSON but fails a domain rule (e.g. checklist doesn't match expected categories, no matching land document rule, household not yet clearable for a pack).
- Every error body is FastAPI's standard `{"detail": "<message>"}` shape.
- Unhandled/unexpected exceptions fall through to FastAPI's default `500 {"detail": "Internal Server Error"}` — the underlying Python message is not exposed to the client in that case.
