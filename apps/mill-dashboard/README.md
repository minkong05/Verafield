# apps/mill-dashboard

The web app a mill's procurement/sustainability staff use to see their own suppliers' compliance status and download evidence packs. Part of tech.md's "Output" layer (§6.1, Table 38), scoped here to the one deployable app that implements the mill-facing half of it.

## Roadmap features this implements

- [`07-supplier-mill-dashboard`](../../docs/roadmap/07-supplier-mill-dashboard.md) — live cleared / pending / frozen status per supplier, strictly isolated per mill (a mill only ever sees its own suppliers).

Evidence pack generation and renewal scheduling themselves are backend jobs (`backend/services/evidence_pack`, `backend/services/renewal`) — this app only displays their output and lets a mill trigger/download a pack, it doesn't generate one itself.

## Talks to

`backend/routes` — reads status and evidence-pack data. No direct database or service access.

## Indicative tech (not finalized)

Not yet specified in tech.md beyond "document generation service and API" for the layer as a whole — a plain server-rendered or SPA web app is enough for MVP. Confirmed with a development partner at Sprint 0.

## Non-goals

No cross-mill visibility, ever — multi-tenant isolation is enforced in `backend/db`, not just hidden in the UI.
