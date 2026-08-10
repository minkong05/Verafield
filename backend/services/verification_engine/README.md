# backend/services/verification_engine

Cross-checks collected data against itself and against satellite imagery, and routes anything suspicious to a human review queue instead of passing it through silently. The most defensible piece of the system per tech.md §6.3.2 — the checks are easy to copy, the tuned thresholds are not.

## Roadmap features

- [`04-deforestation-satellite-check`](../../../docs/roadmap/04-deforestation-satellite-check.md) — before/after land-cover comparison per plot against the 31 Dec 2020 cutoff.
- [`05-five-signal-verification-engine`](../../../docs/roadmap/05-five-signal-verification-engine.md) — the Five-Point Field Check (GPS, photo geotag, land area, MPOB licence coverage, yield) plus the anomaly review queue.

## What it owns

Threshold values here are calibration data, not constants — tune against the first 400 households (tech.md §6.3.2), don't hardcode once and forget.

## Interface

Called by `backend/routes` on record sync. Reads land area from `backend/services/rules_engine`, MPOB licence/yield data from `backend/services/national_integration` (or manual entry until that ships). Writes clear/flag status via `backend/db`, which gates `backend/services/evidence_pack`.
