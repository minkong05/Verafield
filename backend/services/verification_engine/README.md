# backend/services/verification_engine

Cross-checks collected data against itself and against satellite imagery, and routes anything suspicious to a human review queue instead of passing it through silently. The most defensible piece of the system per tech.md §6.3.2 — the checks are easy to copy, the tuned thresholds are not.

## Roadmap features

- [`04-deforestation-satellite-check`](../../../docs/roadmap/04-deforestation-satellite-check.md) — before/after land-cover comparison per plot against the 31 Dec 2020 cutoff.
- [`05-five-signal-verification-engine`](../../../docs/roadmap/05-five-signal-verification-engine.md) — the Five-Point Field Check (GPS, photo geotag, land area, MPOB licence coverage, yield) plus the anomaly review queue.

## What it owns

Threshold values here are calibration data, not constants — tune against the first 400 households (tech.md §6.3.2), don't hardcode once and forget.

## Interface

Called by `backend/routes` on record sync. Reads land area from `backend/services/rules_engine`, MPOB licence/yield data from `backend/services/national_integration` (or manual entry until that ships). Writes clear/flag status via `backend/db`, which gates `backend/services/evidence_pack`.

`service.household_is_cleared` (Feature 06's generation gate) and `service.get_plot_by_id` were added to support `evidence_pack`, which imports both directly — the same cross-service-import direction this module already uses for `gap_assessment.service.get_household`. `household_is_cleared` also reads `LandOwnershipAssessment` (Feature 02, `rules_engine`'s model), a new cross-domain dependency: it's the only source of the assembled pack's Art 9(1)(h) legality-evidence field, so a household with no cleared land-ownership assessment is treated as unresolved too, not just one with a Feature 05 flag.

## Implementation status

- **`Plot`** (Feature 04) — implemented. A household's land parcel: polygon/centroid geolocation, area, and client-supplied collection metadata. One household may have many plots — the one MVP entity so far without a "one per household" constraint.
- **`DeforestationCheck`** (Feature 04) — implemented. One per plot: forest three-threshold test (Article 2(4)) plus a before/after 31 Dec 2020 land-cover comparison, recorded by a GIS specialist and resolved to a compliant/non_compliant/needs_review status by `service.compute_status`. MVP is manual review of every check, not an automated satellite-imagery integration.
- **`FieldVerificationCheck`** (Feature 05, signals 1–3) — implemented. One per plot: GNSS check-in vs. the plot's own recorded coordinates/time, photo EXIF vs. the polygon centroid, and system-computed area vs. the area stated on the title. GNSS/photo values are client-supplied (captured on-site by the field app, same as `Plot.collected_at`); resolved to a `cleared`/`needs_review` status by `service.compute_field_verification_status`.
- **`YieldLicenceCheck`** (Feature 05, signals 4–5) — implemented. One per household: MPOB licence area vs. the household's total declared plot area, and annual output ÷ area vs. the regional yield benchmark. MPOB licence area and annual output are manual entry for MVP, pending Feature 08 (`national_integration`); resolved to a `cleared`/`needs_review` status by `service.compute_yield_licence_status`.
- All Feature 05 threshold constants (`_MAX_CHECKIN_DISTANCE_M`, `_MAX_PHOTO_DISTANCE_M`, `_MAX_AREA_VARIANCE_PCT`, `_MIN_LICENCE_COVERAGE_PCT`, `_MAX_YIELD_BENCHMARK_MULTIPLE`, `_MAX_CHECKIN_TIME_DELTA`) are placeholder MVP values in `service.py`, not yet calibrated against a real household cohort — the first thing to revisit once the first 400 households (tech.md §6.3.2) are onboarded.
