# reliage — Engineering Status Review

_Contribution PIR03-C2 (Frontier Research Foundry). Status as of this session:
reliage v0.2.1, protocol locked, acceptance spec restructured, no real data scored yet._

---

## 1. Mission

**Mission (one paragraph).** `reliage` is an open, reproducible benchmark that
quantifies the *reliability* of epigenetic aging clocks — how much a clock's output
changes when the same biological material is measured more than once — and reports
it in a form a researcher can act on (intraclass correlation, absolute
within-subject error, and the individual change a clock can actually detect). It is
the reliability companion to ComputAgeBench (which benchmarks clock *accuracy*), and
it deliberately operates only on a table of clock *scores* plus a replicate map, so
it is independent of any particular methylation pipeline, clock package, or even
biomarker modality.

**Exact scientific problem.** Epigenetic clocks are used to track whether an
intervention changes "biological age," but a clock's output includes technical
measurement noise. If that noise is large relative to the effect being measured, the
clock cannot detect the effect. reliage measures that noise floor per clock and
tests the published claim that principal-component (PC) transformed clocks suppress
it relative to their original versions.

**Why it matters.** Reliability is the precondition for a clock being usable in a
trial or longitudinal study. A 2-year intervention effect is unmeasurable through a
±5-year measurement error. The reliability science exists (Higgins-Chen 2022; a 2025
platform), but there is **no open, rerunnable tool** that reproduces it from public
data — the comprehensive one (TranslAGE) is gated. That openness/reproducibility gap
is the contribution.

**Claims reliage will validate (technical reliability, GSE55763):**
- PC-transformed clocks have **lower within-subject technical error** than their
  originals (primary endpoint: within-subject variance ratio < 1).
- PC clocks reach **higher ICC** than originals on the same replicate pairs.
- The published **median/max absolute replicate differences** are reproducible on
  public data with open code.

**Claims reliage deliberately does NOT answer:**
- Whether a clock is stable across **repeat blood draws on different days**
  (biological reliability — Tier B, future).
- **Longitudinal** stability across meaningful time (Tier C).
- **Responsiveness** to acute perturbation (Tier D) — a real biological shift, not
  unreliability.
