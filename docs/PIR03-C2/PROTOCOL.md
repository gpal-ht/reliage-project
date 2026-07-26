# PIR03-C2 — Locked Protocol (Milestone 0)

> 🔒 **v1 FROZEN (2026-07-26)** — see [`PROTOCOL_FREEZE.md`](PROTOCOL_FREEZE.md). Decisions here are
> immutable for v1; change only via a dated, versioned amendment. (The `v1.0` release tag is held
> pending independent reproducibility, CLAIMS #8.)

Purpose: freeze analytic decisions **before** producing results or charts, so the
reproduction is confirmatory, not outcome-shaped. This document supersedes the
looser framing in earlier notes where they conflict. It incorporates the expert
review of the plan (accepted corrections recorded inline).

Scope of this experiment: **technical reliability of epigenetic clocks on
GSE55763** (36 duplicate pairs, two measurements processed in separate batches).
Not biological reliability, not cross-platform, not longitudinal (those are Tier B).

---

## 1. Clock set (frozen)

See `CLOCK_MANIFEST.csv`. The **primary comparison** is the four clock families
with a clean original↔PC pair runnable in-package in methylCIPHER:
**Horvath1, Hannum, PhenoAge, GrimAge**. Secondary/among caveats:
- **DunedinPACE** — no PC variant; **unit is PACE (biological years per
  chronological year), not years** — reported separately, never in a "years" column.
- **DNAmTL** — unit is telomere-length (kb) proxy, not years; PC variant to be
  verified before promising the pair.

No original↔PC pair is claimed until it has actually run on ≥5 example samples
(`verified_runs_5_samples` in the manifest flips from `pending_local` to a commit hash).

**Scorer:** two options, both acceptable; the run records which was used.
- **methylCIPHER (R)** — definitive source from the originating lab; computes
  originals + PC via `calcPCClocks`; DunedinPACE needs an external install.
- **pyaging (Python)** — pure-Python alternative (PCGrimAge, GrimAge2, DunedinPACE
  confirmed); removes the R/Python boundary. Broader-catalogue coverage of the
  other originals to be confirmed against its Clock Catalogue.
Recommendation: methylCIPHER for the headline original-vs-PC pairs (authoritative);
pyaging as a cross-check. **The same imputation policy must be used for both the
original and PC member of a pair** (see §5) or a reliability difference could be an
imputation artifact.

## 2. Result schema (units are first-class)

A single "error in years" column is invalid across clocks (DunedinPACE, DNAmTL).
Every numeric result carries its unit:

```
clock, variant, scorer, scorer_version/commit,
estimate, estimate_unit,
icc_primary, icc_primary_form, icc_ci_low, icc_ci_high,
icc_sensitivity (form->value...),
within_subject_sd, within_subject_sd_unit,
mean_abs_diff, mad_unit,
p95_abs_diff,
coeff_of_repeatability,
bland_altman_bias, bland_altman_loa_low, bland_altman_loa_high,
mdc95, mdc95_unit,
n_pairs, pct_required_cpgs_present, imputation_method, warnings, dataset, tier
```

## 3. Reliability metrics (definitions frozen)

- **ICC — primary: ICC(2,1)** (two-way random effects, absolute agreement,
  single measure). Justification: we want reliability that generalizes to
  *arbitrary future measurement occasions*, so measurement occasion (here: batch)
  is treated as a random draw, and we care about absolute agreement (do the two
  values *agree*, not merely correlate). **Sensitivity:** also report ICC(1,1) and
  ICC(3,1); if the batch structure is better viewed as two fixed assay runs, ICC(3,1)
  is the relevant comparator. The harness reports the primary plus both sensitivities
  — never a silent single form. (Koo & Li 2016: form, definition and unit must be stated.)
- **ICC is not a pure error metric** — it scales with between-person heterogeneity,
  so it is always reported *alongside* absolute error, never alone.
- **Within-subject SD (SEM)** — for duplicate pairs: `SD(differences)/√2`.
  This is *the* named "within-subject error." (Note: the reliage v0.2 ANOVA
  `sqrt(MSE)` is algebraically this for k=2; the pairwise-difference form is the
  canonical statement and what the schema reports.)
- Also report, per the review: **mean absolute replicate difference**, **95th
  percentile absolute difference**, **coefficient of repeatability** (1.96·√2·SEM),
  and **Bland–Altman limits of agreement** (bias ± 1.96·SD_diff), which reveal
  systematic run-to-run bias, magnitude-dependent error, and outliers that a bar can't.
- **MDC95 (individual smallest detectable change)** = `1.96·√2·SEM`. This is the
  core reliability output and is named **MDC95**, NOT "minimum detectable
  intervention effect." (Correction accepted: the earlier "MDE" label overclaimed.)
  A separate, clearly-labelled *trial-design* calculator may report
  `minimum detectable mean effect = f(SEM, n, power, α, design)` — illustrative only,
  not part of the core reliability verdict.

## 4. Acceptance framework (three separate kinds of test)

Do not collapse software correctness, reference reproduction, and scientific
findings into one pass/fail.

**(a) Software-correctness tests — must pass.** Every replicate paired exactly
once; no silent sample drops; units declared on every number; ICC matches a
trusted reference (Shrout & Fleiss canonical values — already passing) and an
independent implementation on synthetic data; CIs match an independent
implementation; deterministic re-runs; malformed/missing pairs handled.

**(b) Reference-reproduction tests — explicit, pre-registered tolerances.**
Compare against published values with direction + magnitude + tolerance declared
*before* seeing final output; the exact source figure/table and extracted numbers
stored in `acceptance_cases.yaml`. NOTE (correction accepted): the "≈9 years →
≈1.5 years" phrasing is an agreement-range/deviation statement, **not** a
within-subject SD target — it must not be asserted as an SD until the exact
statistic behind it is matched to the source.

**(c) Scientific findings — NOT hardcoded pass/fail.** Whether every PC clock
reaches 0.90, every original sits at 0.7–0.8, etc., are *findings*, not gates.

**Primary reproducibility verdict** (not binary):
- **Supported** — most prespecified PC↔original pairs improve in the expected
  direction and uncertainty is compatible with the published result.
- **Partially supported** — mixed direction, imprecise, or only some pairs reproduce.
- **Not reproduced** — expected advantage absent/reversed after verified implementation.
- **Inconclusive** — data/implementation/CIs don't support a decision.

## 5. Provenance & reproducibility staging

> ⚠ **Update (2026-07):** the fast-path example RData is **unavailable (Box link removed)**; M1 used
> the GEO full path directly. See `SCORING_DECISION.md` (gate superseded by a tiered gate, ratify at Tier-3).

- **Fast path** (debug/validate): PC-Clocks `Example_PCClock_Data.RData` (Lehne
  technical-replicate subset). Convenience/bootstrap only — an *intermediate
  artifact prepared by the original team*, not full public reproduction.
- **Full path** (before any "public end-to-end reproducibility" claim): retrieve
  **GSE55763 from GEO**, identify the 36 duplicate pairs, reproduce preprocessing,
  and **compare the independently-derived matrix against the example matrix**;
  document any preprocessing differences. Only after this is the public-repro claim earned.
- **Probe coverage is an acceptance gate, not a warning:** record
  `pct_required_cpgs_present` and the imputation method per clock; a pair is
  invalid if the original and PC members used different coverage/imputation.

## 6. Named risks (carried, mitigated)

1. **Clock-implementation mismatch** — record exact package, function, and
   version/commit for every score; two "Horvath"s can differ in preprocessing,
   age transform, missing-CpG handling, coefficients, normalization.
2. **Missing probes / imputation** — gate on coverage; identical policy across a pair.
3. **Batch structure** — the duplicates are deliberately cross-batch; results
   estimate reliability *under that setup*, stated as such.
4. **Small n (36 pairs)** — wide CIs; interpret by direction, absolute error, and
   uncertainty, not tiny point-estimate rank differences.
5. **ICC model selection** — primary ICC(2,1) justified above; report sensitivities.

## 7. Presentation (scoping rules)

- Title is scoped: **"Technical reliability of epigenetic clocks on GSE55763"** —
  never "Which clock can you trust?" (a clock can be technically reliable and
  biologically unreliable; technical ≠ biological, and the two are ~uncorrelated).
- Table columns: Clock | Variant | Unit | ICC | 95% CI | Within-subject SD | Mean
  abs replicate diff | MDC95 | valid pairs | %CpG present | impl version.
- Charts: (i) **paired original↔PC plot** (lines connecting the two variants) —
  shows the transformation's effect directly; (ii) **Bland–Altman per clock family**
  for absolute error (bias, magnitude-dependence, outliers) — more informative than
  bars; (iii) forest plot of ICC±CI as a secondary view.
- HTML is generated *from* the machine-readable results, never hand-maintained.

## 8. Revised milestone order (accepted)

0. **Lock protocol** (this doc) + `CLOCK_MANIFEST.csv`. ← current
1. **Validate reliage** independently on synthetic data with known variance
   components (ICC, CIs, within-subject SD, MDC95, Bland–Altman, malformed pairs,
   row-order invariance) vs a trusted R stats package. Implement the §2 units
   schema and §3 extra metrics here (deferred until the protocol is agreed).
2. **Fast-path scoring** on the example RData → score CSV + env lockfiles + clock
   manifest (commits) + probe-coverage report + pairing audit.
3. **Rebuild from GEO** (GSE55763); compare matrices; only now claim public repro.
4. **Analyze** without changing the protocol → ICC + CIs, absolute-error metrics,
   Bland–Altman, PC-vs-original contrasts, bootstrap CIs for the improvement,
   reproduction verdict.
5. **Publish scoped artifacts**: PROTOCOL.md, CLOCK_MANIFEST.csv, DATA_PROVENANCE.md,
   results.csv/json, RESULTS.md, generated HTML, static figures, one-command env.

## Accepted corrections from review (summary)
- "MDE" → **MDC95** (individual); trial-level MDE is a separate, labelled calculator.
- **Per-clock units** in the schema; DunedinPACE = pace units, DNAmTL = kb, not years.
- **ICC(2,1)** justified + report ICC(1,1)/ICC(3,1) sensitivities.
- "9→1.5 years" is not an SD assertion target.
- Acceptance split into software / reference-repro / scientific-findings; verdict is
  Supported/Partial/Not/Inconclusive, not binary.
- Public reproducibility earned only after **GEO rebuild**, not the authors' RData.
- Presentation scoped to GSE55763 technical reliability; add paired + Bland–Altman plots.
- Probe coverage is a **gate**; record implementation versions.
