# TAPAK MVP Feature Roadmap

Source: `../tech.md` (Section 6, Product Architecture and Technical Feasibility) and `../eudr.md` (Regulation (EU) 2023/1115). This roadmap covers **MVP scope only** — what is needed to deliver the first compliant evidence pack ahead of the 30 December 2026 deadline. Post-MVP expansion (Peninsular rulebook, multi-mill scaling, a second commodity) is out of scope here — with the exception of the tenant identity that scaling later builds on, which is in scope as Feature 10 because the M8 pilot's two mills cannot be told apart without it.

## MVP philosophy

Per tech.md §6.6: the MVP is not the platform. It is a Gap Report for 20 households at one mill, producible by hand if necessary. If a mill won't act on a hand-made Gap Report, no amount of software changes that. Every feature below exists to take that manual Gap Report and make it repeatable, defensible, and deliverable at scale — in this order:

1. Prove the gap is real and a mill will pay to close it.
2. Build the rulebook that says exactly which documents close it.
3. Capture the evidence in a way that can't be easily faked.
4. Turn captured evidence into a file a buyer will actually accept.
5. Let a mill see its own compliance status without asking us.
6. Stop re-collecting what national systems already hold.
7. Keep the pack valid year over year, not just once.

Features 10 and 11 do not appear in that sequence because they sit beneath it: every step above is scoped to a mill, and 10 is what makes a mill a real, identified thing rather than a value a caller asserts. 11 then proves a caller is the mill it claims to be.

## Build order

| # | Feature | One-line description |
|---|---|---|
| [01](01-gap-assessment-report.md) | Gap Assessment Report | Manual/semi-manual scan of a household's existing documents against EUDR requirements — the MVP and sales instrument itself |
| [02](02-land-ownership-verification.md) | Land & Ownership Verification | The state-by-state rulebook (Land Document Playbook) mapping land status to the exact documents Article 9(1)(h) requires |
| [03](03-labour-rights-declaration.md) | Labour & Rights Declaration | On-site consent, no-child-labour, and land-dispute declarations, captured under dual-track PDPA/GDPR consent |
| [04](04-deforestation-satellite-check.md) | Deforestation Satellite Check | Satellite-based comparison proving no forest loss on a plot since 31 December 2020 |
| [05](05-five-signal-verification-engine.md) | Five-Signal Verification Engine | Cross-checks GPS, photo location, land area, MPOB licence data, and yield against each other; flags mismatches for review |
| [06](06-evidence-pack-generator.md) | Evidence Pack Generator | Assembles all captured evidence into one ready-to-submit Annex II-mapped file per shipment batch |
| [07](07-supplier-mill-dashboard.md) | Supplier / Mill Compliance Dashboard | Live cleared / pending / frozen status per supplier, visible only to that supplier's mill |
| [08](08-national-system-integration.md) | National System Integration | Read-only interface into SIMS, GeoSAWIT, and e-MSPO, keyed on MPOB licence number |
| [09](09-annual-renewal-workflow.md) | Annual Renewal Workflow | Re-verification and re-issuance of the evidence pack each year, as EUDR due diligence requires |
| [10](10-mill-registry.md) | Mill Registry | The registry of onboarded mills — the tenant identity every record in 01–09 is scoped by |
| [11](11-mill-authentication.md) | Mill Authentication | Proves a caller is the mill it claims to be, so the tenant comes from a credential rather than the request |

## Dependency shape

```
10 Mill Registry ──> 11 Mill Authentication
        │
        └──> every feature below is scoped by the mill 10 registers
             │
             v
01 Gap Assessment ──┐
                     ├──> 02 Land & Ownership ──┐
                     ├──> 03 Labour & Rights    ├──> 05 Five-Signal Engine ──> 06 Evidence Pack ──> 07 Dashboard
                     └──> 04 Deforestation Check ┘                                    │
                                                                                        v
                                                                              08 National System Integration
                                                                                        │
                                                                                        v
                                                                              09 Annual Renewal
```

01 can ship as a manual process before any of 02–09 exist. 05 depends on 02–04 producing raw signals to cross-check. 06 depends on 05 clearing a record. 08 is a cross-cutting input that 02 and 05 both consume once available. 09 depends on 06 already existing once, since renewal re-runs the same pipeline. 10 is the one feature whose number does not match its dependency position: it underpins all of 01–09 but was written after them, once the cost of leaving mill identity implicit became clear. 11 depends on 10 and blocks nothing — 01–09 work under 10 alone, and gain confidentiality rather than capability when 11 ships.
