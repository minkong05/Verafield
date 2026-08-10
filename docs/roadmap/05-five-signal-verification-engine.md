# Feature 05 — Five-Signal Verification Engine

## Summary

Cross-checks five independent signals captured at the moment of collection — GPS check-in, photo geotag, declared land area, MPOB licence coverage, and yield — against each other, and raises an automatic review flag on any mismatch. This is tech.md's Asset Two, the Five-Point Field Check (§6.3.2).

## Why it exists

Article 10(2)(h) treats data and document falsification as a specific risk factor in an operator's risk assessment, and Article 18(2)(d) gives EU competent authorities the right to test a due diligence statement against Copernicus and other earth-observation data. A single self-reported data point (a GPS pin, a photo) is trivially fabricated by a field officer, a dealer, or a smallholder under pressure. The only way to make fabrication difficult without full-time human audit is to require several independent signals to agree.

## Who uses it

- **Field officer**: is checked by this system in real time (or near-real time) — a mismatch at collection time means an immediate second visit is cheaper than one discovered months later.
- **Compliance analyst**: reviews the anomaly queue for flagged households before evidence packs are assembled.
- **GIS specialist (Months 1–6)**: manually reviews disagreements between human judgment and system output to calibrate thresholds.

## MVP scope

In scope:
- All five signal comparisons as specified in tech.md Table 41:
  1. GNSS check-in time/coordinates vs. the collection record's stated time/coordinates.
  2. Coordinates/timestamp embedded in site photographs vs. the polygon centroid.
  3. System-computed plot area vs. the area stated on the title.
  4. Area covered by the MPOB licence vs. plots actually declared.
  5. Annual output ÷ area vs. the regional yield benchmark.
- An anomaly review queue: any mismatch above threshold routes to human review rather than silently failing or silently passing.
- Manual threshold calibration using the first 400 households as the training set (tech.md §4.2) — thresholds are not assumed correct on day one.

Out of scope for MVP:
- Fully unsupervised anomaly detection (e.g. ML-based scoring) — MVP uses fixed, manually-tuned thresholds, not a learned model.
- Cross-mill anomaly correlation — each mill's checks run independently for MVP (see also Feature 07's multi-tenant isolation).

## How data is captured / technical approach

A versioned rule engine (tech.md §6.1 Layer 2) that consumes: GNSS/photo metadata from on-site collection, the declared area from Feature 02, the MPOB licence data from Feature 08 (once available) or manually entered in the interim, and yield records. Thresholds are configuration, not code, so they can be re-tuned as the calibration set grows without a redeploy. Per tech.md §6.3.2: the five rules themselves are easy to copy, but the thresholds — how much area variance is normal on Sarawak native customary land, how high a tonnes-per-hectare figure is suspicious for a given stand age — can only be learned from real field data, which is why this is treated as defensible IP rather than a commodity rule set.

## Inputs / outputs

- **Input**: GNSS/photo metadata (Feature 03's collection mechanism), declared land area (Feature 02), MPOB licence and yield data (Feature 08 or manual entry).
- **Output**: a pass/flagged status per household per signal, with flagged records routed to a human review queue rather than proceeding automatically to Feature 06.

## Dependencies

Depends on Features 02, 03, and 04 having produced raw signals to check, and ideally Feature 08 (national system integration) for MPOB licence data — until 08 ships, this data can be entered manually as an interim measure. Gates Feature 06 (Evidence Pack Generator): a household with an unresolved flag should not produce a pack.

## Success metric

Households cleared per field officer per month, and anomaly false-positive rate (tech.md §6.6) — the unit economics break if throughput stays below 25 households/officer/month after six months, and trust breaks if false positives run high.
