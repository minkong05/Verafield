# backend/services/auth

Authentication and the principal model: password hashing, token issue and decode, and the user accounts those tokens identify — so the mill a request acts as is proved by a credential rather than merely named in the URL.

## Roadmap feature

[`11-mill-authentication`](../../../docs/roadmap/11-mill-authentication.md)

## What it owns

Credentials and principals, not tenancy. Who a mill *is* belongs to `backend/services/mill` (Feature 10); this service establishes only that a caller **is** who they claim, and which of the two principal kinds they are — an admin (TAPAK staff, never bound to a mill) or a mill user (bound to exactly one). Roles *within* a mill are deliberately out of scope.

It performs no authorization itself. Deciding whether a given principal may act on a given mill is `backend/routes/dependencies.py`'s `authorize_mill`, which is where the path parameter and the credential are reconciled.

Three decisions are load-bearing and should not be quietly reversed:

- **Tokens carry `sub`/`iat`/`exp` and nothing else.** Role and `mill_id` are re-read from the database on every request, so deactivating a user or moving them between mills takes effect immediately rather than waiting out a token's lifetime, and authorization has exactly one source of truth instead of two that can disagree. The cost is one indexed primary-key lookup per request, on the session the endpoint already holds.
- **Failed logins are indistinguishable.** A wrong password, an unknown email and a deactivated account return the same status and the same body, and a lookup miss still runs an Argon2 verification against a fixed dummy hash so the response time does not become an account-enumeration oracle.
- **`get_auth_settings()` resolves lazily, not at import.** `DatabaseSettings` is read at import time in `backend/db/session.py` because the engine is built there; copying that here would make `backend.main` unimportable without `JWT_SECRET_KEY`, breaking `test_health.py`'s module-level `TestClient` and CI's anonymous `/health` probe. `jwt_secret_key` still has no default and is rejected below 32 bytes (RFC 7518 §3.2) — a shipped fallback secret is worse than a loud failure.

## Interface

Called by `backend/routes/auth.py` (login, `/me`, change-password), `backend/routes/user.py` (admin-only account administration) and `backend/routes/dependencies.py`. Also by `backend/cli.py`, which creates the first admin — `POST /users` requires an admin token, so that one account cannot come through the API.

Unlike every other service here, its queries are not scoped by `mill_id`: a principal is looked up by id or email across all tenants, and `User.mill_id` is what the lookup *establishes* rather than something it filters by.
