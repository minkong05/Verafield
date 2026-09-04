# backend/services/mill

The tenant registry: one record per onboarded mill — name, MPOB licence number, postal address, email, district and state — so the `mill_id` every other table carries resolves to a named, licensed operator instead of a value the caller invented.

## Roadmap feature

[`10-mill-registry`](../../../docs/roadmap/10-mill-registry.md)

## What it owns

Mill *identity*, and only that. It establishes who a mill is; it does not establish that a caller **is** that mill — proving a credential belongs to a mill is `backend/services/auth` (Feature 11), and this service holds no credentials, hashes or tokens. It is also not tenant-scoped data: `mills` is the tenant root, so unlike every other model here it has no `mill_id` column and no `UNIQUE(id, mill_id)` (see the `Mill` docstring for why, and do not "fix" it).

Registration is analyst-mediated, not self-service — onboarding is a commercial step, so there is no sign-up flow. `mpob_licence_number` is unique, which is the anti-duplicate-tenant guard; it is the *mill's own* licence and unrelated to `NationalSystemsLookup.mpob_licence_number` (Feature 08), which is the *smallholder household's*. `is_active` revokes a mill's access without deleting it; rows are never deleted, and both foreign keys pointing here are RESTRICT rather than CASCADE so a delete can never take a five-year evidence trail with it.

## Interface

Called by `backend/routes/mill.py`, and by `backend/routes/dependencies.py`'s `validate_mill`/`authorize_mill`, which refuse an unregistered `mill_id` ahead of every mill-scoped route in Features 01–09. Unlike every sibling service, its lookups are keyed on `mills.id` directly rather than filtered by `mill_id` — here that column *is* the tenant key.
