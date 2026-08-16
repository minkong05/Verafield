# backend/db

Schema, migrations, and the multi-tenant isolation rules that keep one mill from ever seeing another mill's supplier data.

## Core entities

Implemented:
- **Household** — smallholder profile (`gap_assessment`). Land type/state live on `LandOwnershipAssessment`, not `Household` itself — see below.
- **GapAssessment / GapAssessmentItem** — per-household checklist status across the six EUDR evidence categories (`gap_assessment`).
- **LandDocumentRule / LandDocumentRuleRequirement** — the versioned Land Document Playbook: global reference data (no `mill_id`) keyed on `(rule_version, state, land_type)`, returning the required documents and any hard-fail conditions (`rules_engine`).
- **LandOwnershipAssessment / LandOwnershipDocument** — per-household record of the declared state/land type, the exact `LandDocumentRule` it was resolved against, the documents collected, and the computed pass/fail/needs-follow-up outcome (`rules_engine`). One per household for MVP, mirroring `GapAssessment`.
- **LabourDeclaration** — per-household signed labour-arrangement, no-child-labour, and land-dispute declaration; `collected_at`/`collected_by` are client-supplied, not server-stamped, since capture happens on-site and offline and syncs later (`labour_declaration`). One per household for MVP.
- **ConsentRecord** — dual-track PDPA/GDPR consent instrument: identity-minimised `mykad_last4`, data-processing consent, and a separate credit-referral opt-in line, all dated by one `collected_at` (`labour_declaration`). Stored as its own table, separate from other household data, given its sensitivity. One per household for MVP.

Expected, not yet finalized:
- **Plot** — geolocation/polygon (WGS84, ≥6 decimal places per Article 2(28)), area, linked household.
- **VerificationResult** — per-signal pass/flag status from `services/verification_engine`, five-year retention (Articles 9(1), 4(3), 12(5)).
- **EvidencePack** — generated batch output from `services/evidence_pack`, plus renewal due date.
- **Mill / Supplier link** — the join enforcing that a mill only ever queries its own suppliers.

## Hard rule

Multi-tenant isolation is enforced at the query/schema level, not just hidden in `apps/mill-dashboard`'s UI — a mill's query can never structurally return another mill's rows.

## Retention

Five years per Articles 9(1), 4(3), 12(5), then deletion on a documented schedule (tech.md §6.4). Original document scans stay in Malaysia; only the assembled evidence pack a mill chooses to send crosses the border.
