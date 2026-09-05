# Feature 11 — Mill Authentication

## Summary

Authentication for mill-scoped requests, so that the tenant a request acts as is proven by the caller's credential rather than named in the URL. Unlike every other feature in this roadmap, this one is scoped from the codebase's own needs: neither tech.md nor the regulation describes an authentication model, so nothing here is derived from a source document.

## Why it exists

Article 12(5) requires an operator's due diligence records to be retained and produced to a competent authority on request, and tech.md §6.4 commits that "each mill sees only its own supplier data." Feature 10 makes a mill identifiable and refuses invented identifiers, but identification is not authorisation — a caller still asserts which mill it is simply by naming one, so any party who learns a registered mill's identifier can read that mill's entire supplier base. Isolation that holds against accident but not against an interested party is not the confidentiality commitment §6.4 makes to a mill, and it is not a basis on which a mill can be asked to place its supplier relationships in a third-party system.

## Who uses it

- **Mill (procurement or sustainability head)**: authenticates to see its own dashboard, and cannot reach another mill's data even knowing that mill's identifier.
- **Field officer**: authenticates the field collector app's sync so captured records are attributed to a mill rather than assigned by whatever the client sends.
- **Compliance analyst (the admin principal)**: registers mills, issues and revokes the accounts that act for them, and is the only role that can do either — the same onboarding step that registers a mill under Feature 10, which until this feature had no gate on it at all.

## MVP scope

In scope:
- Per-person accounts under two principal kinds: an **admin** (TAPAK staff — the compliance analyst above, never bound to a mill) and a **mill user** (bound to exactly one). Accounts are issued at onboarding by an admin and revocable individually, without deleting the mill or rotating anything the mill's other users hold.
- Tenant **authority** derived from the authenticated caller. The identifier stays in the URL path as the addressing scheme, because an admin reaching any mill needs a way to say which one; what changes is that naming a mill no longer grants access to it. A mill user passing any identifier but its own is refused, closing the gap recorded against every mill-scoped route today.
- Closing the two oracles Feature 10 knowingly leaves open: single-mill lookup confirms whether an identifier is registered, and duplicate-licence rejection at registration confirms whether a licence is already held. Both are inherent to a registry without authentication and are inputs to this feature, not defects in that one.
- An identified actor behind the free-text operator names Features 06 and 10 currently accept on trust.

Out of scope for MVP:
- Role-based permissions **within** a mill — field officer versus procurement head, say. Every user of a mill has the same rights over that mill's data; splitting that further is a product decision no source document scopes. (The admin/mill-user split is not this: it is two kinds of principal, one of which is not a mill at all, and Feature 10 already names the analyst as the only role that registers mills.)
- Refresh tokens, self-service password reset, and rate limiting on login — named here so they are not mistaken for oversights. Access tokens are long-lived and revocation is by deactivating an account, which is checked on every request. This should be revisited before any deployment reachable beyond a controlled pilot.
- Field-officer identity as distinct from the mill it collects for — deferred for the same reason, and because the field collector app has no chosen stack yet.
- Any credential shared with SIMS, GeoSAWIT, or e-MSPO — Feature 08 is read-only against systems the service does not own, and coupling the two authentication stories would create a dependency on a national system's release schedule.

## How data is captured / technical approach

An account is issued at onboarding and exchanged for a bearer token at login, which is presented on every subsequent request and resolves to a principal. The token carries only the account id and its expiry: role and mill are re-read from the database each request, so revocation and reassignment take effect immediately rather than at the next login. This is cross-cutting rather than belonging to one of tech.md §6.1's five layers, and it displaces rather than adds to what exists: the validation Feature 10 performs ahead of each route becomes an authorization check rather than disappearing — `validate_mill` is wrapped by `authorize_mill`, which refuses a mill user naming any mill but its own before the registry is consulted at all.

## Inputs / outputs

- **Input**: a registered mill identity from Feature 10, plus a bearer token presented by the caller on each request.
- **Output**: an authenticated principal for the request, and an authorization decision over the mill the path names — consumed by every mill-scoped endpoint across Features 01–09, which no longer trust a client-supplied identifier on its own.

## Dependencies

Feature 10 must ship first — there is nothing to authenticate as until mills are registered entities. No feature blocks on this one to function, since Features 01–09 already work under Feature 10's identification; they gain confidentiality rather than capability. This should nonetheless precede any deployment reachable beyond a controlled pilot.

## Success metric

No dedicated metric is named for this feature in tech.md, and no metric in §6.6 moves when it ships. The obligation it discharges is the §6.4 commitment itself, so the measure is a negative one: no request should be able to read or write a mill's data without a credential belonging to that mill.
