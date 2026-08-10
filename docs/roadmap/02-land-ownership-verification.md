# Feature 02 — Land & Ownership Verification (Land Document Playbook)

## Summary

A maintained, versioned rulebook that, for a given state and land type, states exactly which documents satisfy Article 9(1)(h) — and what to do when the ideal document doesn't exist. This is tech.md's Asset One (§6.3.1) and is treated as core, in-house IP, never outsourced.

## Why it exists

Article 9(1)(h) requires "adequately conclusive and verifiable information that the relevant commodities have been produced in accordance with the relevant legislation of the country of production, including any arrangement conferring the right to use the respective area." In Sabah and Sarawak this is genuinely hard: land is frequently held informally or under native customary rights rather than a clean title. Without a rulebook that knows the difference between a Sabah Native Title, a Sarawak Provisional Lease, and untransferred inheritance land, a field officer has no way to know what "conclusive" evidence actually looks like for a given household — so the check either fails silently or gets fabricated.

## Who uses it

- **Field officer**: looks up the household's land type and land state to know what to collect on-site.
- **Compliance analyst**: reviews collected documents against the rule the household was assessed under.
- **Auditor (years later)**: needs to see which rule version applied to a given record.

## MVP scope

In scope:
- Rule sets for Sabah and Sarawak only (the plan's two operating states) — no Peninsular Malaysia rules for MVP.
- Coverage of the land types already named in tech.md §6.3.1: Sabah Native Title, Country Lease, Field Register; Sarawak Provisional Lease and, for native customary rights land, written permission from Jabatan Tanah dan Survei; leased land (tenancy agreement + landlord identity + landlord's title); untransferred inheritance (full co-owner list, per Article 2(40)(d)); scheme land (settler agreement + scheme number).
- A hard validation rule: leased land without a tenancy agreement fails Article 9(1)(h) outright — this cannot be silently skipped.
- Version tagging on every rule, so every household record can point to the exact rule version it was assessed under.

Out of scope for MVP:
- Peninsular Malaysia land types (Geran Mukim, Geran Negeri, etc.) — planned as a later-phase rulebook expansion, not MVP.
- Automated document classification (e.g. OCR-based document-type detection) — MVP assumes a human matches the document to the rule.

## How data is captured / technical approach

A structured rule library under version control (tech.md §6.1 Layer 3), not a static document — each rule is a queryable record keyed on state + land type, returning the required document list and any hard-fail conditions. Every land-ownership record captured in the field stores a reference to the rule version it was checked against, so a rule change later doesn't retroactively invalidate or silently reinterpret past assessments.

## Inputs / outputs

- **Input**: household's state, land type, and the documents the field officer photographs/collects on-site (title, lease, tenancy agreement, co-owner list, etc.).
- **Output**: a pass/fail/needs-follow-up status per household against Article 9(1)(h), plus the underlying document set, tagged with the rule version used.

## Dependencies

Consumes the land-type flag identified in Feature 01 (Gap Assessment). Feeds Feature 05 (Five-Signal Verification Engine), which cross-checks the declared land area against the title's stated area (signal 3), and Feature 06 (Evidence Pack Generator), which pulls the legality evidence for Article 9(1)(h).

## Success metric

Percentage of households with a tenure gap (tech.md §6.6 innovation accounting) — this is the number this feature exists to surface and eventually close.
