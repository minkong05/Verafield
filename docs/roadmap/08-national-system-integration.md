# Feature 08 — National System Integration (SIMS / e-MSPO / GeoSAWIT)

## Summary

A read-only interface into Malaysia's existing national systems — SIMS, GeoSAWIT, and e-MSPO — keyed on the mill's MPOB licence number, so nothing they already track is re-collected or re-typed.

## Why it exists

The governing principle in tech.md §6.2 is stated once and applied everywhere: where national systems reach, consume them; where they don't, fill the gap; never rebuild what MPOB already has. SIMS already records supplier name, MPOB licence number, and FFB transaction quantity (used at 95% among licence holders); GeoSAWIT already maps estates and smallholders; e-MSPO already holds certification and declaration status. Re-collecting any of this would waste field-officer time that is the business's scarcest and most expensive resource, and would introduce a second, potentially inconsistent copy of data a government system already treats as authoritative.

## Who uses it

- **Five-Signal Verification Engine (Feature 05)**: consumes MPOB licence coverage data for signal 4 (licence area vs. declared plots) and SIMS transaction volume for signal 5 (yield plausibility).
- **Compliance analyst**: cites GeoSAWIT mapping and e-MSPO certification status as complementary information (Article 10(2)(n)) rather than re-verifying them.

## MVP scope

In scope:
- Read-only queries against SIMS, GeoSAWIT, and e-MSPO, all keyed on MPOB licence number.
- Cross-validation only: declared volume against area-derived expected yield (SIMS), existing mapping reuse where GeoSAWIT already covers a plot (skip remapping), and certification/declaration status citation (e-MSPO).
- Explicit non-goal, stated as a boundary rather than an omission: no integration with the EU's own Article 33 due diligence information system — that stays with the EU importer.

Out of scope for MVP:
- Write access to any national system — this integration is strictly read-only, by design, to avoid duplicating systems of record.
- Automatic reconciliation logic beyond flagging a mismatch (e.g. auto-correcting a declared area against GeoSAWIT) — MVP surfaces discrepancies for Feature 05/human review rather than resolving them silently.

## How data is captured / technical approach

A read-only ingestion and cross-validation layer (tech.md §6.1 Layer 5), not a data-entry or sync mechanism — this system only ever reads from SIMS/GeoSAWIT/e-MSPO, never writes to them. Where GeoSAWIT already provides mapping for a plot, that mapping is cited directly rather than re-captured, lowering field-collection cost per household as GeoSAWIT's own coverage improves.

## Inputs / outputs

- **Input**: MPOB licence number (the join key across all three systems).
- **Output**: transaction volume (SIMS), existing plot mapping where available (GeoSAWIT), and certification/declaration status (e-MSPO), all consumed by Feature 05's cross-checks and cited in Feature 06's evidence pack as complementary information.

## Dependencies

Feature 05 depends on this for full signal-4/5 checks (MPOB licence coverage, yield benchmarking) — until this integration ships, that data can be entered manually as an interim measure, as noted in Feature 05. No other feature strictly blocks on this one.

## Success metric

No dedicated metric is named for this feature in tech.md; its effect is indirect — as GeoSAWIT reaches full coverage, per-household collection cost should fall (tech.md §6.2's explicit framing: "a business that improves when the government succeeds is a business that has chosen the right gap"), so field cost per household is the metric this integration should move over time.
