# 6.0 Product Architecture and Technical Feasibility

This criterion sits in natural tension with our business model, and it is better to say so than to disguise it. We are a field service company; the software is a tool. Claiming an artificial intelligence capability we do not have would be seen through immediately. Saying nothing would forfeit the marks. The correct answer is to articulate precisely what is proprietary — and it is not the mobile application.

## 6.1 System architecture: five layers

***Table 38:*** *System architecture. Technology choices are indicative and would be confirmed with the development partner at Sprint 0.*

| **Layer** | **Contents** | **Indicative technology** | **Requirement addressed** |
| --- | --- | --- | --- |
| **1 · Collection** | Offline-first mobile client: GNSS tracks, plot polygons, document photography, signatures and thumbprints, consent capture | React Native, local SQLite store, background sync queue | Availability under intermittent rural connectivity |
| **2 · Verification** | Five-signal cross-checking, threshold triggers, anomaly queue and review workflow | Versioned rule engine plus satellite imagery comparison service | Data integrity; Art 10(2)(g) and (h) |
| **3 · Rules** | State tenure mapping, EUDR and MSPO requirement templates, versioning and republication | Structured rule library under version control | Maintainability as regulation changes |
| **4 · Output** | Annex II evidence pack as PDF plus structured data including GeoJSON; supplier status dashboard; annual review scheduling | Document generation service and API | Deliverability to the buyer's system |
| **5 · Interface** | Read-only consumption of SIMS, e-MSPO and GeoSAWIT™, keyed on MPOB licence number | Read-only ingestion and cross-validation | Legacy compatibility; no duplication of national systems |

### 6.1.1 Technical specifications that come from the regulation, not from preference

* Coordinate system WGS84; latitude and longitude to at least six decimal places, expressly required by Article 2(28).
* Polygons mandatory above four hectares with sufficient points to describe the perimeter (Article 2(28)). Below four hectares we capture polygons anyway, because buyers ask for them.
* Output format GeoJSON, machine-readable, so the mill can pass it into a buyer's system without re-keying.
* Mandatory metadata on every record: collection method and accuracy, collection date, collector identity — matching the Article 10(2)(g) requirement on source, reliability and validity of information.
* Forest three-threshold test recorded per plot: area above 0.5 ha, tree height above 5 m, canopy cover above 10%, excluding land predominantly under agricultural or urban use (Article 2(4)).
* Five-year retention on all records and due diligence documentation (Articles 9(1), 4(3) and 12(5)).

## 6.2 Integration with national systems

The governing principle is stated once and applied everywhere: where the national systems reach, we consume them; where they do not, we fill the gap; we never rebuild what MPOB already has.

***Table 39:*** *Interface strategy with Malaysian national systems.*

| **System** | **What it does** | **How we use it** |
| --- | --- | --- |
| SIMS | Mandatory since 2023. Records supplier name, MPOB licence number and quantity for every FFB transaction; usage among licence holders reported at 95% | We do not duplicate transaction capture. We key our plot records on the MPOB licence number and cross-validate declared volume against area-derived expected yield |
| GeoSAWIT™ | Mapping platform covering estates, organised smallholders and independent smallholders; upgrade due mid-2026 | Where mapping already exists we cite it and do not remap, lowering our own cost. We fill only what is uncovered or does not meet the EUDR format and transferability requirement |
| e-MSPO traceability module | Live since April 2025: supplier and buyer registration, monthly declarations, sales declarations | We cite certification status and declaration records as cross-validation of what we collect in the field |
| MSPO certificate | Malaysian Sustainable Palm Oil certification | Recorded as complementary information under Article 10(2)(n) and conditionally so. MSPO does not substitute for plot coordinates or a land title |
| EU Article 33 information system | The EU's official due diligence statement platform | We do not touch it. The submitting party is the EU importer. Stating this boundary is part of understanding our own legal position |

**Why GeoSAWIT reaching full coverage is good news for us.** Our value was never in the coordinates. If MPOB completes national mapping, our collection cost per household falls and our margin improves, while the tenure, labour and batch-assembly work that generates our revenue is untouched. A business that improves when the government succeeds is a business that has chosen the right gap.

## 6.3 What is actually proprietary

Three assets constitute the defensible technology. They have been given plain names, because a judge should be able to understand what each one is in a single sentence, and because a name that requires explanation usually conceals the absence of substance.

### 6.3.1 Asset one · The Land Document Playbook

***Table 40:*** *Asset one — The Land Document Playbook.*

