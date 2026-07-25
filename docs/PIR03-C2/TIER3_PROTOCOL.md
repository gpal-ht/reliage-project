# Tier-3 — Published-Reference Agreement (PROTOCOL)

**Status:** protocol locked before the comparison is run (P1). Evidence dimension:
*published-reference agreement* → moves **CLAIMS #7**. Milestone 001
(`v0.3.1-scientific-baseline`) is the frozen input; this experiment does not modify it.

## Central question
Do reliage's frozen M1 GSE55763 results agree with the **published Higgins-Chen (2022)**
reliability figures within prespecified tolerances?

## Hypotheses
- **H0:** reliage's results deviate from the published figures beyond tolerance.
- **H1:** reliage reproduces the published figures within tolerance.
Both outcomes are acceptable; a recorded "not met" from a correct run is a valid finding.

## Critical design fact — this is a SAME-COHORT reproduction
Higgins-Chen's technical-reliability analysis used the **Lehne et al. 2015 technical
replicates = GSE55763**, which is the dataset M1 independently rebuilt. Therefore:
- **Absolute replicate-difference statistics** (median / max |rep1 − rep2|) are directly
  comparable (spread-independent).
- **Raw ICC is also comparable here** (same cohort → same between-subject spread), unlike the
  general cross-cohort case where only spread-independent statistics may be compared.
Residual differences can still arise from preprocessing/normalization, the exact replicate
subset used, imputation of missing clock CpGs, and GrimAge V1-vs-V2 details — these are the
expected sources of any tolerance miss and must be named, not hand-waved.

## Reference values (PINNED — from `acceptance/published_reference_cases.yaml`, Higgins-Chen 2022)
Primary (statistic RESOLVED — REF-HC2022-ABSDIFF), original clocks, years:

| Clock | Published median |Δ| | Published max |Δ| |
|---|---|---|
| Horvath1 | 2.1 | 5.4 |
| GrimAge | 0.9 | 2.4 |
| others (Hannum, PhenoAge) | in [0.9, 2.4] | in [4.5, 8.6] |

Secondary (REF-HC2022-ICC — *text-extracted, pending exact figure confirmation*):
- PC raw ICC **> 0.99** (all four PC clocks); PC age-acceleration ICC **≈ 0.97**.
- Horvath1 original: raw ICC **0.945**, age-accel ICC **0.817**.
- PC absolute replicate differences fall within **~0–1.5 yr** for the majority.

Reference confirmation task (before the verdict is finalized): attempt to confirm the exact
published per-clock figures against the paper/supplement; if unconfirmable, the ICC anchors
remain "text-extracted" and the verdict leans on the RESOLVED absolute-difference statistics.

## Metrics reliage will compute (from the FROZEN M1 outputs)
From `datasets/GSE55763/out/` (M1, tag `v0.3.1-scientific-baseline`) and its
`robustness/pair_diffs.csv`:
- per original clock: **median** and **max** absolute replicate difference;
- per PC clock: median / max / fraction ≤ 1.5 yr absolute replicate difference;
- raw ICC(2,1) and age-acceleration ICC (already in `leaderboard.csv` / `leaderboard_ageaccel.csv`).

## Prespecified tolerances (locked BEFORE comparison)
Set on principled measurement grounds, not reverse-engineered from M1:

| Comparison | Pass tolerance |
|---|---|
| Median \|Δ\| (Horvath1, GrimAge) | within **±0.5 yr** of the published value |
| Max \|Δ\| (Horvath1, GrimAge) | within **±1.5 yr** of the published value (max = one extreme pair, noisier) |
| Median / max \|Δ\| (Hannum, PhenoAge) | **inside** the published "others" ranges [0.9, 2.4] / [4.5, 8.6] |
| PC raw ICC (all four) | **≥ 0.985** (published ">0.99"; allow 3-dp rounding) |
| PC age-accel ICC (all four) | **0.97 ± 0.03** → [0.94, 1.00] |
| Horvath1 original raw ICC | within **±0.02** of 0.945 |
| Horvath1 original accel ICC | within **±0.03** of 0.817 |
| PC \|Δ\| majority within 0–1.5 yr | **≥ 75%** of PC pairs ≤ 1.5 yr |

## Verdict rule (prespecified)
- **PASS (H1):** all *primary* checks (median + max \|Δ\| for clocks with a specific published
  value, i.e. Horvath1 and GrimAge) within tolerance **and** the PC-ICC band checks hold.
- **PARTIAL:** primary passes but ≥1 secondary check misses (report which + likely cause from
  the named sources above).
- **NOT MET:** any primary check outside tolerance (recorded honestly with cause analysis).

## Deliverables
1. `TIER3_PROTOCOL.md` (this document, locked).
2. `TIER3_COMPARISON.md` — reliage vs published, per metric, with pass/fail against tolerance.
3. `datasets/GSE55763/out_tier3/` — the computed reliage-side numbers (median/max \|Δ\| table).
4. CLAIMS #7 status update (Supported / Partial / Not-met, scoped).
5. **If PASS/PARTIAL:** ratify the tiered reproduction gate into `SCORING_DECISION.md`
   (the tracked follow-up: T1 reproduce published stats ✓ · T2 independent GEO rebuild ✓ ·
   T3 consistency within tolerances).

## Scope / out of scope
- In: the 4 M1 clock pairs on GSE55763 vs Higgins-Chen 2022 figures.
- Out: other datasets/platforms/clocks; the "technical vs biological reliability r=0.0168"
  and biological-ICC anchors (REF-TB-CORR, REF-PCGRIMAGE-BIO) — those are biological-reliability
  (Tier B/C/D, v2), not this dimension.

## Principles applied
P1 (protocol locked before results), P4 (this is the *scientific/reference* evidence layer,
distinct from software/statistical), P6 (tolerances + scope explicit), P7 (exists to move CLAIMS #7).
Comparison uses spread-independent statistics as primary (per the cross-cohort caution recorded in
`TECHNICAL_REPORT_v0.1.md §10`), with raw ICC admissible here only because the cohort is the same.
