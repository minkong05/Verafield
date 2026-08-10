# Feature 07 — Supplier / Mill Compliance Dashboard

## Summary

A live view, per mill, of its own suppliers' status: cleared, pending, or frozen. No cross-mill visibility. This is the second differentiator tech.md Table 42 calls out — it lets a mill decide at the weighbridge whether to accept a delivery, rather than finding out after the fact.

## Why it exists

Article 10 requires operators to assess and manage non-compliance risk on an ongoing basis, not just at the point of a single due diligence statement. A mill buying fresh fruit bunches daily from many smallholders needs to know, in near real time, which suppliers currently have valid evidence and which don't — otherwise one undocumented farm can disqualify an entire truckload, as business context establishes is a real and costly failure mode. A static, emailed PDF pack does not support that decision; a live status view does.

## Who uses it

- **Mill (procurement staff, weekly or daily)**: checks supplier status before accepting a delivery.
- **Compliance analyst**: updates status as households move through Features 02–06 or fall out of compliance.

## MVP scope

In scope:
- Three-state status per supplier household: cleared / pending / frozen.
- Status transitions driven by the pipeline: a household enters "pending" at Feature 01, moves to "cleared" once Feature 06 successfully generates a pack covering it, and moves to "frozen" if Feature 05 raises an unresolved flag or a renewal (Feature 09) lapses.
- Strict multi-tenant isolation: a mill can see only its own suppliers. A smallholder supplying two mills appears separately in each mill's view, under separate consent records (per tech.md §6.4).

Out of scope for MVP:
- Supplier-facing (farmer-facing) access to the dashboard — MVP is mill-facing only; tech.md's design-thinking section (§6.7) explicitly rejected a farmer-facing app based on evidence of low active usage in a comparable product (Kapitani).
- Analytics, trend charts, or export tooling beyond the current status list.

## How data is captured / technical approach

Reads from the same structured records that Features 01–06 already produce — the dashboard is a view layer, not a separate data source. Multi-tenant isolation is enforced at the data-access layer, keyed on mill identity, so a query can never return another mill's supplier records regardless of application-layer bugs.

## Inputs / outputs

- **Input**: status events from Features 01 (intake), 05 (flag/clear), 06 (pack generated), and 09 (renewal due/lapsed).
- **Output**: a per-mill, per-supplier status list, refreshed as pipeline events occur.

## Dependencies

Depends on Features 01–06 emitting status changes it can display. Feature 09 (Annual Renewal) also writes to it, since a lapsed renewal must flip a supplier back to "pending" or "frozen."

## Success metric

No dedicated metric is named in tech.md for the dashboard itself; treat mill engagement with it (e.g. suppliers checked before a delivery decision) as a proxy for whether the "no cross-mill visibility, live status" design decision is actually valued, consistent with the disconfirming-evidence approach in tech.md §6.6.
