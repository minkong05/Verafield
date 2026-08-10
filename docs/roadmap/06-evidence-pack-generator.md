# Feature 06 — Evidence Pack Generator (One-Click Buyer Pack)

## Summary

Automatically assembles household-level records into the exact structure required for a due diligence statement, per shipment batch. This is tech.md's Asset Three (§6.3.3) — the step that turns collected data into a deliverable the mill can actually send to its EU buyer.

## Why it exists

Article 9(1) lists the information an operator must collect, organise, and keep for five years per relevant product; Annex II specifies the exact fields a due diligence statement must contain. A mill does not need raw field data — it needs one file, per batch, in the right structure. No competitor in this market segment currently builds this per-batch assembly step (tech.md Table 42); without it, all the evidence collected in Features 02–05 remains unusable to the mill.

## Who uses it

- **Mill (procurement/sustainability head)**: receives the assembled pack and forwards it into its own buyer relationship.
- **Compliance analyst**: triggers generation once a batch's households have cleared Feature 05, and spot-checks the output.

## MVP scope

In scope:
- Field-by-field mapping from collected data to Annex II / Article 9(1), per tech.md Table 42:
  - Product description, trade name, HS code (Art 9(1)(a)) — from the mill's batch record.
  - Quantity in kilograms of net mass (Art 9(1)(b)) — from weighbridge tickets aggregated per batch.
  - Country of production, state, district (Art 9(1)(c)) — from the plot record.
  - Geolocation of every plot in the batch, listing all plots where products are mixed (Art 9(1)(d)) — from Feature 04's polygons.
  - Production date/time range (Art 9(1)(d)) — harvest date, explicitly not the delivery date.
  - Supplier name, postal address, email (Art 9(1)(e)) — from Feature 01's household profile.
  - Recipient (mill) name, postal address, email (Art 9(1)(f)).
  - Deforestation-free evidence (Art 9(1)(g)) — from Feature 04.
  - Legality evidence (Art 9(1)(h)) — from Feature 02/03.
  - A per-batch no-mixing status flag (Art 10(2)(j)) — the differentiator tech.md calls out as something no national system produces.
- Output in a machine-readable structured format (GeoJSON for geolocation data) alongside a human-readable document, so a mill can pass it into a buyer's system without re-keying.
- Blocking generation for any household in the batch that has an unresolved Feature 05 flag.

Out of scope for MVP:
- Direct submission into the EU's Article 33 information system — TAPAK does not touch that system; the pack is handed to the mill, and the EU importer submits it.
- Multi-batch or multi-commodity templating beyond oil palm — MVP is single-commodity.

## How data is captured / technical approach

A document generation service (tech.md §6.1 Layer 4) that reads from the structured records produced by Features 01–05 rather than re-collecting anything — its only job is assembly and formatting, not data capture. Output includes both a PDF-equivalent evidence pack and structured GeoJSON data for the geolocation fields.

## Inputs / outputs

- **Input**: cleared household records (post-Feature 05) grouped into a shipment batch, plus weighbridge/mill batch records.
- **Output**: one ready-to-submit evidence file per batch, mapped field-by-field to Annex II/Article 9(1), plus the no-mixing status flag.

## Dependencies

Depends on Features 02, 03, 04 (raw evidence) and Feature 05 (clearance gate) for every household in a batch. Feeds Feature 07 (dashboard status changes to "cleared" once a pack is generated) and is re-run by Feature 09 (Annual Renewal).

## Success metric

Days from onboarding to first evidence pack accepted by a buyer (tech.md §6.6 innovation accounting) — this is the end-to-end cycle time this feature is the final step of.
