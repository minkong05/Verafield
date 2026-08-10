# apps/field-collector

The offline-first mobile app field officers carry on-site: GNSS tracks, plot polygons, document photography, signatures/thumbprints, consent capture. Must work with no signal in rural Sabah/Sarawak and sync once connectivity returns. This is tech.md's "Collection" layer (§6.1, Table 38), scoped here to the one deployable app that implements it.

## Roadmap features this implements

- [`01-gap-assessment-report`](../../docs/roadmap/01-gap-assessment-report.md) — the on-site checklist of present/missing documents.
- [`02-land-ownership-verification`](../../docs/roadmap/02-land-ownership-verification.md) — photographing/collecting land documents, looked up against `backend/services/rules_engine`.
- [`03-labour-rights-declaration`](../../docs/roadmap/03-labour-rights-declaration.md) — signature/thumbprint capture and dual-track PDPA/GDPR consent.
- [`04-deforestation-satellite-check`](../../docs/roadmap/04-deforestation-satellite-check.md) — captures the plot geolocation/polygon this check runs against (the satellite comparison itself runs in `backend/services/verification_engine`).

## Talks to

`backend/routes` — syncs captured records to the API once online. Nothing here talks directly to any backend service.

## Indicative tech (not finalized)

React Native + local SQLite store + background sync queue, per tech.md §6.1. Confirmed with a development partner at Sprint 0.

## Non-goals

No farmer-facing UI (rejected in tech.md §6.7 on evidence of low active usage in comparable products). Field-officer tool only.
