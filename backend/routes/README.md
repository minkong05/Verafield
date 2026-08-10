# backend/routes

HTTP API endpoints — the only thing either app (`apps/field-collector`, `apps/mill-dashboard`) talks to. No app reaches into `services/` or `db/` directly.

## Expected endpoint groups (one per consuming app need)

- **Sync endpoints** (used by `apps/field-collector`) — accept household/plot/document/consent records captured offline, hand off to `services/rules_engine` and `services/verification_engine`.
- **Status endpoints** (used by `apps/mill-dashboard`) — return a mill's own supplier cleared/pending/frozen status ([`07-supplier-mill-dashboard`](../../docs/roadmap/07-supplier-mill-dashboard.md)), scoped by the requesting mill's identity.
- **Evidence pack endpoints** (used by `apps/mill-dashboard`) — trigger/download a generated pack from `services/evidence_pack`.

## Rule

Routes stay thin: validate the request, delegate to a service, shape the response. Business logic (rule lookups, five-signal checks, pack assembly) belongs in `services/`, not here.
