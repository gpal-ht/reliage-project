# PIR03-C2 — What goes IN, what comes OUT

A concrete end-to-end view of the reliability experiment on a tiny
realistically-shaped example. Reproduce with
`python examples/input_output_walkthrough.py`. Nothing here is real biology — the
**shapes, units, and column meanings** are the point.

## The pipeline is FIVE stages (not four)

The replicate map does **not** feed clock scoring — it joins only at the
reliability step. This is deliberate: `reliage` depends on **neither methylation
data nor clock software**, only on a score matrix + a replicate map.

```
1. acquire methylation data ─▶ beta matrix
                                   │
2. calculate clock scores ─────────▼
                                clock implementation (methylCIPHER / pyaging)
                                   │
                                   ▼
                          3. versioned SCORE MATRIX ──────────┐
                                                              ├─ 4. reliability
                             replicate map ───────────────────┘     (ICC, abs error)
                                                              │
                                                              ▼
                                              5. present & interpret
                                              (leaderboard / figures / JSON + verdict)
```

---

## INPUT 1 — DNA methylation beta matrix

Rows = samples, columns = CpG sites, values in [0,1] (fraction methylated; 0.82 ≈
82% methylated at that site). Each subject is measured **twice** (`_a`, `_b`).
The matrix alone does **not** say which rows are repeats.

```
sample_id  cg_sig0 cg_sig1 cg_sig2 cg_sig3  cg_noise0 cg_noise1 cg_noise2 cg_noise3
P1_a         0.411   0.409   0.416   0.411      0.173     0.227     0.283     0.262
P1_b         0.403   0.397   0.404   0.410      0.065     0.192     0.130     0.161
...          (12 samples = 6 subjects x 2 replicates, 8 CpGs shown)
```

*Real 450K:* ~72 rows × ~485,000 CpG columns.

## INPUT 2 — replicate map (carries the experimental design)

```
P1: [P1_a, P1_b]   ...   P6: [P6_a, P6_b]
```

An incorrect pairing produces a misleading ICC even when every calculation is
correct, so the pipeline must **validate** the map (a tool-validation gate):
every referenced sample exists; each replicate belongs to exactly one subject;
duplicate sample IDs rejected; expected replicate count met; unpaired samples
reported; final valid-pair count explicit.

## STEP 2/3 — clock scores (a formal, versioned interface)

Apply each clock's CpG weights → one biological-age number per sample per clock.
The score matrix is the **contract between the R/Python scoring stage and the
reliability stage**. A **long-form** table is safest for provenance:

```
sample_id  clock_id     score  unit        implementation  version   pct_cpg_present  imputation
P1_a       Horvath      51.2   years       methylCIPHER    <commit>  0.998            none
P1_a       DunedinPACE  1.04   years/year  pyaging         <ver>     0.971            knn
```

(A wide table is convenient for humans; generate it *from* the long form so every
score keeps its unit, implementation, coverage, and warnings.) Illustrative wide view:

```
sample_id  GoodClock  ShakyClock
P1_a         153.27      175.03
P1_b         150.30      103.76     <- ShakyClock swings ~71 between repeats of ONE sample
...
```

## STEP 4/5 — the reliability leaderboard (the deliverable)

| Clock | ICC | 95% CI | Within-subject SD | Mean abs diff | Individual MDC95 | Reliability | n | k |
|---|---|---|---|---|---|---|---|---|
| GoodClock | 0.998 | (0.986, 1.000) | 1.85 | 2.28 | 5.12 | excellent | 6 | 2 |
| ShakyClock | 0.758 | (0.015, 0.962) | 26.34 | 27.45 | 73.02 | good | 6 | 2 |

**Each column, precisely (all in the clock's OWN unit — never inferred from the name):**
- **ICC** — between-person variance ÷ (between-person + error variance). It answers
  *"does the clock consistently distinguish people in THIS sample despite
  measurement noise?"* — **not** *"how many years of error does it have?"* It scales
  with between-person spread (see below), so it is read *with* the absolute columns.
- **Within-subject SD** — the SD of technical error on **one** measurement.
- **Mean abs diff** — the typical `|rep1 − rep2|`. A **different** quantity from
  within-subject SD: `SD(rep1 − rep2) = √2 × within-subject SD`. So a within-subject
  SD of 26.34 does **not** mean repeats differ by ~26; the *difference* has SD ≈ 37.
- **Individual MDC95** — the change in **one person's** value that exceeds technical
  noise at 95% (`1.96·√2·SD`). **Individual-level, not trial-level:** a sufficiently
  large trial can detect a group-average change far smaller than this.
- **Reliability** — Koo & Li band of the **point estimate**. Read the CI too.

## Two things the tiny example teaches

**(a) A clock can amplify noise.** GoodClock weights the stable CpGs → repeats
agree; ShakyClock weights noisy CpGs → a small probe-level fluctuation becomes a
large score swing. This is the exact problem Higgins-Chen's PC transformation
targets: original clocks use individual CpGs directly; PC clocks combine
methylation into principal components meant to keep stable biological structure
while suppressing probe-level technical noise. (The toy doesn't simulate PCs — it
illustrates the *consequence*: stable input → stable score; noisy input → unstable score.)

**(b) A point-estimate band can mislead.** ShakyClock's CI is **0.015–0.962** — with
n=6 the data are compatible with anything from poor to excellent, so a lone "good"
chip is misleading. Report both:
```
Point-estimate band:        Good
CI-compatible interpretation: Poor to Excellent
```
On real GSE55763 (36 pairs) precision improves, but some intervals stay wide.

## ICC depends on between-person spread (why absolute columns are essential)

Two clocks with identical 2-year technical error: in a cohort aged 20–90 the ICC
looks excellent (huge between-person spread); in a cohort aged 50–55 the same
error looks moderate/poor. Higgins-Chen even report ICC in two flavors — **raw
predicted age** vs **age-acceleration** (age-adjusted): Horvath1 original is 0.945
on raw age but 0.817 on acceleration, because removing the age spread makes the
same error loom larger. The protocol therefore reports both flavors, and always
pairs ICC with absolute error.

## The desired real-data output (UNIT-NEUTRAL target)

The code must never infer units from the clock name; units come from the versioned
clock manifest. DunedinPACE is **not** in years.

| Clock | Output unit | ICC | Within-subject SD | Mean abs diff | Individual MDC95 |
|---|---|---|---|---|---|
| PhenoAge | years | … | … years | … years | … years |
| DunedinPACE | years/year | … | … years/year | … years/year | … years/year |

## Objective — a hypothesis, not a required result

> Evaluate, using fully public technical-replicate data and open code, whether
> PC-transformed clocks show **higher ICC and lower absolute measurement error**
> than their originals — and classify the result as **supported / partially
> supported / not supported / inconclusive**.

All of these are scientifically useful outcomes: PC clocks improve dramatically;
only some improve; improvement shows in absolute error but not ICC; uncertainty
too wide; or preprocessing differences block a clean comparison. Encoding
"PC ≫ original, PC excellent" as a *required* result would be confirmation bias —
see `acceptance/replication_hypotheses.yaml` for the verdict-based encoding.
