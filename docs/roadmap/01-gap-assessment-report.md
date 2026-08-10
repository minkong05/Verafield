# Feature 01 — Gap Assessment Report

## Summary

A report, per household, showing exactly which EUDR-required documents and evidence exist today and which are missing. This is the MVP itself, not a preview of it — tech.md §6.6 is explicit that it should be producible by hand if the software isn't ready yet.

## Why it exists

Malaysia's national systems (SIMS, GeoSAWIT, e-MSPO) already cover product, quantity, and rough geolocation. What they don't cover — land ownership, deforestation-since-2020 proof, labour records — is exactly what disqualifies a shipment under Article 9(1)(g)-(h) and Article 3(a)-(b) of Regulation (EU) 2023/1115 if missing. A mill cannot know its real exposure until someone lists, per farm, what it's missing. Without this report, there is no way to demonstrate value before asking a mill to pay for the rest of the pipeline.

## Who uses it

- **Field officer**: fills it out during or immediately after a farm visit.
- **Mill (procurement/sustainability head)**: reads it to decide whether to engage the full service.
- **Compliance analyst**: uses it as the intake record that seeds every later feature.

## MVP scope

In scope:
- A fixed checklist per household covering the six EUDR evidence categories (product/quantity, geolocation, land ownership, deforestation proof, labour/consent, full documentation pack).
- Per-item status: present / missing / needs verification.
- Enough structure that the same checklist becomes the input record for Features 02–04 later — do not design a one-off form that has to be re-entered.

Out of scope for MVP:
- Automated scoring or risk-weighting of gaps (a human reads the list and judges).
- Any client-facing polish beyond a clean, deliverable document (PDF or spreadsheet is enough).

## How data is captured / technical approach

No app dependency required to ship this feature — it can run on a paper checklist or a simple structured form (spreadsheet or lightweight mobile form) filled in by the field officer. Once Feature 02–04's data model exists, the same checklist fields should map directly onto their structured records rather than being a separate schema, so nothing collected here is thrown away later.

## Inputs / outputs

- **Input**: field officer's on-site observation of what documents/evidence the household currently holds.
- **Output**: a per-household gap list (present/missing per evidence category), used both as a sales artifact for the mill and as the starting checklist for Features 02–04.

## Dependencies

None — this is the first feature and has no upstream dependency. It is a prerequisite for 02, 03, and 04, since it identifies which of those pipelines a given household actually needs to run.

## Success metric

Per tech.md §6.6 (Lean Startup / build-measure-learn): the hypothesis is falsified if a mill reads the gap scan, agrees the gap is real, and still declines to pay. The metric to track is conversion — how many mills that receive a Gap Assessment on a 20-household sample proceed to a paid engagement.
