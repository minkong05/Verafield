# backend/services/labour_declaration

On-site collection of a signed labour/no-child-labour/land-dispute declaration and a dual-track PDPA/GDPR consent instrument, one of each per household.

## Roadmap feature

[`03-labour-rights-declaration`](../../../docs/roadmap/03-labour-rights-declaration.md)

## What it owns

Two tables under one service module, split by sensitivity: `LabourDeclaration` (labour arrangement, no-child-labour confirmation, land-dispute status) and `ConsentRecord` (identity-minimised `mykad_last4`, data-processing and credit-referral consent), both signed via `signature_method` (signature/thumbprint) and dated by a client-supplied `collected_at`/`collected_by` rather than a server timestamp — capture happens on-site and offline (`apps/field-collector`) and syncs later, and Feature 05's cross-checks compare this timestamp against other on-site signals (GPS check-in, photo geotag), so a sync-time server stamp would misfire. No computed status field and no checklist-style validation: unlike `rules_engine`, a compliance analyst reviews the declaration for completeness by hand. A household has at most one of each record for MVP.

## Interface

Called by `backend/routes` (household-scoped labour-declaration and consent endpoints). Every lookup is scoped by `mill_id` explicitly, on top of `backend/db`'s own composite-foreign-key tenant isolation (`backend/db/README.md`'s hard rule). Feeds Feature 05 (collector identity, collection date) and Feature 06 (Article 9(1)(h)/legality and FPIC evidence).
