> **SUPERSEDED (kept for evidence/provenance).** The canonical acceptance spec is now
> the three files in `acceptance/` (`validation_cases.yaml`, `published_reference_cases.yaml`,
> `replication_hypotheses.yaml`) + `acceptance/README.md`, which separate software validation
> from reference reproduction from verdict-based external replication. Corrections since this
> doc: "we have currently **verified** two public datasets" (not "only two are cleanly public");
> **SATSA is Tier C (longitudinal)**, not a clean technical/biological set; the "9→1.5 yr"
> figures are **median/max absolute replicate difference**, not within-subject SD. Read this
> doc for the dataset-provenance detail; use `acceptance/` for what actually gets asserted.

# PIR03-C2 — Acceptance Test Cases (published reliability results)

Purpose: concrete, **published** reliability results that `reliage` must reproduce,
so the tool has an *external* acceptance target (not just internal self-checks).
This is the "reproduce the published figures" acceptance milestone for PIR03-C2.

## The honest constraint that shapes everything below

Most published **exact** per-clock ICCs were computed on **restricted or
proprietary** datasets (HRS = dbGaP `phs000724.v7.p11`; InCHIANTI; FHS; PRISMO;
Elysium — proprietary). We cannot reproduce an exact number on data we cannot
access. Only two replicate datasets in this literature are cleanly **public**:

| Dataset | Accession | Array | Replicates | Public? |
|---|---|---|---|---|
| Lehne et al. 2015 | **GSE55763** | 450K | 36 duplicate pairs | **Yes** (used as PC-Clocks example data) |
| SATSA | **E-MTAB-7309** (ArrayExpress) | — | longitudinal/replicate | **Yes** |

**Consequence for acceptance:** the exact published numbers become *reference
anchors*; our runnable acceptance is **reproduce the published pattern — bands,
ordering, and decoupling — on public data**, plus exact-number reproduction only
where a public dataset was actually used. This is a scientifically honest
acceptance criterion, and it is stated as such in the delivery notes.

Two evidence tiers below:
- **Tier A — runnable** on public data now (pattern/band/ordering; exact where public).
- **Tier B — reference anchors** (exact published numbers, mostly on non-public data → consistency checks, not exact reproduction).

---

## Tier A — Runnable acceptance tests (public data)

### A1. PC-transformed clocks are technically "excellent" (ICC ≥ 0.90)
- **Published claim:** PC versions of established clocks and SystemsAge show the
  highest technical reproducibility; PC clocks are the reliability fix.
  Higgins-Chen: PC versions bring "agreement between most replicates within 1.5
  years" vs "deviations up to 9 years" for the originals.
- **reliage check:** on GSE55763 duplicate pairs, PC-clock ICC(2,1) ≥ 0.90
  (Koo–Li "excellent"). *(Requires PC-clock scores; via methylCIPHER, or PC
  coefficients.)*
- **Sources:** Higgins-Chen 2022 (Nature Aging); reliability paper 2025.

### A2. PC version out-reliables its own original (ordering test)
- **Published claim:** the entire point of PC-clocks — original clocks are noisy,
  PC versions are not. Original PhenoAge/Hannum technical reliability is only
  "good" (ICC ≈ 0.7–0.8); PC versions reach "excellent".
- **reliage check:** on the same public replicate data, `ICC(PCPhenoAge) >
  ICC(PhenoAge)` and `ICC(PCHannum) > ICC(Hannum)`; originals land ~0.7–0.8,
  PC versions ≥ 0.90. Ordering must hold even if absolute values differ by dataset.
- **Sources:** Higgins-Chen 2022; reliability paper 2025 (Hannum, PhenoAge,
  DNAm PhenoAge "generally in the 'good' range, ICC ∼0.7–0.8").

### A3. Within-subject error in years — originals ≫ PC
- **Published claim:** replicate deviations "up to 9 years" (original clocks) vs
  "within 1.5 years" (PC versions).
- **reliage check:** the **within-subject error** output (years) for original
  clocks is materially larger than for PC versions on public replicate data.
  This directly exercises Output 2 of the artifact spec (within-subject error).
- **Source:** Higgins-Chen 2022 (abstract, verbatim figures above).

---

## Tier B — Reference anchors (exact published numbers)

These are exact numbers to be *consistent with*; most were computed on non-public
data, so they are consistency/pattern checks, not exact reproductions.

### B1. Technical vs. biological reliability are essentially uncorrelated
- **Exact published value:** **r = 0.0168** (correlation between a clock's
  technical and biological reliability) — "largely independent."
- **reliage check:** given both technical-replicate and biological-replicate
  (repeat-draw) data, the per-clock technical ICC and biological ICC show
  near-zero correlation. This is the paper's headline and a strong pattern test.
- **Source:** reliability paper 2025 (verbatim r = 0.0168).

### B2. PCGrimAge is the best biological performer
- **Exact published value:** **PCGrimAge biological ICC = 0.76** (best; still only
  "good", not "excellent").
- **reliage check:** among clocks on biological-replicate data, PCGrimAge ranks
  top and lands ≈ 0.76 / "good" band.
