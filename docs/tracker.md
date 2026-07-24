# Longevity Foundry — Contribution Tracker

**Scope of this version:** Contribution Candidates extracted from **Project Intelligence Reports 0001–0003 only**, per Gaurav's instruction to start narrow and add later reports (0004 onward) once more familiar with those topics. Do not re-derive this tracker from scratch in future sessions — extend it.

**Sources read in full this session (for context, not yet mined for their own candidates):** PIR 0005–0014, the Constitutional Specification v0.1, and Research Foundry v4. Their own Contribution Candidates are deliberately deferred — see the Deferred section at the bottom.

**PIR 0004** ("What Is Caloric Restriction Teaching Us") exists on Gaurav's local device but is still missing from this Claude Project's knowledge base — an attempted resync failed (upload rejected). It has not been read or mined yet, consistent with the current 0001–0003 scope.

**Reading convention:** the **PIR03-C2 — Current State** block below is canonical for what is true *now*. The **PIR03-C2 — Changelog** preserves history. Where an older narrative paragraph and the Current State block disagree, the Current State block wins.

---

## PIR03-C2 — Current State (canonical)

**Target unknown (v1 — technical reliability only):** Do PC-transformed epigenetic clocks reduce **technical measurement error** relative to their original versions on **independently rebuilt public replicate data**, and **what effect sizes exceed each clock's technical measurement-noise floor**? *(Deliberately avoids implying technical reliability alone establishes trial detectability. Biological variation, longitudinal drift, and responsiveness are out of v1 scope — Tiers B/C/D.)*

