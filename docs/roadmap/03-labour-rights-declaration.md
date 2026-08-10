# Feature 03 — Labour & Rights Declaration

## Summary

On-site collection of signed labour-arrangement, no-child-labour, and land-dispute declarations from each household, captured under consent that satisfies both Malaysia's PDPA and the EU's GDPR.

## Why it exists

EUDR's "relevant legislation of the country of production" test (Article 2(40)) explicitly includes labour rights (point (e)), human rights protected under international law (point (f)), and free, prior and informed consent — FPIC (point (g)). None of Malaysia's national systems (SIMS, GeoSAWIT, e-MSPO) record this today. tech.md §6.4 treats consent as a first-class requirement, not an afterthought, because the evidence collected here ultimately reaches an EU buyer and mishandling it is a real legal risk, not just a compliance formality.

## Who uses it

- **Field officer**: collects signatures/thumbprints and administers the consent instrument during the farm visit.
- **Household/smallholder**: the subject of the declaration and the consent grantor.
- **Compliance analyst**: reviews the declaration for completeness before it enters the evidence pack.

## MVP scope

In scope:
- A signed declaration set per household: labour arrangement, no-child-labour, and land-dispute status.
- A single dual-track consent instrument (PDPA + GDPR) covering: data collection and processing purpose, and a separate, explicit consent line for any credit referral (per tech.md §6.4 — consent must be specific to recipient and purpose).
- Identity minimisation: only the last four digits of a MyKad are captured — EUDR never requires a full identity document, and full ID scans are not collected under any circumstance.
- Signature/thumbprint capture suitable for a household that may not have a formal signature on file.

Out of scope for MVP:
- Any automated legal-language localisation beyond Bahasa Malaysia / English — MVP ships two languages.
- Digital identity verification against a government ID database — not required by EUDR and deliberately not built.

## How data is captured / technical approach

Captured via the same on-site collection mechanism used for other field evidence (photographs, signature/thumbprint capture, offline-tolerant since rural connectivity is intermittent) and synced once connectivity is available. Consent records and identity fragments are stored separately from the rest of the household record, given their sensitivity, and are excluded from anything that leaves Malaysia — only the assembled evidence pack (Feature 06) crosses the border, not raw consent documents.

## Inputs / outputs

- **Input**: field officer's on-site interview and the household's signature/thumbprint on the declaration and consent instrument.
- **Output**: a signed declaration record and a consent record, both timestamped and tied to the household, feeding Feature 05's cross-checks (collector identity, collection date) and Feature 06's Article 9(1)(h)/legality evidence.

## Dependencies

Follows Feature 01 (Gap Assessment) identifying that labour/consent records are missing. Feeds Feature 05 (Five-Signal Verification Engine) for collector-identity and timestamp metadata, and Feature 06 (Evidence Pack Generator) for the legality/FPIC evidence field.

## Success metric

No dedicated metric is named in tech.md for this feature specifically; track it as part of the same "percentage of households with a [documentation] gap" measure used for land ownership (tech.md §6.6), scoped to labour/consent completeness rather than tenure.
