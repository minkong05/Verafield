# Feature 10 — Mill Registry (Tenant Identity)

## Summary

A registry of the mills the service is operated on behalf of — name, MPOB licence number, address, and contact — so that the `mill_id` every record is scoped by resolves to a known, identified operator instead of an arbitrary value. This is the tenant root the rest of the data model already assumes exists.

## Why it exists

tech.md §6.4 states the tenancy rule once: "Each mill sees only its own supplier data. A smallholder supplying two mills appears in both tenancies with separate consent." Features 01–09 enforce the isolation half of that rule at the schema level, but not the identity half — a mill is currently nothing more than a value carried in a request, so the system cannot say which mills exist, cannot tell a genuine tenant from an invented one, and cannot resolve a stored `mill_id` back to an operator. Articles 9(1), 4(3) and 12(5) require every piece of due diligence evidence to be retained for five years and produced to a competent authority on request; evidence retained that long is only defensible if the operator it belongs to is identified, and an unresolvable identifier fails that test years after the field officer who captured the record has moved on.

## Who uses it

- **Compliance analyst**: registers each mill once at onboarding, and is the only role that does so.
- **Features 01–09**: consume the registry implicitly — a request scoped to an unregistered mill is refused before any household, plot, or evidence pack is touched.
- **Auditor (years later)**: resolves the mill identifier stamped on a five-year-old evidence pack to a named operator holding a specific MPOB licence.

## MVP scope

In scope:
- A registered mill record per onboarded mill: name, MPOB licence number, postal address, email, district and state.
- Registration and single-mill lookup, performed by an analyst at onboarding rather than by the mill itself.
- Rejection of any mill-scoped request naming an unregistered mill, enforced both in the schema and ahead of every route, so an invented identifier can neither create records nor read them.
- Included in MVP despite tech.md §6.5 scheduling multi-mill tenant isolation to Sprint 5: that item is about hardening isolation as mill count grows, whereas Table 43 puts pilot go-live at M8 with two mills, and two mills cannot be told apart without a registry.

Out of scope for MVP:
- Authentication and API keys — the registry establishes who a mill is, not that a caller is that mill. Deferred to Feature 11 rather than half-built here, since neither tech.md nor the regulation scopes an authentication model.
- Listing every registered mill — a cross-tenant read with no authentication in front of it would enumerate the whole customer base, so it waits for Feature 11.
- Mill self-service registration — onboarding is an analyst-mediated commercial step (business_plan.md §5.4), not a sign-up flow.
- Replacing the per-shipment recipient fields Feature 06 captures on a batch — those identify the mill's *buyer*, not the mill, and one mill ships to many buyers.

## How data is captured / technical approach

A compliance analyst enters the mill's details once, at onboarding, from the same commercial paperwork that establishes the relationship. The registry sits beneath tech.md §6.1's five layers rather than inside any one of them: it holds no evidence and performs no verification, but every layer above it is scoped by the identity it issues. Enforcement is deliberately doubled — the schema refuses to attach a record to an unregistered mill, and the API refuses the request before it reaches a route — so isolation does not depend on application code remembering to check.

## Inputs / outputs

- **Input**: mill onboarding details — name, MPOB licence number, postal address, email, district and state — entered once by a compliance analyst.
- **Output**: a registered mill identity, which is the tenant key every record created by Features 01–09 is scoped by and the subject Feature 11 will later authenticate.

## Dependencies

Nothing upstream — this is the one feature with no dependency on any other, since a mill exists before any household is recorded against it. Everything downstream depends on it: Features 01–09 all scope their records by a mill, and Feature 11 authenticates the identity this feature issues. Its number is therefore the exception to the roadmap's dependency ordering, reflecting when it was written rather than where it sits.

## Success metric

No dedicated metric is named for this feature in tech.md; its effect is preventative rather than measurable in the innovation-accounting sense of §6.6. The closest proxy is auditability under Article 12(5) — every stored record should resolve to a named, licensed operator, so the count of records whose mill cannot be identified is the number this feature must hold at zero.