| Field | Value |
|---|---|
| Status | **First real-data result produced (GSE55763, 2026-07-24) — hypothesis SUPPORTED, 4/4 pairs** |
| Current milestone | **Gate 3 crossed** (scientific result produced) — see `status_report_0.3.1.md` gate ladder |
| Primary scorer | **methylCIPHER `@9e8c1e5`** (LOCKED) — installed, run; GrimAge=V1 per manifest |
| Secondary scorer | **pyaging — implementation-sensitivity check only** (not yet run) |
| Completed | ICC engine + F-CIs (Shrout–Fleiss verified), within-subject SD, mean absolute difference, MDC95, **variance ratio + paired bootstrap CI**, detectability screen, **CLI/runner**, provenance schema, **+ first real GSE55763 run (scores.csv, RESULTS.md, PROVENANCE.md)** |
| Result | **PC reduces technical error, 4/4 supported.** Variance ratios (PC/original): PhenoAge 0.036, GrimAge 0.128, Horvath1 0.133, Hannum 0.135 — all CIs < 1. PC raw ICCs 0.990–0.998. |
| Age-accel ICC | **DONE (2026-07-24):** age-acceleration ICC computed — PC 0.972–0.988, originals fall to 0.756–0.959 ("good"). **PC advantage widens** under age-accel (e.g. PhenoAge 0.756→0.988). SEM & variance ratio **invariant** (within-subject error unchanged). Matches published PC accel ~0.97. |
| Robustness | **DONE:** compression audit (denoising not compression — noise −87–96%, signal retained 74–85%, ranking ρ 0.87–0.96), leave-one-subject-out (0/144 flips), outlier audit (cg00017157 dismissed — not a clock CpG), Bland–Altman. 5 figures. `out/ROBUSTNESS.md`. |
| Reporting | **DONE:** `docs/PIR03-C2/TECHNICAL_REPORT_v0.1.md` (14 sections, 5 figures) + `PIPELINE.md`. |
| Experiment E2 | **DONE (2026-07-25): Implementation-ROBUST.** pyaging 0.3.1 reproduces M1 — per-sample scores r≥0.9997, ICC & variance-ratio ordering ρ=1.000, verdict supported 4/4 in both. One benign divergence: GrimAge constant −2.63 yr calibration offset (r=1.0). Caveat: PC-clock independence partial (shared Higgins-Chen reference). Docs: `E2_PROTOCOL`, `IMPLEMENTATION_COMPARISON`, `POSTMORTEM_E2`; scores `out_E2/`. |
| Next action | **formal Tier-3 tolerance comparison; independent third-party rerun; ICC(1,1)/(3,1) sensitivity** — THEN consider v1.0 freeze (E2 done) |
| Following action | **pyaging sensitivity check** on overlapping clocks; ratify tiered reproduction gate into `SCORING_DECISION.md` |
| Publication gate | Box fast-path unavailable → **gate redefined as tier hierarchy** (T1 reproduce published stats · T2 independent GEO rebuild ✅ · **T3 consistency within tolerances — to ratify**) |
| Remaining v1 work | real scores; pairing audit (VAL-DATA-AUDIT); median/max abs diff + Bland–Altman LoA if not yet landed; reference comparison; RESULTS report; public CI (pytest green); **v1 protocol freeze** |
| North Star | The open reproducible **metrology layer for aging biomarkers** (biomarker-agnostic; v1 = epigenetic clocks, technical reliability) |
| Key docs | VISION, PROTOCOL, SCORING_DECISION, CLOCK_MANIFEST.csv, acceptance/*, STATUS_REVIEW, INPUT_OUTPUT (all under `Contributions/PIR03-C2/`) |

**Evidence & claim gates (governance):**

| Field | Value |
|---|---|
| Evidence state | **First real-data result (GSE55763, 2026-07-24):** PC-transformed clocks reduce technical measurement error vs originals on an independent GEO rebuild (36 pairs) — joint verdict **supported (4/4)**, all variance-ratio CIs < 1. **Raw-age ICC only.** |
| Current claims | **First real finding + software/synthetic validation.** Result strikingly consistent with published Higgins-Chen figures (PC raw ICC ≥ 0.99; mean abs diff ~ published). **NOT yet a ratified public-reproduction claim** — Tier-3 tolerance check + age-acceleration ICC pending. |
| Next claim gate | **Formal Tier-3 consistency check** (rebuilt cohort vs published, prespecified tolerances) + age-acceleration ICC + ICC(1,1)/(3,1) sensitivity |
| Public-reproduction gate | GSE55763 GEO rebuild **done ✅**; **Tier-3 tolerance ratification pending** (gate redefined — Box fast-path gone; see `status_report_0.3.1.md`) |

**Architecture note:** reliage is **scorer-agnostic** — it consumes a versioned score table + replicate map, so it depends on *neither* a methylation pipeline *nor* ComputAgeBench. (Earlier notes calling it "a companion package that depends on ComputAgeBench" are superseded; ComputAgeBench is no longer a dependency. methylCIPHER produces the v1 scores.)

## PIR03-C2 — Changelog (history; not current state)

- **v0.1.0** — minimal open bridge: verified ICC engine (ICC 1/2/3, F-CIs, Koo–Li bands; reproduces Shrout–Fleiss 0.17/0.29/0.71), scores→leaderboard runner, synthetic generator, selfcheck (2 gates).
- **v0.2.0** — added within-subject error + MDC95 columns; input→output walkthrough; public-data download bundle (`data/`).
- **v0.2.1** — mean-absolute-difference metric; leaderboard columns made unit-neutral (Within-subject SD / Mean abs diff / Individual MDC95); walkthrough corrected to the 5-stage pipeline.
- **Protocol lock** — `PROTOCOL.md` (analytic decisions frozen before results) + `CLOCK_MANIFEST.csv`. Verified current methylCIPHER computes GrimAgeV1/V2 + all PC-clocks in-package (`calcPCClocks`) → 4 clean original↔PC pairs (Horvath1, Hannum, PhenoAge, GrimAge). Corrections: MDE→MDC95; per-clock units (DunedinPACE = pace, DNAmTL = kb); ICC(2,1) primary + (1,1)/(3,1) sensitivity; "9→1.5 yr" = median/max abs replicate difference (NOT within-subject SD; Horvath1 median 2.1/max 5.4; GrimAge 0.9/2.4; PC raw ICC >0.99, accel ~0.97); GEO-rebuild gate for public-repro claim.
- **Acceptance restructure** — split into `acceptance/{validation_cases, published_reference_cases, replication_hypotheses}.yaml` + README. Two gates (tool-validation vs scientific-replication verdict); four-tier taxonomy (A technical / B short-interval-stable / C longitudinal=SATSA / D acute-responsiveness).
- **v0.3.0** — **variance ratio + paired bootstrap CI** (primary endpoint) in `reliage.contrast`; **detectability engine** (`effect_detectable` / `detectability_table` / `recommend_for_effect`) in `reliage.detectability`; selfcheck → 4 gates. Mission reframed to measurement science; "Measurement Characteristics" → "Measurement Capability".
- **v0.3.1 + SCORER LOCKED** — methylCIPHER primary / pyaging sensitivity-only (`SCORING_DECISION.md`, commit-level provenance checklist + prespecified fast-path↔GEO tolerances). Turnkey runner `reliage/scoring/` (`score_methylCIPHER.R` provenance-emitting; `run_analysis.py` end-to-end — leaderboard + paired contrasts + detectability + verdict, tested on synthetic scores → joint verdict "supported" 4/4; `PROVENANCE.template.md`). Trial-mode detectability relabelled a measurement-noise **screen** (not a power calc). `STATUS_REVIEW.md`; `datasets/` scaffold. North Star → open metrology layer for aging biomarkers; roadmap → Measurement → Detectability → Recommendation.

---

## Pass 2 — external prior-art sweep across the rest of the backlog

Checked every remaining candidate (everything except the already-resolved PIR01-C1/PIR03-C1) against the published literature and existing open tools. Findings, most consequential first:

**PIR01-C4 (curated cross-study intervention database) — substantially superseded.** [DrugAge](https://genomics.senescence.info/drugs/) (part of the Human Ageing Genomic Resources suite alongside GenAge/CellAge/LongevityMap) already is this: ~3,423 curated entries, 30+ species, freely downloadable as CSV, actively maintained (Build 5, Nov 2024). Rebuilding raw curation here has no remaining information gain. **What DrugAge explicitly does *not* do**, per its own documentation: include human clinical trials, include negative/null results, or perform cross-study statistical harmonization/meta-analysis. That residual — a thin statistical-comparison layer *on top of* DrugAge — is a smaller, genuinely open follow-on if Gaurav wants it later, but it's not separately tracked as its own candidate here since it wasn't part of the original extraction. Moved to Superseded.

**PIR01-C5 (negative-result/failed-translation registry) — scope narrowed, not superseded.** [Clinical Trial Failures Database](https://clinicaltrialfailures.com/) is a real, actively maintained (updated July 2026), structured, filterable database of 23,517 stopped clinical trials with classified stop-reasons, built from the ClinicalTrials.gov API. It's general pharma, not aging-specific, but it means the *clinical-trial-stoppage* slice of "failed translation" is already well covered externally — Gaurav's tool could simply filter/cross-reference it for longevity-relevant sponsors rather than rebuild it. What remains genuinely uncovered: **preclinical, model-organism-level** negative and failed-translation results (a worm/fly result that never replicated in mammals, a mouse effect that failed to translate). This is exactly the gap DrugAge itself admits it doesn't fill, and nothing else found fills it either. Recommend narrowing PIR01-C5 to this preclinical slice specifically — smaller, sharper, and confirmed open.

**PIR02-C1 (rejuvenation-vs-identity trajectory benchmark) — reframed, not superseded.** Found "[Longevity and rejuvenation effects of cell reprogramming are decoupled from loss of somatic identity](https://www.biorxiv.org/content/10.1101/2022.12.12.520058v1.full)" (bioRxiv, 2022) — a meta-analysis of 41 time-course datasets across 14 studies using mixed-effect models and multi-tissue aging clocks, which already establishes (for OSKM/OSK/7F reprogramming specifically) that rejuvenation and identity-loss are statistically dissociable. This is the same scientific question PIR02-C1 asks, and it's been answered in a specific case. But the paper's own aging clocks are described as "previously developed... (unpublished)" — no open dataset or reusable tool was released. This is the same pattern as ComputAgeBench/the reliability paper: the science is validated, the public rerunnable artifact isn't there. Recommend keeping PIR02-C1 but reframing it as: build an *open* version of this analysis using public clocks instead of proprietary ones, on public GEO reprogramming time-course data, packaged so a third party can test a new reprogramming protocol and get a rejuvenation-vs-identity decoupling score. Risk is lower now that the underlying methodology is externally validated.

**PIR01-C3 / PIR02-C3 / PIR03-C3 (evidence-map / contradiction-graph candidates) — confirmed open, with a useful building block.** No existing tool does claim-level, source-classified, contradiction-aware evidence mapping for aging mechanisms or biomarkers. The closest adjacent resource is [HALD](https://www.nature.com/articles/s41597-023-02781-0) (Human Aging and Longevity knowledge graph) — 12,227 entities, 115,522 relations extracted automatically from ~340,000 PubMed *abstracts*, classified only as positive/negative/associated. Its authors explicitly confirm it does **not** track contradictory evidence, evidence strength, or source credibility, and it only mines abstracts (not full text), which is why its overlap with a manually-curated resource like LongevityMap is only ~10%. It's not a substitute for any of the three evidence-map candidates, but its auto-extracted relations could be reused as a *candidate-claim seed list* to reduce the cold-start curation effort on any of the three. Also adjacent but not overlapping: the NIH [SenNet](https://www.cell.com/cell/fulltext/S0092-8674(26)00587-8) consortium's new human senescence cell atlas — that's biological mapping data, not a literature evidence graph, so it doesn't compete with PIR01-C3 but is worth knowing about as fresh primary-source material for it.

**PIR01-C2 (reproducible reanalysis notebooks for landmark studies, e.g. ITP rapamycin) — confirmed open and now precisely scoped.** The [Mouse Phenome Database ITP portal](https://phenome.jax.org/projects/ITP1) hosts the raw ITP cohort data (2004–2021) as downloadable spreadsheets, but no reproducible analysis code, notebooks, or statistical pipeline exists publicly. A third party would still need to build: the log-rank survival test implementation, a data-cleaning pipeline from the raw spreadsheets, dose-response modeling across compounds, and visualization. This makes the candidate's next action more concrete than before — not a reason to reprioritize, just to note it's a well-specified, real gap.

**PIR03-C4 (confound-audit tool) — inconclusive, worth a direct check before starting.** [Biolearn](https://github.com/bio-learn/biolearn) (open-source, Biomarkers of Aging Consortium, published in *Nature Aging*) does biomarker computation with "quality control and cell-type deconvolution," which sounds adjacent to confound auditing, but a source-level check couldn't confirm whether that deconvolution is exposed as a reusable, standalone diagnostic (flagging confounds in *someone else's* published result) versus being purely an internal preprocessing step for Biolearn's own biomarker calculations. Recommend Gaurav (or a future pass) read Biolearn's source directly before scoping this candidate, since it may be a dependency that meaningfully cuts the effort rather than a full substitute.

**PIR02-C4 / PIR02-C5 (in-vivo reprogramming database / safety-window meta-analysis) — unaffected.** No dedicated structured database of in-vivo reprogramming dose/duration/outcome data was found. The 14 studies referenced by the rejuvenation-vs-identity paper above are a useful starting bibliography but don't substitute for the structured database these two candidates call for.

---

## PIR03-C2 build-research findings (prior-art landscape; historical context)

Full competitive/prior-art landscape for reliability benchmarking:

| Tool | Lang | Open? | Does reliability (ICC)? | Notes |
|---|---|---|---|---|
| **ComputAgeBench** | Python | Yes (CC BY-SA) | No | Accuracy benchmark only; data is unique biological samples (no technical replicates). Not a reliage dependency in the locked v1 design. |
| **PC-Clocks** (MorganLevineLab) | R | Yes | No | Computes PC clocks; ships example replicate data (Lehne 2015) but no ICC/benchmark harness. Unmaintained → methylCIPHER. |
| **methylCIPHER** (HigginsChenLab) | R | Yes | No (calc only) | Clock calc library (PC clocks, GrimAgeV1/V2, DunedinPACE...). **v1 PRIMARY scorer.** |
| **pyaging** | Python | Yes | No (calc only) | Large clock catalogue; **v1 SECONDARY (sensitivity) scorer only.** |
| **TranslAGE** (Oct 2025) | web platform | **No — gated** | **Yes, comprehensively** | 41 clocks, ICC on 5 technical + 6 biological replicate datasets, but web-only + download-restricted. Not independently reproducible. |

**Reassessment (still current):** the reliability *science* is published and TranslAGE is a comprehensive but **gated** platform. So PIR03-C2 is an **openness + reproducibility** contribution: no open, rerunnable reliability benchmark exists on public data. On-mission per the Foundry Constitution (reproducible, independently checkable).

**Confirmed public input data:** **GSE55763** (Lehne 2015, 450K, 36 duplicate pairs — anchor). Secondary/future: E-MTAB-4664 (Tier B/D), GSE49065, SATSA/E-MTAB-7309 (Tier C longitudinal), diurnal set (accession TBD).

---

## Recommended build order

1. **PIR03-C2** — open reliability-benchmarking module (`reliage`, scorer-agnostic; methylCIPHER-scored for v1). **In progress — see Current State.**
2. **PIR02-C1, reframed** — open rejuvenation-vs-identity-loss benchmark using public clocks, following the externally-validated 2022 decoupling methodology.
3. **PIR01-C2** — ITP reanalysis notebooks; unaffected, precisely scoped.
4. Evidence-map trio (PIR01-C3, PIR02-C3, PIR03-C3) and narrowed PIR01-C5 — all confirmed open, good Next-tier once 1–3 are underway.

---

## Now

| ID | Title | Source | Debt class | Effort | Rationale |
|---|---|---|---|---|---|
| PIR03-C2 | Reliability-benchmarking module (`reliage`) | PIR 0003 (Ch25, Project 2) | Measurement | ~3–5wk | **Sole Now item** — v0.3.1, synthetic pipeline validated; at real-data execution (see Current State). Depth over breadth: nothing else is "Now" until reliage hits v1 freeze or is explicitly paused. |

## Superseded (do not build — satisfied externally)

| ID | Title | Source | Status | Note |
|---|---|---|---|---|
| PIR01-C1 / PIR03-C1 | Multi-clock benchmark on public methylation data | PIR 0001, PIR 0003 | **Superseded by ComputAgeBench** | See prior-art landscape. [GitHub](https://github.com/ComputationalAgingLab/ComputAge) |
| PIR01-C4 | Curated cross-study intervention database | PIR 0001 (Ch27) | **Superseded by DrugAge** | 3,423 entries, 30+ species, actively maintained. Excludes negative results and cross-study statistical harmonization — a thin comparison layer on top remains a possible smaller follow-on, not separately tracked. [DrugAge](https://genomics.senescence.info/drugs/) |

## Next

| ID | Title | Source | Debt class | Effort | Rationale |
|---|---|---|---|---|---|
| PIR02-C1 | Open rejuvenation-vs-identity-loss benchmark (using public clocks) | PIR 0002 (Ch27) | Measurement | 5–7wk | Report's own top pick; 2022 decoupling paper validates the methodology but used unpublished clocks/data. **Promoted here from Now** — not started until reliage (PIR03-C2) reaches v1 freeze or is explicitly paused (depth over breadth). |
| PIR01-C2 | Reproducible reanalysis notebooks for landmark studies | PIR 0001 (Ch27) | Replication | 6–8wk | Confirmed open — ITP raw data exists publicly (MPD portal) but no reanalysis code does. Precisely scoped: log-rank survival test, data-cleaning pipeline, dose-response modeling, visualization all still need building. |
| PIR02-C2 | Reproducible epigenetic-clock re-analysis pipeline | PIR 0002 (Ch27) | Replication | 4–6wk | Related to PIR02-C1's tooling — likely shares infrastructure with it and with PIR01-C2. Not separately checked against external prior art this pass; check before starting. |
| PIR01-C3 | Evidence map / claim-contradiction graph for a contested mechanism | PIR 0001 (Ch27) | Theory | 4–6wk | Confirmed open — HALD is the closest adjacent resource but explicitly doesn't do contradiction/evidence-strength tracking; its auto-extracted relations are a possible seed list, not a substitute. |
| PIR02-C3 | Source-classified evidence map of partial-reprogramming claims | PIR 0002 (Ch27) | Theory | 4–6wk | Same finding as PIR01-C3 — confirmed open, HALD-seedable. |
| PIR03-C3 | Source-classified evidence map of biomarker claims by ladder level | PIR 0003 (Ch25) | Theory | 5–7wk | Same finding as PIR01-C3/PIR02-C3. Biolearn is adjacent (computes biomarker values) but doesn't classify claims by evidence maturity — confirmed, not a substitute. |
| PIR01-C5 | Negative-result / failed-translation registry (narrowed to preclinical/model-organism results) | PIR 0001 (Ch27) | Negative-Evidence | 4–6wk (narrower scope) | Clinical-trial-stoppage data is now well covered externally (Clinical Trial Failures Database) — narrow scope to the preclinical/model-organism slice, which is confirmed open and is the harder, more valuable gap anyway (DrugAge itself excludes it). |

## Later

| ID | Title | Source | Debt class | Effort | Rationale |
|---|---|---|---|---|---|
| PIR02-C4 | Curated database of in-vivo reprogramming experiments | PIR 0002 (Ch27) | Data | 5–7wk | Unaffected by either pass — confirmed open, still curation-heavy. The 2022 decoupling paper's 14-study bibliography is a useful seed list. |
| PIR02-C5 | Safety-window meta-analysis (dose/duration → outcomes) | PIR 0002 (Ch27) | Translation | 6–8wk | Explicitly dependent on PIR02-C4; unaffected. |
| PIR03-C4 | Confound-audit tool | PIR 0003 (Ch25) | Measurement / Metadata | 6–8wk | Inconclusive external check — Biolearn's cell-type deconvolution may or may not be reusable as a dependency; needs a direct source-code look before scoping. |

---

## Full tracker (all fields)

| ID | Title | Source report | Target Unknown | Debt class | Extraction type | Effort (wk) | Priority | Status | Next action | Dependencies | Links |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PIR01-C1 | Multi-clock benchmark on public methylation data | PIR 0001 | Are epigenetic clocks measuring aging or correlated noise? | Measurement | explicit | 4–6 | — | **Superseded (external)** | Monitor ComputAgeBench. | none | [ComputAgeBench](https://github.com/ComputationalAgingLab/ComputAge) |
| PIR01-C2 | Reproducible reanalysis notebooks for landmark studies | PIR 0001 | Do landmark aging-modification results reproduce from public data with pinned code? | Replication | explicit | 6–8 | Next | Backlog | Build ITP reanalysis: pull MPD cohort spreadsheets (2004–2021), implement log-rank survival test + dose-response modeling, containerize. | none | [MPD ITP portal](https://phenome.jax.org/projects/ITP1); shares tooling with PIR02-C2 |
| PIR01-C3 | Evidence map / claim-contradiction graph for a contested mechanism | PIR 0001 | Which claims about a contested aging mechanism are supported vs. contradicted, by whom? | Theory | explicit | 4–6 | Next | Backlog | Select one contested mechanism claim (e.g., senescence causally drives aging); consider seeding candidate relations from HALD's auto-extracted graph. | none | [HALD](https://www.nature.com/articles/s41597-023-02781-0) (seed list only) |
| PIR01-C4 | Curated cross-study intervention database | PIR 0001 | Which interventions have been tested where, on what outcomes? | Data | explicit | 6–8 | — | **Superseded (external)** | None — DrugAge already covers this. | none | [DrugAge](https://genomics.senescence.info/drugs/) |
| PIR01-C5 | Negative-result / failed-translation registry (narrow to preclinical/model-organism) | PIR 0001 | Which preclinical aging interventions failed to translate or replicate, and why? | Negative-Evidence | explicit | 4–6 | Next | Backlog | Scope to preclinical/model-organism results (worm/fly/mouse); cross-reference Clinical Trial Failures Database for the clinical slice rather than rebuilding it. | none | [Clinical Trial Failures Database](https://clinicaltrialfailures.com/) (adjacent, clinical-only) |
| PIR02-C1 | Open rejuvenation-vs-identity-loss benchmark | PIR 0002 | Can rejuvenation trajectories be distinguished from identity-loss trajectories in reprogramming data? | Measurement | explicit | 5–7 | Next | Backlog | Reproduce the 2022 decoupling-paper methodology (mixed-effect models over time-course datasets) using public clocks; package as a rerunnable tool. | public clocks | [2022 decoupling paper](https://www.biorxiv.org/content/10.1101/2022.12.12.520058v1.full); relates to PIR03-C2 tooling |
| PIR02-C2 | Reproducible epigenetic-clock re-analysis pipeline | PIR 0002 | Do published reprogramming/clock results reproduce independently? | Replication | explicit | 4–6 | Next | Backlog | Not yet checked against external prior art — check before starting. | none | PIR01-C2 |
| PIR02-C3 | Source-classified evidence map of partial-reprogramming claims | PIR 0002 | Which partial-reprogramming safety/efficacy claims are supported vs. contradicted, by whom? | Theory | explicit | 4–6 | Next | Backlog | Same as PIR01-C3 — HALD as a possible seed list only. | none | PIR01-C3 |
| PIR02-C4 | Curated database of in-vivo reprogramming experiments | PIR 0002 | What in-vivo reprogramming experiments exist, at what dose/duration? | Data | explicit | 5–7 | Later | Backlog | Use the 2022 decoupling paper's 14-study bibliography as a starting seed list. | none | Prerequisite for PIR02-C5 |
| PIR02-C5 | Safety-window meta-analysis (dose/duration → outcomes) | PIR 0002 | What dose/duration window is safe vs. tumorigenic in reprogramming? | Translation | explicit | 6–8 | Later | Backlog | — | PIR02-C4 | — |
| PIR03-C1 | Multi-clock benchmark on public methylation data | PIR 0003 | Same as PIR01-C1 | Measurement | explicit | 4–8 | — | **Superseded (external)** | Same as PIR01-C1. | none | [ComputAgeBench](https://github.com/ComputationalAgingLab/ComputAge) |
| PIR03-C2 | Reliability-benchmarking module (`reliage`) | PIR 0003 | Do PC-transformed clocks reduce **technical** measurement error vs their originals on rebuilt public replicate data, and what effect sizes exceed each clock's technical measurement-noise floor? *(technical reliability only)* | Measurement | explicit | 3–5 | **Now (lead)** | **Building — v0.3.1, synthetic pipeline validated (real-data execution)** | Run the PC-Clocks example fast path with **pinned methylCIPHER**; then rebuild the 36-pair cohort from GSE55763 and compare within prespecified tolerances. | Pinned methylCIPHER (primary); pyaging (sensitivity only) | [SCORING_DECISION](Contributions/PIR03-C2/SCORING_DECISION.md); [GSE55763](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE55763); [methylCIPHER](https://github.com/HigginsChenLab/methylCIPHER) |
| PIR03-C3 | Source-classified evidence map of biomarker claims by ladder level | PIR 0003 | Which biomarker claims sit at which evidence-ladder rung, and why? | Theory | explicit | 5–7 | Next | Backlog | Same pattern as PIR01-C3/PIR02-C3. Biolearn adjacent (computes values, doesn't classify claim maturity) — not a substitute. | none | [Biolearn](https://github.com/bio-learn/biolearn) |
| PIR03-C4 | Confound-audit tool | PIR 0003 | Which published aging-biomarker results are confounded by uncontrolled variables? | Measurement / Metadata | explicit | 6–8 | Later | Backlog | Read Biolearn's source directly to check whether its cell-type deconvolution is reusable as a dependency before scoping. | Possibly Biolearn (unconfirmed) | [Biolearn](https://github.com/bio-learn/biolearn) (unconfirmed fit) |

---

## Cross-report + external signal (context, not yet actionable)

Independent confirmation from four Foundry reports (0001, 0003, 0008, 0009) plus the external literature (ComputAgeBench's own acknowledged gap, and an Oct 2025 paper with no visible open tool) all point at the reliability-benchmarking work as the single best thing to build first.

---

## Deferred (not yet mined for their own candidates)

Per Gaurav's instruction, Contribution Candidates from the following are **not yet extracted** into this tracker:

- PIR 0004 — What Is Caloric Restriction Teaching Us (also still missing from the Project KB — resync attempted, failed, needs retry)
- PIR 0005 — What Does Rapamycin Reveal About Aging
- PIR 0006 — What Makes an Aging Intervention Succeed
- PIR 0007 — When Should We Trust Our Understanding of Aging
- PIR 0008 — Which Unknowns Matter Most
- PIR 0009 — How Should We Design Decisive Experiments
- PIR 0010 — When Has Science Earned Action
- PIR 0011 — How Should We Design Aging Interventions
- PIR 0012 — How Should We Validate Aging Interventions
- PIR 0013 — How Do Validated Interventions Survive Changing Contexts
- PIR 0014 — How Should Society Govern Scientific Power (series capstone)
- Frontier Research Foundry — Constitutional Specification v0.1
- Research Foundry v4 — Investigation-Centric Intelligence

*Last updated: this session — reconciled PIR03-C2 canonical state to reliage v0.3.1 + locked methylCIPHER ADR; moved history to the changelog; corrected target unknown to technical-reliability-only and the scorer/dependency fields. Do not regenerate from scratch — extend and keep Current State authoritative.*