- **Source:** reliability paper 2025.

### B3. Technically-excellent-but-biologically-poor clocks (the key warning)
- **Named clocks:** **GrimAgeV2** and **DunedinPACE** — "technically excellent
  but biologically unreliable"; "poor" under acute stress.
- **reliage check:** for these clocks, technical ICC ≥ 0.90 (excellent) AND
  biological ICC falls to "poor/moderate" — the split the tool must surface.
  This is exactly the ICC(2,1)-absolute-agreement failure-mode `reliage` is built
  to catch (cf. the quickstart drift demo).
- **Source:** reliability paper 2025.

### B4. Biological reliability ceiling
- **Exact published range:** most clocks biological ICC ≈ **0.4–0.7**, **no clock
  reaches "excellent"** biologically.
- **reliage check:** on biological-replicate data, all clocks < 0.90; the
  distribution centers in moderate/good, not excellent.
- **Source:** reliability paper 2025.

### B5. Koo–Li banding (sanity)
- **Exact thresholds:** Excellent ≥ 0.90, Good ≥ 0.75, Moderate ≥ 0.50, else Poor.
- **reliage check:** already implemented (`reliage.icc.koo_li_band`); unit-tested.
  Included here so the band definitions are traceable to the source the
  reliability papers use.
- **Source:** Koo & Li 2016, as used by both papers.

---

## Still to pin down (needs manual figure/supplement access)

The **exact per-clock ICC table** from Higgins-Chen 2022 (original vs PC value
for Horvath1, Horvath2/SkinBlood, Hannum, PhenoAge, GrimAge, DNAmTL, DunedinPoAm)
is in that paper's figures/supplementary tables, which sit behind an interactive
access wall not fetchable here. **Action:** open Higgins-Chen 2022 Fig 2 +
Supplementary Table and fill exact original→PC ICC pairs into `acceptance_cases.yaml`
(the A2/A3 exact values). Until then A1–A3 run as band/ordering tests, which is
sufficient for a first acceptance pass.

## How these get executed

`acceptance_cases.yaml` (this folder) encodes the machine-checkable expectations.
Once GSE55763 (and later SATSA) scores are computed, a real-data acceptance test
loads the YAML and asserts each case. Tier A must pass to claim "same
capabilities as the published technical-reliability results"; Tier B patterns
(B1, B3) require biological-replicate data and are the second milestone.

## Tier B (biological reliability) — public dataset candidates

Biological reliability needs **repeat draws from the same person over a short
interval** (not technical replicates). "Short interval" is not one thing — pick
the dataset to match the question:

| Interval | Question it tests | Public candidate | Status |
|---|---|---|---|
| **Hours (within-day)** | Do time-of-day / diurnal rhythm move the clock? (closest to the 2025 paper's meals/stress tests) | Diurnal blood-methylation data behind *"Epigenetic age oscillates during the day"* (Koncevičius, Aging Cell 2024) and *"Daily rhythm in DNA methylation…"* (2025) — both reanalyze public within-day repeat-sampled blood methylation | **Exact accession not yet pinned** (papers behind access wall); high fit — worth resolving |
| **~1 day (acute perturbation)** | Does an acute perturbation destabilize the clock? | **E-MTAB-4664** (ArrayExpress) — 16 healthy subjects, within-subject, normal-sleep vs total sleep-deprivation, **blood**, public. Plus referenced **E-GEOD-49065 / GSE49065** (10 healthy male donors, public) | **Confirmed public** |
| **Weeks–months** | Medium-term within-person stability | *"Agreement in DNA methylation across batches, tissues, and time"* (2017); MDPI 2023 whole-blood/buccal longitudinal | Leads; accessions not yet pinned |

**Important methodological caveat.** Several of these are *perturbation* studies
(sleep deprivation, stress). Within-person variation there mixes **natural
fluctuation** with the **deliberate intervention effect**. For a clean biological
*reliability* ICC, use the **stable/control arm** (normal-sleep timepoints, or
diurnal-under-normal-conditions samples) — the perturbation arm answers a
different question (does X *move* the clock = responsiveness), which is related
but distinct. Same small-n caveat as the technical side (n ≈ 10–16 → wide CIs →
pattern-level acceptance, not exact numbers).

**Recommended first Tier-B dataset:** resolve the diurnal accession (best fit to
the published biological-reliability finding); E-MTAB-4664's normal-sleep arm is
a confirmed-public fallback available immediately.

## Sources

- Reliability paper (2025): https://www.biorxiv.org/content/10.1101/2025.10.13.682176v2.full
- Higgins-Chen et al., PC-clocks, Nature Aging (2022): https://www.nature.com/articles/s43587-022-00248-2
- ComputAgeBench: https://github.com/ComputationalAgingLab/ComputAge
- GSE55763 (Lehne 2015): https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE55763
- SATSA: https://www.ebi.ac.uk/arrayexpress/experiments/E-MTAB-7309
- Koo & Li (2016), J Chiropr Med — ICC reporting guideline.
