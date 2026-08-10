# Feature 04 — Deforestation Satellite Check

## Summary

A satellite-imagery comparison proving that a plot of land has not been deforested since 31 December 2020, satisfying the "deforestation-free" definition in Article 2(13).

## Why it exists

Article 3(a) prohibits placing relevant products on the market unless they are deforestation-free, and Article 2(13) defines that as: produced on land not subject to deforestation after 31 December 2020. Article 9(1)(g) requires "adequately conclusive and verifiable information" proving this per plot. This cannot be inferred from ownership documents or national registries — it requires an actual before/after land-cover comparison against the plot's exact geolocation.

## Who uses it

- **GIS specialist (contracted, Months 1–6)**: manually reviews every comparison alongside the system's output during the calibration period.
- **Compliance analyst / CTO (from Month 6)**: owns oversight once human–system agreement stabilises and routine cases are handled automatically.
- **Field officer**: is not the direct user of this feature but supplies the plot geolocation it depends on.

## MVP scope

In scope:
- A per-plot forest three-threshold test recorded against Article 2(4)'s forest definition: area above 0.5 ha, tree height above 5 m, canopy cover above 10%, excluding land predominantly under agricultural or urban use.
- A before/after (pre- and post-31 December 2020) land-cover comparison per plot, using the plot's geolocation as the query key.
- Manual GIS specialist review of every comparison during MVP — full automation is not required to ship; tech.md §4.2 explicitly stages this as human-reviewed first, system-assisted second.
- A binary compliant/non-compliant/needs-review outcome per plot feeding the evidence pack.

Out of scope for MVP:
- Fully automated satellite analysis with no human review — this is the post-calibration state, not the MVP state.
- Continuous/real-time monitoring between annual checks — MVP checks at onboarding and at renewal (Feature 09), not continuously.

## How data is captured / technical approach

Runs as part of the Verification layer (tech.md §6.1 Layer 2): a satellite imagery comparison service that takes a plot's polygon (from Feature 02/geolocation capture) and returns a land-cover change assessment. Per tech.md's technical specifications, geolocation must use WGS84 coordinates to at least six decimal places (Article 2(28)), and polygons are mandatory above four hectares with enough points to describe the perimeter — captured below four hectares too, since buyers ask for it regardless of the legal threshold.

## Inputs / outputs

- **Input**: plot geolocation/polygon, pre- and post-2020 satellite imagery.
- **Output**: a deforestation-free determination per plot, with the underlying imagery comparison retained as evidence for Article 9(1)(g), feeding Feature 05's cross-checks and Feature 06's evidence pack.

## Dependencies

Depends on plot geolocation captured as part of Feature 01/02's on-site data collection. Feeds Feature 05 (Five-Signal Verification Engine, which cross-checks system-computed area against title area) and Feature 06 (Evidence Pack Generator, Article 9(1)(g) field).

## Success metric

Anomaly false-positive rate (tech.md §6.6 innovation accounting) — a high false-positive rate on deforestation flags destroys mill trust faster than a missed case, so this is tracked explicitly during the calibration period.
