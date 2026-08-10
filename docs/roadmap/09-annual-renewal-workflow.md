# Feature 09 — Annual Renewal Workflow

## Summary

Re-verification and re-issuance of a household's evidence pack on an annual cycle, as EUDR's ongoing due diligence obligations require, rather than treating compliance as a one-time event.

## Why it exists

Article 10(4) requires operators to document and review their risk assessments at least annually and make them available to competent authorities on request; Article 12(2) requires the due diligence system itself to be reviewed at least once a year and updated when new developments emerge. A due diligence statement proves compliance for a specific shipment at a specific time — it does not remain valid indefinitely, since land use, ownership, and deforestation status can all change year to year. Without a renewal workflow, every household would need to be re-onboarded from scratch each year, which defeats the purpose of having built a structured record in the first place.

## Who uses it

- **Compliance analyst**: schedules and tracks renewals due per household/mill.
- **Field officer**: revisits a household only for what may have changed (e.g. a new deforestation check, updated land status) rather than repeating full onboarding.
- **Mill**: sees renewal status reflected in Feature 07's dashboard.

## MVP scope

In scope:
- A per-household renewal due date, one year from the prior evidence pack's generation date.
- Re-running the relevant checks (Feature 04's deforestation check at minimum, since land use can change; Feature 02/03 only where something has changed since the last cycle) rather than a full from-scratch re-collection.
- A lapsed-renewal state that flips a household's Feature 07 dashboard status away from "cleared" if the due date passes without re-verification.

Out of scope for MVP:
- Automated proactive re-verification (e.g. continuous satellite monitoring that triggers renewal early) — MVP renewal is calendar-driven, checked once a year, not continuously monitored.
- Renewal workflow for a second commodity or Peninsular Malaysia — MVP renewal applies to the same Sabah/Sarawak oil palm households already onboarded.

## How data is captured / technical approach

Reuses the same pipeline as initial onboarding (Features 02–06) rather than a separate code path — a renewal is functionally a new run of the existing verification and evidence-pack-generation steps against an existing household record, scoped to what needs re-checking. This keeps the rule library (Feature 02) and verification engine (Feature 05) as the single source of truth for both first-time and renewal assessments.

## Inputs / outputs

- **Input**: an existing household record approaching its one-year anniversary from the last evidence pack.
- **Output**: an updated evidence pack (via Feature 06) reflecting the current year's checks, or a lapsed/frozen status (via Feature 07) if renewal isn't completed in time.

## Dependencies

Depends on Feature 06 having produced an initial evidence pack to renew, and reuses Features 02, 04, and 05. Writes status updates to Feature 07.

## Success metric

No renewal-specific metric is named in tech.md; treat it as governed by the same "days from [renewal trigger] to evidence pack accepted" cycle-time measure used for first-time onboarding (tech.md §6.6), since a slow renewal cycle risks a household lapsing out of compliance between shipments.
