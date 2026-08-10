# backend/services/rules_engine

The Land Document Playbook: a versioned rule library that, for a given state and land type, returns exactly which documents satisfy Article 9(1)(h) — and what to do when the ideal document doesn't exist.

## Roadmap feature

[`02-land-ownership-verification`](../../../docs/roadmap/02-land-ownership-verification.md)

## What it owns

Core, in-house IP per tech.md §6.3.1 and §4.7 — never outsourced. MVP scope is Sabah and Sarawak only; no Peninsular Malaysia rules yet. Every rule is versioned, and every household record must store which rule version it was assessed under — that's what makes a later audit possible.

## Interface

Called by `backend/routes` (sync endpoint, on land-document submission) and by `backend/services/verification_engine` (to check declared land area against the title's stated area). Reads/writes via `backend/db`.