|  |  |
| --- | --- |
| **In one sentence** | A maintained, versioned rulebook that says: for this state, this kind of land, this kind of owner — here is the exact list of documents Article 9(1)(h) requires, and here is what to do when one of them does not exist. |
| **What it contains** | Peninsular: Geran Mukim, Geran Negeri, Hakmilik Sementara, Pajakan Negeri, plus Lot or PT number with Mukim, Daerah and Negeri, plus land conditions confirming agricultural use with no restriction on oil palm. Sabah: Native Title, Country Lease, Field Register. Sarawak: Provisional Lease, and for native customary rights land the written permission of the Jabatan Tanah dan Survei. Leased land: tenancy agreement plus landlord identity plus landlord's title — without a tenancy agreement Article 9(1)(h) simply fails, so this is built as a hard validation. Untransferred inheritance: full co-owner list, engaging Article 2(40)(d). Scheme land: settler agreement and scheme number. |
| **Why it is hard to copy** | This is not code. It is knowledge scattered across each state's land law and each district's practical custom, assembled by visiting land offices and getting things wrong first. A competitor entering East Malaysia must rebuild this layer from zero, and cannot shortcut it with engineering effort. |
| **Why it is a product and not a document** | It is versioned and republished when a rule changes, and every customer record carries the rule version under which it was assessed. That is what makes an audit three years later possible. |
| **Protection** | Copyright registration of the database structure and rule set; trade secret regime for the decision logic; contractual IP assignment from any outsourced developer. |

### 6.3.2 Asset two · The Five-Point Field Check

Five signals are captured at the moment of collection that must agree with one another. Any disagreement raises an automatic review flag. The purpose is blunt: to make it difficult for a field officer, a dealer or a smallholder to fabricate a record, which is what Article 10(2)(h) treats as a risk factor and what an EU competent authority may test against Copernicus and other earth observation data under Article 18(2)(d).

***Table 41:*** *The Five-Point Field Check.*

| **#** | **Signals compared** | **What a mismatch means** |
| --- | --- | --- |
| 1 | GNSS check-in time and coordinates against the collection record's time and coordinates | The site visit did not happen where or when it was recorded |
| 2 | Coordinates and timestamp embedded in site photographs against the polygon centroid | The photograph was not taken on the plot |
| 3 | System-computed area against the area stated on the title | Boundary error, encroachment, or a title that does not describe this land. Variance above threshold triggers second review |
| 4 | Area covered by the MPOB licence against the plots actually declared | Fruit is being sold from land the licence does not cover — a major red flag |
| 5 | Annual output divided by area, against the regional yield benchmark | An implausibly high figure suggests outside fruit is being mixed in |

**Why this is genuinely defensible.** The five rules can be copied in an afternoon. The thresholds cannot. How much area variance is normal in Sarawak native customary land, and how high a tonnes-per-hectare figure is suspicious for a twelve-year-old stand in Tawau, can only be learned from real collection data. The first 400 households are our calibration set. A later entrant begins with generic thresholds and a high false-positive rate, and in compliance work false positives destroy the customer's trust faster than misses do.

### 6.3.3 Asset three · The One-Click Buyer Pack

Household-level records are automatically assembled, per batch, into the structure the EU buyer's due diligence statement requires. This is the step that turns a pile of data into a deliverable product, and it is the part of the chain no one currently specialises in.

***Table 42:*** *Field mapping from our collected data to Annex II and Article 9(1). Full version at Appendix A.*

| **Output field** | **Legal basis** | **Source in our data** |
| --- | --- | --- |
| Product description, trade name, HS code | Art 9(1)(a); Annex II point 2. Oil palm codes at Annex I include 1207 10, 1511, 1513 21/29, 2306 60 | Mill batch record |
| Quantity in kilograms of net mass | Art 9(1)(b) | Weighbridge tickets aggregated per batch |
| Country of production plus state and district | Art 9(1)(c) | Plot record |
| Geolocation of every plot in the batch | Art 9(1)(d); Annex II point 3 | Service B polygons; where several plots are mixed, all are listed |
| Production date or time range | Art 9(1)(d) | Harvest records — note this is not the delivery date and is captured separately |
| Supplier name, postal address, email | Art 9(1)(e) | Service A profile |
| Recipient name, postal address, email | Art 9(1)(f) | Mill record |
| Deforestation-free evidence | Art 9(1)(g) | Service D report |
| Legality evidence | Art 9(1)(h) | Service C file |
| **Per-batch no-mixing status flag** | Art 10(2)(j) | **Our differentiator — no national system produces this** |
| **Supplier compliance status list (cleared / pending / frozen)** | Operational control supporting Art 10 | **Our differentiator — lets the mill decide at the weighbridge** |

## 6.4 Data protection and security

Geospatial and personal data sharing is constrained by data protection law on both sides of the transaction, and treating this as an afterthought would be a material risk rather than a compliance formality.

* **Dual-track consent.** Every smallholder signs a consent instrument drafted to satisfy both the Malaysian PDPA and the GDPR, because the data will reach an EU buyer. Consent is specific as to recipient and purpose, and is separately given for any credit referral.
* **Minimisation on identity data.** We store only the last four digits of MyKad. The EUDR text nowhere requires an identity document; scanned identity cards are highly sensitive personal data and we do not hold them.
* **Data residency.** Original document scans are not uploaded outside Malaysia. What crosses the border is the evidence pack the mill chooses to send to its buyer.
* **Multi-tenant isolation.** Each mill sees only its own supplier data. A smallholder supplying two mills appears in both tenancies with separate consent.
* **Retention.** Five years, per Articles 9(1), 4(3) and 12(5), then deletion on a documented schedule.

