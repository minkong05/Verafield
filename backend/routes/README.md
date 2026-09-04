# backend/routes

HTTP API endpoints — the only thing either app (`apps/field-collector`, `apps/mill-dashboard`) talks to. No app reaches into `services/` or `db/` directly.

## Expected endpoint groups (one per consuming app need)

- **Auth endpoints** — `POST /auth/login` exchanges an email/password for a bearer token; `/auth/me` and `/auth/change-password` act on the caller's own account. Admin-only account and mill administration lives under `/users` and `/mills`.
- **Sync endpoints** (used by `apps/field-collector`) — accept household/plot/document/consent records captured offline, hand off to `services/rules_engine` and `services/verification_engine`.
- **Status endpoints** (used by `apps/mill-dashboard`) — return a mill's own supplier cleared/pending/frozen status ([`07-supplier-mill-dashboard`](../../docs/roadmap/07-supplier-mill-dashboard.md)), scoped by the requesting mill's identity.
- **Evidence pack endpoints** (used by `apps/mill-dashboard`) — trigger/download a generated pack from `services/evidence_pack`.

## Rule

Routes stay thin: validate the request, delegate to a service, shape the response. Business logic (rule lookups, five-signal checks, pack assembly) belongs in `services/`, not here.

## Authorization

Every mill-scoped router carries `dependencies=[Depends(authorize_mill)]` (`dependencies.py`), so the check runs before any route body. `mill_id` stays in the path as the addressing scheme — it is how an admin names which mill to act on — while the bearer token is the authority over it: a mill user may only pass its own, and is refused from the token alone before the registry is consulted, so it cannot learn which mill ids are registered. `rules_engine.py` is the exception, carrying the dependency per-route because it also serves the global rulebook lookup, which takes `get_current_user` instead (any principal, no mill scoping). `GET /health` is the only fully anonymous route.