- Whether a clock is **accurate / biologically valid / causal** — out of scope
  (accuracy is ComputAgeBench's job; validity/causality need wet-lab evidence).
- Cross-platform (450K vs EPIC) or cross-tissue reliability (future).

---

## 2. Current Architecture (end-to-end)

```
STAGE 1  Acquire methylation data        [EXTERNAL: GEO / ArrayExpress]
            beta matrix (samples × CpGs) + sample metadata + provenance
               │
STAGE 2  Calculate clock scores          [EXTERNAL: methylCIPHER (R) / pyaging (Py)]
            per-clock scores; record implementation, version, CpG coverage,
            imputation, output UNIT
               │
               ▼
STAGE 3  Versioned SCORE TABLE  ─────────────────────────┐   ← reliage boundary starts here
            long-form: sample_id, clock_id, score, unit, │
            implementation, version, %cpg, imputation     │
               │                          replicate map ──┤
               ▼                                          │
STAGE 4  Reliability analysis  ◀──────────────────────────┘
            validate pairing → build n×k matrices →
            ICC(2,1)+CI (+sensitivity 1,1/3,1) · within-subject SD ·
            mean/median abs diff · [Bland-Altman] · Individual MDC95 ·
            [variance ratio + bootstrap CI for PC vs original]
               │
               ▼
STAGE 5  Scientific verdict  [PLANNED]
            per-pair + joint: supported / directionally / partially /
            not supported / inconclusive
               │
               ▼
STAGE 6  Reports  [PLANNED]
            results.csv/json (long-form) → HTML leaderboard, forest plot,
            paired original↔PC plot, Bland-Altman; PROTOCOL + provenance + limitations
```

**Stage explanations.** *1 Acquire* and *2 Score* are **external by design** — reliage
never touches CpGs or clock formulas, so it is reusable for proteomic/metabolomic
clocks. *3 Score table* is the formal contract (long-form preferred for provenance).
*4 Reliability* is the implemented core. *5 Verdict* converts metrics into a
non-binary disposition (planned). *6 Reports* renders machine-readable results into
human artifacts (planned).

---

## 3. Current State (subsystem classification)

| Subsystem | State | Notes |
|---|---|---|
| Architecture | ✅ Complete | Five external + reliage-internal stages defined; score-table boundary clean |
| Input schema (score table) | 🟡 Partial | Wide-form accepted (`scores` DataFrame + replicate map). Long-form provenance schema (unit/impl/version/coverage) **specified, not enforced** |
| Score table interface | 🟡 Partial | `score_samples()` + `linear_clock`; no long-form ingest/validator yet |
| Replicate map | 🟡 Partial | `replicate_groups_from_metadata()`; drops <k deterministically; **no explicit audit/counts report** (VAL-PAIRING/DATA-AUDIT pending) |
| Validation (tool) | 🟡 Partial | selfcheck (2 gates) + pytest fixtures; 12 validation_cases defined, ~2 passing, rest pending |
| Reliability metrics (container) | 🟡 Partial | ICC, SD, mean-abs-diff, MDC95 in leaderboard; median/Bland-Altman/variance-ratio missing |
| ICC | ✅ Complete | ICC(1,1)/(2,1)/(3,1) via ANOVA, F-based CIs, Koo–Li bands; verified vs Shrout & Fleiss |
| MDC95 | ✅ Complete | `1.96·√2·SEM`, individual-level; property on ICCResult |
| Within-subject SD | ✅ Complete | `sqrt(MSE)`; = SD(diff)/√2 for k=2 (equivalence test pending) |
| Mean absolute difference | ✅ Complete (v0.2.1) | `mean|rep1−rep2|` |
| Median difference | ❌ Not started | — |
| Bland–Altman | ❌ Not started | limits of agreement + plot |
| Variance ratio (PC/original) | ❌ Not started | **the primary endpoint** — not yet implemented |
| Bootstrap | ❌ Not started | needed for paired-contrast CIs |
| Scientific verdict | ❌ Not started | verdict engine over replication_hypotheses.yaml |
| Reporting (CSV/JSON/HTML) | ❌ Not started | leaderboard only renders markdown today |
| CLI | ❌ Not started | library-only; no entry point |
| Testing | 🟡 Partial | selfcheck passes; pytest suite exists (not runnable offline here); cross-impl checks pending |
| Documentation | ✅ Strong | README, PROTOCOL, CLOCK_MANIFEST, INPUT_OUTPUT, acceptance/, DATASETS, dataset scaffolds |

---

## 4. Reliability Metrics (per metric)

**ICC (intraclass correlation).**
- *Why:* does the clock consistently distinguish people despite replicate noise.
- *Formula (ICC(2,1), primary):* `(MSR−MSE) / (MSR+(k−1)·MSE+(k/n)(MSC−MSE))` from a
  two-way ANOVA; sensitivities ICC(1,1), ICC(3,1).
- *Assumptions:* subjects random; occasion random (ICC2) — justified because we want
  generalization to arbitrary future measurement occasions; absolute agreement.
  Depends on between-person heterogeneity (why absolute error is reported alongside).
- *Status:* ✅ implemented + verified (Shrout & Fleiss 0.17/0.29/0.71).
- *CI:* F-distribution (McGraw & Wong 1996), implemented.
- *Tests planned:* cross-implementation vs R `psych::ICC` / `pingouin`; CI match; raw
  vs age-acceleration flavor.

**Within-subject SD (SEM).**
- *Why:* absolute technical error in the clock's own unit — actionable where ICC isn't.
- *Formula:* `sqrt(MSE)` (two-way residual); for k=2, `SD(rep1−rep2)/√2`.
- *Assumptions:* homoscedastic error across the range (checked via Bland–Altman).
- *Status:* ✅ implemented. *CI:* none yet (bootstrap planned). *Tests planned:*
  equivalence `sqrt(MSE)` == `SD(diff)/√2`; hand-calc fixture.

**Mean absolute difference.**
- *Why:* the intuitive "typical `|rep1−rep2|`."
- *Formula:* `mean|rep1−rep2|`. *Assumption:* duplicate design (k=2).
- *Status:* ✅ (v0.2.1). *CI:* bootstrap planned. *Tests planned:* hand-calc fixture.

**Median difference.**
- *Why:* robust to outliers; the statistic Higgins-Chen actually report per clock.
- *Formula:* `median|rep1−rep2|`. *Status:* ❌. *Tests planned:* fixture + match to
  REF-HC2022-ABSDIFF (Horvath1 2.1 yr, GrimAge 0.9 yr).

**MDC95 (individual).**
- *Why:* the smallest change in one person exceeding noise (95%).
- *Formula:* `1.96·√2·SEM`. *Assumption:* normal error, individual-level (NOT trial).
- *Status:* ✅. *CI:* inherits from SEM bootstrap (planned). *Tests planned:* exact
  arithmetic identity.

**Bland–Altman (limits of agreement).**
- *Why:* reveals systematic run-to-run bias, magnitude-dependent error, outliers that
  ICC/bars hide.
- *Formula:* bias = `mean(rep1−rep2)`; LoA = `bias ± 1.96·SD(rep1−rep2)`.
- *Assumptions:* approx-normal differences, constant variance (the plot tests this).
- *Status:* ❌. *Tests planned:* fixture; bias/LoA hand-calc.

**Variance ratio (primary endpoint).**
- *Why:* directly tests the PC mechanism (noise reduction), less spread-dependent
  than ICC. `< 1` favors PC.
- *Formula:* `var_within(PC) / var_within(original)` (= `MSE_PC/MSE_orig`, same subjects).
- *Assumptions:* same subjects/pairs for both clocks (paired); independent replicate error.
- *Status:* ❌ **highest-value missing metric.** *CI:* **paired bootstrap over subjects**
  (planned) — resample pairs, recompute ratio, percentile CI. *Tests planned:*
  synthetic data with known variance components recovers the ratio + CI coverage.

---

## 5. Scientific Assumptions

| Assumption | Statement | Status |
|---|---|---|
| Technical-replicate definition | The two GSE55763 measurements are the same biological sample re-assayed (no biological aging between them) | **Established** (GEO record: measured in duplicate) |
| No biological change within a pair | score difference ≈ pure technical error | **Established** for technical replicates; **weak** for any repeat-draw (Tier B+) |
| Replicate independence | the two measurements are independent draws of the error process | **Reasonable**, but they are **cross-batch by design** — so error includes batch; state as "reliability under cross-batch conditions" |
| Normal / homoscedastic error | error ~normal, constant variance across clock range | **Reasonable**; Bland–Altman will test it (magnitude-dependence is plausible) |
| ICC occasion = random | measurement occasion is a random draw (→ ICC2) | **Reasonable**; sensitivity ICC(3,1) reported in case batches are "fixed" |
| Bootstrap resampling unit = subject/pair | resample pairs (not measurements) for paired-contrast CIs | **Reasonable/established** for clustered data |
| Missing-probe / imputation neutrality | imputing missing CpGs doesn't differentially advantage PC vs original | **Weak/unknown** — must use identical policy per pair; coverage is a gate |
| Clock-implementation identity | "Horvath" means the same thing across packages | **Weak** — pin package/version/commit; two impls differ |
| Clock-score independence (for tech-vs-bio r) | clocks treated as independent points | **Weak** — clocks share CpGs/training/families |
| Small-n adequacy | 36 pairs suffices for direction, not tight point estimates | **Reasonable** for direction; **weak** for ranking by small differences |

---

## 6. Validation Plan (how we know reliage is correct)

Four layers, mapped to `acceptance/`:

1. **Software correctness** (`validation_cases.yaml`, must-pass): pairing exactly once;
   deterministic drop of incomplete subjects with reported counts; row-order
   invariance; determinism; units preserved; missing/malformed handled; the executable
   GSE55763 replicate-manifest audit.
2. **Statistical correctness:** ICC matches Shrout & Fleiss canonical values (✅ passing)
   AND an independent implementation (R `psych`/`pingouin`) on synthetic data; CI
   coverage checked by simulation; within-subject SD equivalence (`sqrt(MSE)`==`SD(diff)/√2`);
   MDC95 identity; variance-ratio recovery on data with known variance components;
   bootstrap CI coverage.
3. **Replication correctness** (`replication_hypotheses.yaml`, verdict-based): prespecified
   directional hypotheses with tolerances declared *before* seeing results; verdict ∈
   {supported, directionally, partially, not, inconclusive}.
4. **Comparison against published numbers** (`published_reference_cases.yaml`): reproduce
   the *statistic the source actually used* (median/max abs diff — resolved) under source
   conditions; feed the published table to recover r=0.0168 (exact-repro test).

**Bottom line:** correctness = layers 1–2 pass (deterministic, cross-checked math) on
synthetic + fixed fixtures; scientific standing = layers 3–4 reported honestly, where a
"not supported" verdict from a correct run is a valid result, not a bug.

---

## 7. Public Dataset Inventory

| Accession | Name | Tissue | Replicate type | Samples | Why chosen | Expected analyses | Tier |
|---|---|---|---|---|---|---|---|
| GSE55763 | Lehne 2015 | blood | technical (cross-batch duplicates) | 2,664 indiv; **36 dup pairs** | Public 450K anchor; used as PC-Clocks example | ICC, within-subj SD, median/max abs diff, variance ratio, PC↔original | **Tier 1** |
| — (GitHub) | PC-Clocks example (Lehne subset) | blood | technical | 36 pairs | Small/fast debug of full pipeline | Same as above, debug path | **Tier 1** |
| E-MTAB-4664 | Acute sleep deprivation | blood | repeat draw ~1 day (normal + sleep-dep arms) | 16 | Only confirmed-public short-interval repeat draw | Tier B stability (normal arm), Tier D responsiveness (sleep arm) | Tier 2 |
| GSE49065 | Sleep-dep companion | blood | within-subject timepoints | 10 | Public companion to above | Tier B/D | Tier 2 |
| (TBD) | Diurnal within-day methylation | blood | hours (multi-timepoint) | ~small | Best fit to published *biological* reliability | Tier B (within-day) | Tier 2 (accession to pin) |
| E-MTAB-7309 | SATSA | blood | **longitudinal** (years) | many | Longitudinal trajectory stability | **Tier C** (NOT technical/biological) | Tier 3 |

Tier 1 = must-have for the current technical-reliability milestone. Tier 2 = biological
(short-interval) future work. Tier 3 = longitudinal, a distinct question.

---

## 8. Download Plan

**Constraint (stated plainly):** I cannot pull dataset bytes from inside this cloud
sandbox — external-URL fetching is restricted here and the sandbox is ephemeral with a
fixed disk allowance. So I have **built and organized the directory structure and the
runnable download tooling**; the bytes are pulled where the data will live.

Created scaffold (`reliage/datasets/`):
```
datasets/
  README.md                     (index)
  pcclocks_example/  raw/ processed/ metadata/  README.md
  GSE55763/          raw/ processed/ metadata/  README.md
```
Runnable download: `reliage/data/download_data.sh [pcclocks|gse55763|...]` + `data/DATASETS.md`.

Per Tier-1 dataset (full detail in each dir's README):
- **pcclocks_example** — source: `git clone MorganLevineLab/PC-Clocks` → `Example_PCClock_Data.RData`;
  preprocessing: extract betas+annotation; mapping: identify duplicate pairs; issues:
  author-prepared (not independent provenance), cross-check vs GEO.
- **GSE55763** — source: GEO suppl dir / GEOparse; preprocessing: normalized betas, subset
  72 replicate samples, record pipeline; mapping: 36 pairs via metadata + executable audit;
  issues: several GB, cross-batch by design, 450K only, wide CIs at n=36.

---

## 9. Remaining Engineering Work (backlog)

**Critical path (blocks the first real result / publishable claim):**
| Item | Difficulty | Depends on | Est. |
|---|---|---|---|
| Variance-ratio metric + paired bootstrap CI | Med | ICC core (done) | 2–3 d |
| Long-form score-table ingest + units schema (per-clock unit, impl/version, coverage) | Med | — | 2–3 d |
| Pairing audit + counts + VAL-DATA-AUDIT | Low-Med | replicate map (done) | 1–2 d |
| Cross-implementation ICC/CI validation vs R psych/pingouin | Med | — | 2 d |
| Median diff + Bland–Altman (LoA + values) | Low | metrics core | 1–2 d |
| Verdict engine over replication_hypotheses.yaml | Med | metrics + bootstrap | 2–3 d |
| Score real data: methylCIPHER **or** pyaging on pcclocks_example → CSV | Med | scorer decision (OPEN) | 2–4 d |
| GEO rebuild + matrix cross-check (public-repro claim) | Med-High | above | 3–5 d |

**Nice to have:**
| Item | Difficulty | Est. |
|---|---|---|
| HTML leaderboard + forest / paired / Bland–Altman plots (dataviz) | Med | 2–3 d |
| CLI (`reliage run scores.csv --map map.csv`) | Low | 1 d |
| results.csv/json long-form emitters | Low | 1 d |
| Age-acceleration ICC flavor alongside raw | Low-Med | 1–2 d |

**Future work:** Tier B/C/D datasets + biological-reliability mode; multi-modal
(proteomic/metabolomic) clocks; EPIC/cross-platform; PyPI release + JOSS paper;
living leaderboard; upstream PR to ComputAgeBench.

---

## 10. Risks

**Statistical:** (a) small n=36 → wide CIs → over-reading rank differences → *mitigate:*
report CIs, verdicts, direction not rank; (b) ICC-form mis-specification → *mitigate:*
prespecified ICC(2,1) + sensitivities; (c) bootstrap resampling wrong unit → *mitigate:*
resample subjects/pairs, test CI coverage on synthetic data; (d) heteroscedastic error
→ *mitigate:* Bland–Altman.

**Engineering:** (a) clock-implementation mismatch across packages → *mitigate:* pin
package/version/commit in the score table, clock manifest; (b) missing-probe imputation
differing across a pair → *mitigate:* coverage as a gate, identical policy per pair;
(c) R/Python boundary fragility → *mitigate:* CSV contract, or pyaging pure-Python path;
(d) silent sample drops → *mitigate:* pairing audit with explicit counts.

**Scientific:** (a) confirmation bias (outcome-shaped acceptance) → *mitigate:* verdict
framework, tolerances pre-registered; (b) conflating technical with biological reliability
→ *mitigate:* four-tier taxonomy; (c) treating responsiveness as unreliability →
*mitigate:* Tier D separated.

**Reproducibility:** (a) reproducing from author-prepared RData ≠ public repro →
*mitigate:* GEO rebuild + matrix cross-check before the claim; (b) preprocessing drift →
*mitigate:* record normalization/provenance; (c) hosted-file disappearance → *mitigate:*
GEO as canonical source; (d) environment drift → *mitigate:* lockfiles, one-command env.

---

## 11. What would make reliage publication-quality?

Still missing for "the reference open-source reliability benchmark":
1. **A real result** — technical reliability reproduced on GSE55763 from GEO with a
   verdict (nothing is scored yet).
2. **Independent statistical validation** — cross-checked ICC/CI/variance-ratio/bootstrap
   vs a trusted package, with CI-coverage simulations.
3. **The primary endpoint implemented** (variance ratio + paired bootstrap) — the metric
   that directly tests the PC mechanism.
4. **Provenance rigor** — clock manifest with versions/commits, coverage gates, GEO
   rebuild, data-provenance docs, environment lockfiles, one-command reproduction.
5. **Honest uncertainty in the outputs** — CI-aware bands, no lone colored chips.
6. **Reporting** — HTML leaderboard + paired/Bland–Altman/forest plots from machine-readable
   results.
7. **Extensibility proven** — a second clock family end-to-end; ideally a non-methylation
   modality to demonstrate the score-table generality.
8. **Distribution** — PyPI + JOSS software paper (citable DOI) + upstream/interop with
   ComputAgeBench; a living, updatable leaderboard.
9. **CI/tests green** in a public repo (the pytest suite runnable in CI, not just selfcheck).

---

## 12. Final Recommendation

- **Are we solving the right problem?** Yes — an open, reproducible reliability benchmark
  fills a real gap (the comprehensive existing tool is gated), and it is squarely on the
  Foundry's reproducibility mission. Caveat accepted: it is a *reproducibility/openness*
  contribution, not novel science.
- **Is the current architecture sufficient?** Yes. The score-table boundary (reliage
  independent of CpGs/clock packages) is the right decision and needs no rework; the gaps
  are missing *components* (variance ratio, verdict, reporting), not architectural flaws.
- **Single highest-priority ENGINEERING task next:** implement the **within-subject
  variance-ratio metric with a paired bootstrap CI** — it is the primary endpoint, it's
  currently missing, and every downstream verdict/report depends on it.
- **Single highest-priority SCIENTIFIC validation next:** **score the pcclocks_example
  (Lehne) replicates and run the first PC↔original technical-reliability contrast**,
  checking reliage against the resolved published statistics (median/max abs diff;
  PC raw ICC >0.99) — the first end-to-end evidence the tool works on real data. (This
  needs the open **scorer decision: methylCIPHER vs pyaging** — the one blocking choice.)
- **What to avoid adding (to stay focused):** biological/longitudinal/responsiveness
  tiers (B/C/D), cross-platform/multi-modal generality, a heavy web app, or any
  accuracy/validity/causal analysis — all are scope creep until technical reliability on
  GSE55763 is reproduced, verdicted, and reported end to end.