## 6.5 Development roadmap: sprints aligned to statutory dates

***Table 43:*** *Engineering roadmap. Milestones are anchored to the two statutory dates rather than to internal preference.*

| **Sprint** | **Period** | **Deliverable** | **Statutory anchor** |
| --- | --- | --- | --- |
| Sprint 0 | M1 | State rule set v1 for Sabah and Sarawak; data model finalised | — |
| Sprint 1 | M2–M3 | Offline collection client MVP: polygons, document photography, consent signing | — |
| Sprint 2 | M4–M5 | Verification layer v1: Five-Point Field Check and anomaly queue | — |
| Sprint 3 | M6–M7 | Annex II evidence pack output and supplier status dashboard | — |
| **Pilot go-live** | **M8** | **2 mills; onboarding of 400 households begins** | **First batch complete before 30 December 2026** |
| Sprint 4 | M9–M12 | SIMS, e-MSPO and GeoSAWIT cross-validation interface; annual review scheduling | Annual review under Art 10(4) |
| Sprint 5 | M13–M18 | Rule set extended to the Peninsula; MSPO requirement templates; multi-mill tenant isolation | Second wave, 30 June 2027 |

## 6.6 Lean Startup principles in practice

Lean Startup is invoked frequently and applied rarely. Set out below is what each principle actually obliges us to do in this venture, and what would falsify our thesis.

***Table 44:*** *Lean Startup applied. The falsification column is the point of the exercise.*

| **Principle** | **Our application** | **What would falsify the hypothesis** |
| --- | --- | --- |
| **Minimum viable product** | The MVP is not the platform. It is a Gap Report for 20 households at one mill, produced by hand if necessary. If a mill will not act on a hand-made Gap Report, no amount of software will change that | A mill reads the gap scan, agrees the gap is real, and still declines to pay |
| **Build–measure–learn** | Each sprint in Table 43 ends with a field deployment, not a demo. Sprint 1 ships to two field officers onboarding real households before Sprint 2 begins | Field officers stop using the client and revert to paper |
| **Validated learning** | The Section 3.10 interviews exist to test three specific beliefs: that mills perceive third-party smallholder origin as a live commercial risk; that they will pay per household; and that the missing document is tenure rather than coordinates | Mills report that SIMS and GeoSAWIT are already sufficient for their buyers |
| **Innovation accounting** | Four cohort metrics tracked from the first pilot: households cleared per field officer per month; percentage of households with a tenure gap; anomaly false-positive rate; and days from onboarding to first evidence pack accepted by a buyer | Households cleared per officer per month stays below 25 after six months, breaking the unit economics |
| **Pivot or persevere** | Two pre-defined pivots are already written, not improvised: repositioning from an EUDR pack to a buyer-requirement pack (Section 11.2, scenario one), and shifting from EU-exposed mills to any mill with an international buyer contract | Two consecutive quarters where no new mill converts from pilot to paid |
| **Small batch sizes** | Onboarding runs cluster by cluster through a single SPOC rather than mill-wide, so a quality problem is discovered after 30 households rather than after 200 | Rework rate above 10% within a cluster |

## 6.7 Design thinking: how the service reached its current shape

The five stages below describe decisions already taken, not a process we intend to follow. Each stage names the specific design change it produced.

***Table 45:*** *Design thinking, and the design decisions each stage produced.*

| **Stage** | **What we did** | **The decision it produced** |
| --- | --- | --- |
| **Empathise** | Read the regulation against the Malaysian land tenure system rather than against a generic farm. Mapped what a Sarawak native customary rights household actually holds in a folder at home | Recognition that the binding constraint is documents, not coordinates. This reframed the entire venture away from mapping |
| **Define** | Reframed the problem statement from “there is no map” to “there is a map and no file”, after finding that GeoSAWIT already covers independent smallholders and SIMS usage had reached 95% | The problem statement now survives a well-informed judge, and survives GeoSAWIT reaching full coverage |
| **Ideate** | Considered and rejected: a farmer-facing app; a certification scheme; a marketplace; a lending product | Farmer-facing entry rejected on the evidence of Kapitani's low active usage. Lending rejected because P2P registration requires RM 5 million paid-up capital |
| **Prototype** | Built the Gap Report format and the Annex II field mapping on paper first, before any code, and tested whether they could be completed from what a household plausibly holds | The Gap Report became the MVP and the sales instrument simultaneously. Several fields were dropped as unobtainable |
| **Test** | Structured interviews with mills, dealers, SPOC officers and smallholders (Section 3.10), designed to disconfirm rather than to confirm | Findings that contradict the thesis are reported alongside those that support it. Pricing remains provisional until interview evidence replaces the assumption |
