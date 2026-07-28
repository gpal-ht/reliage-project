# reliage — Engineering & Scientific Handover (v0.3.1)

**Version:** v0.3.1 · **Covers:** Milestone 001 (frozen at `v0.3.1-scientific-baseline`, commit
`61cacf0`) + Experiment E2 (implementation robustness) · **As of:** 2026-07-25.
**Supersession:** this is a *versioned snapshot* valid only for this state. At the next version
bump (e.g. after Tier-3, or a Versioned-Score-Table spec freeze), write a new `HANDOVER_v<next>.md`
— do not silently edit this file for later work; a superseded handover must still describe exactly
what was true at its version. Prior/next handovers live alongside it in `docs/`.

Definitive handover for a maintainer new to this repository. Assumes fluency with epigenetic
clocks, methylation betas, ICC/reliability statistics, PCA, methylCIPHER, pyaging, and GEO.
Biology is explained only where it forced a design decision.

Canonical working copy: `C:\Ambitious Projects\Longevity Project\Contributions\PIR03-C2\reliage-project`
(kept off OneDrive — see Known Pitfalls). Remote: `github.com/gpal-ht/reliage-project`.
Active branch `develop`; `master` + tag `v0.3.1-scientific-baseline` are the frozen M1 reference.

---

## 1. Executive Summary

**What it is.** reliage is a scorer-agnostic **measurement-science layer for aging biomarkers**.
v1 scope: *technical reliability of epigenetic clocks*. It consumes a **Versioned Score Table**
(clock scores + provenance) and a **replicate map**, and produces reliability statistics
(ICC, within-subject SD/SEM, MDC95, PC-vs-original variance ratio with bootstrap CI, detectability
screen) and a scientific verdict. It never touches methylation betas or clock formulas — those are
the scorer's job.

**Why it exists.** Published claims that PC-transformed clocks are more *reliable* than their
originals (Higgins-Chen) had no open, independent, rerunnable reliability benchmark. reliage is
that benchmark, plus the reproducible methodology around it.

**Current maturity.** Two evidence dimensions closed, three open:
- ✅ Software correctness, ✅ Statistical robustness, ✅ Implementation robustness.
- ⏳ Published-reference agreement (Tier-3), ⏳ Independent reproducibility. Generalization
  (other datasets/platforms/biological reliability/other clocks) untested by design.

**Strongest result.** On GSE55763 (36 cross-batch technical-replicate pairs), for four
prespecified clock pairs, PC clocks reduce within-subject technical variance by 87–96% (point
estimates; CI worst case ~67%, Hannum), all four bootstrap CIs exclude 1, robust to
leave-one-subject-out, and the effect is **selective denoising** (between-subject signal retained
74–85%), not range compression. E2 then showed this conclusion is **not an artifact of the
scoring implementation**: an independent scorer (pyaging) reproduces it (per-sample score
r ≥ 0.9997, identical ICC/variance-ratio ordering, same verdict). The strongest *independent*
evidence is the original clocks (separately implemented by both tools from public coefficients).

**Remaining work.** Tier-3 formal reference comparison and an independent third-party rerun. Only
after those is a v1.0 release discussion in scope.

---

## 2. Project Mission

- **Original problem:** reproduce and independently verify the Higgins-Chen reliability finding
  (PC clocks reduce technical error) with open code and independently rebuilt public data.
- **How it evolved:** the durable contribution shifted from *reproducing one finding* to
  *providing a reusable, scorer-agnostic apparatus for evaluating biomarker measurement
  reliability* — a metrology layer, with published reproduction as one experiment inside it.
- **North Star:** the open, reproducible metrology layer for aging biomarkers (biomarker-agnostic
  in principle; v1 realized only for epigenetic clocks, technical reliability).

Read the hierarchy as: **Mission** (metrology layer) → **research objective** (do PC clocks reduce
technical error on rebuilt public data?) → **evidence dimensions** (software / statistical /
implementation / reference / independent) → **claims** (the ledger in `CLAIMS.md`).

The single authoritative statement of *what is true now* is `docs/tracker.md` (Current State block)
plus `docs/PIR03-C2/CLAIMS.md` (the evidence ledger).

---

## 3. Scope

**reliage IS:**
- A consumer of a score table + replicate map that computes technical-reliability metrics.
- Scorer-agnostic and dataset-agnostic (it depends on neither a methylation pipeline nor any
  specific scorer).
- v1: epigenetic clocks, **technical** reliability only (measurement noise under repeated
  assay of the same biological sample).

**reliage IS NOT:**
- A methylation preprocessing/normalization pipeline (it never sees IDATs or raw betas beyond what
  a scorer already consumed).
- An **accuracy** benchmark (that is ComputAgeBench's domain; not a dependency here).
- A biology/causality/intervention tool. Aging mechanisms, longitudinal drift, biological
  reliability, and responsiveness are explicitly out of v1 (Tiers B/C/D).
- A clock trainer or a clock. It does not fit or define clocks.

**Biology boundary (the one that matters for design):** the split between *biomarker computation*
(betas → scores, owned by the scorer) and *measurement science* (scores + replicate design →
capability estimates, owned by reliage). The Versioned Score Table is that boundary made concrete.

---

## 4. Architecture

```
Raw betas (GEO)                         [external, large; not in git]
      │  generated/GSE55763/build/parse_metadata.py   (reconstruct replicate design from GEO series matrix)
      │  generated/GSE55763/build/extract_betas.sh    (stream-extract the replicate columns)
      ▼
Cohort inputs:  betas.csv  +  pheno.csv (sample_id, age, female)  +  map.csv (subject → sample_id)
      │  reliage/scoring/score_methylCIPHER.R   (PRIMARY scorer, R)      ─┐
      │  reliage/scoring/score_pyaging.py        (E2 scorer, Python)      ─┤  interchangeable producers
      ▼                                                                   │
█ VERSIONED SCORE TABLE  (scores.csv / scores_pyaging.csv) █  ◄───────────┘  the contract
      │  reliage/scoring/run_analysis.py     (leaderboard + variance-ratio contrasts + detectability + verdict)
      │  reliage/scoring/age_accel_icc.py    (age-acceleration ICC companion)
      │  reliage/scoring/robustness.py       (compression audit, LOSO, outliers, Bland–Altman)
      ▼
Results:  out/{leaderboard,contrasts,results.json,RESULTS.md,ROBUSTNESS.md,figures/}
```

**Boundaries and why they exist:**
- **Metadata → cohort inputs.** The replicate design (which samples are repeats of which subject)
  is reconstructed from the GEO series matrix, *not* assumed. This is a first-class step because
  the entire reliability computation depends on correct pairing; it is validated (36 subjects × 2,
  0 malformed) and the builder is deterministic (reproduces committed `pheno.csv`/`map.csv`
  byte-identically).
- **Scorer → Versioned Score Table.** The scorer owns clock identity, coefficients, imputation,
  and coverage. It emits the score table and nothing downstream depends on *how* it did so, only
  on the table + its provenance.
- **Versioned Score Table → reliage engine.** reliage consumes only the table + replicate map. It
  is the reason a second scorer (pyaging) dropped in with **one** downstream parameter change.

**Why the Versioned Score Table exists.** It decouples *scoring* from *measurement science* so
that (a) any scorer can be measured, (b) any measurement tool can consume any scorer, (c) scores
carry their own provenance and are reproducible without external notes, and (d) reliage stays free
of methylation-pipeline and clock-formula dependencies.

**Why it became a *contract*, not just an interface.** An interface exists because a programmer
decided it should. A contract exists because independently developed systems *naturally satisfy
it*. E2 was the test: pyaging — authored by different people, in a different language, with
different preprocessing — emitted the same schema, and the measurement engine consumed it
unchanged. Two independent **producers** (methylCIPHER, pyaging) + one independent **consumer**
(reliage) is the bar (Foundry principle P8). Before E2 the table was an architectural hypothesis;
after E2 it is evidence-backed.

---

## 5. Scientific Model

**Evidence layers** (a claim is only as strong as its weakest layer; keep them distinct):
- **Software** — the engine is correct. Evidence: ICC verified against Shrout–Fleiss worked
  examples; `python -m reliage.selfcheck` (4 gates).
- **Statistical** — the effect survives refutation. Evidence: M1 robustness suite (compression
  audit, leave-one-subject-out, Bland–Altman, outliers) — designed as *attempted falsification*,
  not support.
- **Scientific** — the effect exists in real data. Evidence: the GSE55763 result.

**Evidence dimensions** (orthogonal axes; progress = filling cells, not a timeline): software
correctness, statistical robustness, implementation robustness, published-reference agreement,
independent reproducibility. See the coverage matrix in `CLAIMS.md`.

**CLAIMS.md is the primary artifact.** It is the living scientific state: a numbered ledger of
claims, each with evidence, confidence, scope, and last-updated. **Reports, figures, and code are
evidence-production machinery; the ledger is the endpoint.** An experiment must declare, before it
begins, which claim(s) it can change, and is "done" only when it updates a claim's status or scope
(principle P7). When new work is proposed, the first question is "which claim will this change?"

---

## 6. Important Design Decisions

Each: **Decision · Reason · Alternatives · Tradeoffs · Consequences.**

**6.1 Scorer-agnostic engine.**
Decision: reliage consumes a score table + replicate map, never betas or clock formulas.
Reason: measurement reliability is a property of scores under replication, independent of how the
scores were computed; decoupling lets any scorer be measured and keeps reliage dependency-light
(numpy/pandas/scipy only).
Alternatives: bake methylation scoring into reliage; depend on ComputAgeBench.
Tradeoffs: requires a stable score-table schema and shifts scoring/provenance responsibility to
the producer.
Consequences: E2 (second scorer) was a drop-in; reliage core has no heavy/biological dependencies.

**6.2 The Versioned Score Table as the interface.**
Decision: a single, provenance-carrying score table is the sole coupling between scoring and
analysis.
Reason: reproducibility and scorer interchange (see §4).
Alternatives: pass in-memory objects; per-scorer bespoke adapters.
Tradeoffs: schema must be governed and versioned.
Consequences: became a validated contract at E2 (P8).

**6.3 Long-form schema (not wide).**
Decision: one row per (sample × clock × variant), with per-row provenance.
Reason: scales to arbitrarily many clocks/scorers without schema change; each score self-describes
its provenance; trivially supports multi-scorer tables.
Alternatives: wide (samples × clock-columns) — used only as a generated convenience view
(`scores_wide.csv`).
Tradeoffs: verbose (repeated provenance columns); a future spec may normalize provenance via a
run_id header (see `VST_DESIGN_NOTES.md`) — deferred until a second dataset/scorer stress-tests it.
Consequences: `run_analysis.py` pivots long → wide internally; the canonical artifact is long.

**6.4 Protocol locking before results.**
Decision: freeze question, endpoint, constants, and acceptance thresholds before producing results
(`PROTOCOL.md`, `E2_PROTOCOL.md`).
Reason: pre-registration; prevents post-hoc rationalization.
Consequences: verdicts are pre-committed; a "not supported" from a correct run is a valid finding,
not a tool failure.

**6.5 Robustness as attempted refutation, before strengthening claims.**
Decision: run adversarial checks (compression, LOSO, Bland–Altman, outliers) whose purpose is to
*break* the result; strengthen the claim only with what survives.
Reason: confidence comes from failed falsification, not accumulated support.
Consequences: the M1 claim is calibrated ("selective denoising with modest — not zero —
compression"), and the compression objection is answered quantitatively, not asserted.

**6.6 Evidence ledger + claim-driven workflow.**
Decision: `CLAIMS.md` is the scientific state; experiments exist to update claims.
Reason: separates knowledge (claims) from machinery (code/reports); makes scope explicit and
prevents confidence laundering (each "Supported" is provisional and scoped).
Consequences: work is proposed as "which claim does this move?"; release is a function of evidence
coverage, not experiment count.

**6.7 Frozen milestones.**
Decision: at a milestone, tag an immutable snapshot; all later work commits on top, never into it.
Reason: future readers can answer "what did we know when this was declared?" unambiguously.
Consequences: `v0.3.1-scientific-baseline` (commit `61cacf0`) is M1; review polish, postmortem,
and all of E2 sit after it; the tag never moved.

**6.8 GrimAge = V1 (locked).**
Decision: original GrimAge is V1 (`calcGrimAgeV1`), paired with PCGrimAge (`CLOCK_MANIFEST.csv`).
Reason: PCGrimAge was derived against GrimAge V1; pairing V2 would confound variant with PC
transform.
Consequences: methylCIPHER uses `calcGrimAgeV1`; pyaging uses `grimage` (its V1), *not* `grimage2`.
Do not casually switch to V2.

**6.9 methylCIPHER primary, pyaging sensitivity-only.**
Decision: methylCIPHER (pinned commit) is the primary scorer; pyaging is an implementation-
sensitivity check (`SCORING_DECISION.md`).
Reason: methylCIPHER computes all four original↔PC pairs in-package (`calcPCClocks`), enabling a
clean single-tool primary; pyaging provides *independent* re-implementation for E2.
Consequences: M1 scores are methylCIPHER; E2 compares, it does not replace.

---

## 7. Repository Guide

**Canonical vs generated.** *Canonical* = human-authored decisions/state. *Generated* =
reproducible from inputs + code. Do not hand-edit generated files.

| Path | Role | Canonical? |
|---|---|---|
| `reliage/icc.py` | ICC(1/2/3) + F-CIs + Koo–Li bands + SEM + MDC95 (verified core) | canonical (code) |
| `reliage/benchmark.py` | scores → reliability leaderboard; `build_replicate_matrix` | canonical |
| `reliage/contrast.py` | within-subject variance ratio (PC/original) + paired bootstrap CI (**primary endpoint**) | canonical |
| `reliage/detectability.py` | measurement-noise screen ("reliable enough for what?") | canonical |
| `reliage/selfcheck.py` | 4 dependency-light correctness gates | canonical |
| `reliage/scoring/score_methylCIPHER.R` | PRIMARY scorer (R) → Versioned Score Table | canonical |
| `reliage/scoring/score_pyaging.py` | E2 scorer (Python) → Versioned Score Table | canonical |
| `reliage/scoring/run_analysis.py` | end-to-end: leaderboard + contrasts + detectability + verdict | canonical |
| `reliage/scoring/age_accel_icc.py` | age-acceleration ICC companion (optional 4th arg = out path) | canonical |
| `reliage/scoring/robustness.py` | compression audit / LOSO / outliers / Bland–Altman | canonical |
| `reliage/scoring/figures.py` | the 5 M1 figures | canonical (code) |
| `generated/GSE55763/build/` | dataset-prep scripts (metadata parse, column extract) | canonical |
| `generated/GSE55763/metadata/` | `pheno.csv`, `map.csv`, `replicate_sample_ids.txt`, `PROVENANCE.md` | generated (committed) |
| `generated/GSE55763/processed/` | `betas.csv` (**gitignored, 596 MB**), `scores.csv`, `scores_pyaging.csv`, `scores_wide.csv` | generated |
| `generated/GSE55763/out/` | M1 results (leaderboard, contrasts, RESULTS.md, ROBUSTNESS.md, figures/) | generated (force-added at M1 tag) |
| `generated/GSE55763/out_E2/` | E2 results (RESULTS_E2.md, contrasts, robustness/) | generated |
| `docs/FOUNDRY_PRINCIPLES.md` | cross-project methodology (P1–P8) | canonical |
| `docs/tracker.md` | **Current State block is authoritative for what is true now** | canonical |
| `docs/PIR03-C2/CLAIMS.md` | evidence ledger (the scientific state) | canonical |
| `docs/PIR03-C2/PROTOCOL.md`, `SCORING_DECISION.md`, `CLOCK_MANIFEST.csv` | locked analytic decisions | canonical |
| `docs/PIR03-C2/E2_PROTOCOL.md` | E2 locked protocol + pinned clock mapping | canonical |
| `docs/PIR03-C2/TECHNICAL_REPORT_v0.1.md`, `PIPELINE.md` | M1 report + reproduction pipeline | canonical (prose) |
| `docs/PIR03-C2/IMPLEMENTATION_COMPARISON.md` | E2 comparison + divergence taxonomy + root-cause ledger | canonical |
| `docs/PIR03-C2/MILESTONE_001.md`, `POSTMORTEM_M1.md`, `TIMELINE_M1.md`, `POSTMORTEM_E2.md` | milestone archive / reflections | canonical |
| `docs/PIR03-C2/VST_DESIGN_NOTES.md` | deferred Versioned Score Table spec (run_id header, subjects/samples split) | canonical (design) |
| `data/download_data.sh`, `data/DATASETS.md` | dataset download bundle | canonical |

Large data lives on disk but not in git: the 9.7 GB GEO gz (backup at
`C:\Ambitious Projects\Longevity Project\Datasets\`, md5 `64654afe3a8898641c3e321c5a5204df`) and
`betas.csv` (596 MB). External runtimes not in git: the PC reference `PCClocks_data.qs2`
(Zenodo `10.5281/zenodo.19455622`, cached at `C:\Users\gaura\methylCIPHER\`) and the pyaging
Python 3.13 env (`C:\Users\gaura\pyaging_env`).

---

## 8. Versioned Score Table

**Schema (long-form, one row per sample × clock × variant):**
`sample_id, clock_id, variant, score, unit, implementation, repo_url, commit, r_version,
pkg_version, clock_function, imputation`.
- `clock_id` ∈ {Horvath1, Hannum, PhenoAge, GrimAge}; `variant` ∈ {original, PC}. `run_analysis`
  derives the label `clock_id` (original) or `PC+clock_id` (PC) and matches the locked pairs.
- `score` in `unit` (all four families = "years"; **never aggregate across units** — DunedinPACE
  is pace units, DNAmTL is kb, if added later).
- Provenance columns pin the producer: implementation, repo/commit (or `pip-<version>`), runtime
  and package versions, the exact scorer function, and imputation policy.

**Philosophy.** The table is the scientific-exchange object, not an intermediate CSV. It is
intended to be to measurement-science what a BAM is to genomics: multiple engines *produce* it,
multiple tools *consume* it. Demographics live separately (`pheno.csv`), not in the score table.

**Required provenance.** A score is invalid without: scorer + exact version/commit, clock function,
preprocessing/imputation policy, and per-clock CpG coverage for the dataset (a gate, recorded in
`PROVENANCE.md`). Template: `reliage/scoring/PROVENANCE.template.md`.

**Compatibility guarantees / how to target it.** A new scorer must emit the exact column set and
the `clock_id`/`variant` vocabulary above, in the score's native unit, with its own provenance.
If it does, the entire reliage pipeline runs unchanged. Do not add scorer-specific columns to the
canonical schema; put scorer specifics in provenance values. The forward-looking normalized spec
(metadata.yaml + run_id header + subjects/samples split) is in `VST_DESIGN_NOTES.md` and is
**deliberately deferred** until a second dataset and second scorer have exercised the current form
(they now have; a v1.0 spec freeze is a candidate future task, not yet done).

---

## 9. Scientific Results

**M1 (frozen `v0.3.1-scientific-baseline`).** GSE55763, independently reconstructed; 36 cross-batch
technical-replicate pairs (two measurements per subject, deliberately in separate batches); four
prespecified clock pairs. Scored with methylCIPHER `@9e8c1e5` (R 4.6.1), GrimAge V1, PC reference
from Zenodo. Coverage 100% except GrimAge 91% (97 imputed CpGs).
- **Primary endpoint:** within-subject variance ratio (PC/original), paired bootstrap CI. All four
  < 1 (PhenoAge 0.036 [0.021,0.060]; GrimAge 0.128 [0.075,0.219]; Horvath1 0.133 [0.065,0.259];
  Hannum 0.135 [0.058,0.329]). Verdict **supported 4/4**. 87–96% technical-variance reduction
  (point estimates; CI worst case ~67% for Hannum).
- **Absolute capability:** MDC95 tightens 2.7–5.3× (PhenoAge 7.75 → 1.46 yr).
- **Age-acceleration ICC:** originals fall to "good" (0.76–0.96), PC stay "excellent" (0.97–0.99);
  SEM and variance ratio invariant to residualization (both replicates share one age).
- **Robustness:** LOSO 0/144 verdict flips; **selective denoising** (noise −87–96%, between-subject
  signal retained 74–85% [SPR], age association + subject ranking preserved ρ 0.87–0.96); GrimAge
  is not a factor for `cg00017157` (not a clock CpG). Full detail: `out/ROBUSTNESS.md`.

**E2 (implementation robustness).** pyaging 0.3.1 vs methylCIPHER, everything else constant.
- **Supported (H1):** per-sample scores r ≥ 0.9997 (7/8 exactly 1.0000), subject-rank ρ 0.999–1.0,
  ICC identical to 3 dp (ordering ρ = 1.0), variance-ratio ordering ρ = 1.0, verdict supported 4/4
  in both. Robustness (compression/SPR/age-accel) identical.
- **One divergence, benign:** GrimAge constant −2.63 yr calibration offset (r = 1.0000; changes no
  within-subject difference → ICC/VR/verdict unaffected). Classified **Calibration Offset**
  (lowest-importance class; see the divergence taxonomy in `IMPLEMENTATION_COMPARISON.md`).
- **Caveat:** PC-clock independence is *partial* (pyaging and methylCIPHER PC clocks likely share
  the published Higgins-Chen coefficients); the **original** clocks carry the implementation-
  robustness claim.

**Status labels:** **Supported** — evidence meets prespecified criteria within stated scope.
**Pending** — planned, criteria defined, not yet run (Tier-3, independent rerun). **Unknown** — not
tested and out of current scope (other datasets, EPIC, biological reliability, other clock families).

---

## 10. Evidence Ledger

`docs/PIR03-C2/CLAIMS.md` holds 12 numbered claims. Claims 1–6 Supported (software correctness,
bootstrap/variance-ratio correctness, PC reduces technical variance on GSE55763, survives
robustness, selective-denoising interpretation, implementation-robust). Claims 7–8 Pending
(reference agreement, independent reproducibility). Claims 9–12 Unknown (generalization).

**How it evolves.** Each experiment updates a row (status, evidence, scope, last-updated), not the
whole file. "Supported" is provisional and scoped — apply disprove-first (P2) to the ledger itself;
a claim stands until a new dimension or dataset re-tests it. Release decisions read the
evidence-dimension coverage matrix, not an experiment count.

---

## 11. Foundry Principles (how they shape engineering)

`docs/FOUNDRY_PRINCIPLES.md` is canonical; here is how each constrains day-to-day work:
- **P1 (lock protocols):** write and commit the protocol (endpoint, constants, thresholds) before
  producing results. New analysis code lands *after* the protocol commit.
- **P2 (disprove before strengthening):** implement robustness/refutation code, and when an anomaly
  appears, *investigate the cause before concluding* — includes a known-relationship smoke test
  (an age clock must track chronological age).
- **P3 (match by definition, not name):** never map clocks across tools by name; verify by feature
  set (CpG identity/count) and input contract. This is where implementation studies actually spend
  effort.
- **P4 (separate evidence layers):** keep software/statistical/scientific validation distinct in
  code and docs; don't let one borrow another's confidence.
- **P5 (immutable milestones):** tag milestones; commit fixes on top; never rewrite a tagged commit.
- **P6 (record uncertainties):** every result carries an explicit scope + remaining-uncertainty
  statement.
- **P7 (scope by the claim it changes):** an experiment declares its target claim up front and is
  done only when the ledger updates.
- **P8 (promote to contract on ≥2 producers + 1 consumer):** treat an abstraction as a contract
  only after independent multi-party validation (the Versioned Score Table crossed this at E2).

---

## 12. Known Pitfalls

**Scorer / API traps (methylCIPHER, R):**
- The R scorer must match the *installed* methylCIPHER **0.2.0** API: `calcGrimAgeV1/V2(DNAm,
  pheno)`, `calcPCClocks(DNAm, pheno, RData)`, pheno columns capitalized `Age`/`Female`. Older
  scripts targeting a different API silently break. Introspect the installed package, not the
  script's comments.
- methylCIPHER `check_DNAm` **rejects CpGs that are NA in all samples** (GrimAge/PC error out).
  The scorer drops all-NA CpGs (→ treated as missing → imputed) and records the count. Partial-NA
  CpGs are fine.
- **`qs2`/`stringfish` CRAN binaries fail to load on Windows** (`LoadLibrary … module not found`).
  Rebuild both from source (`install.packages(type="source")`) with Rtools; they then static-link.
- The PC reference does **not** require the dead Yale Box `CalcAllPCClocks.RData`. Use
  `download_methylCIPHER(source="zenodo")` or the direct Zenodo file (DOI 10.5281/zenodo.19455622).
- GrimAge/PC require age + sex; `pheno.csv` must carry `age` and `female` (0/1).

**Scorer / API traps (pyaging, Python):**
- **pyaging needs Python ≥3.9,<3.14.** This box has 3.14; use an isolated 3.13 env
  (`C:\Users\gaura\pyaging_env`, built via `uv`). reliage's own analysis runs on 3.14 (numpy/
  pandas/scipy only) — keep the two environments separate.
- **`phenoage` is pyaging's CLINICAL PhenoAge** (albumin/creatinine/glucose), NOT the DNAm clock.
  The methylation Levine clock is **`dnamphenoage`** (513 CpGs). Verified by feature inspection.
- **pyaging GrimAge reads Female/Age as the last two FEATURES** (`x[:,-2]`, `x[:,-1]`), literally
  named `female` and `age`, NOT from `adata.obs`. They must be columns of the betas matrix. Passing
  via `.obs` yields a constant age and a spuriously low `r(age)` — this looked like a large
  "implementation divergence" and was a scoring bug.
- pyaging's logger emits emoji; on Windows cp1252 consoles this raises `UnicodeEncodeError`. Run
  with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.

**Clock-definition traps (general):** clock *name* ≠ clock *definition* across tools. Always match
by biological definition + required feature set. The two pyaging traps above were caught by
verification before they became false findings (root-cause ledger in
`IMPLEMENTATION_COMPARISON.md`).

**Statistics traps:**
- **ICC is between-subject-spread-dependent.** Always report it *with* absolute error (SEM, MDC95).
  Do not compare raw ICC across cohorts; use variance ratio and MDC95 (spread-independent) for
  cross-study comparison — this is the basis for the Tier-3 design.
- **Age-acceleration residualization leaves within-subject variance unchanged** (both replicates
  share one age): SEM and the variance ratio are invariant; only ICC drops. Reporting age-accel ICC
  *without* noting this invariance would mislead.
- The published "3–9 yr / 0–1.5 yr" GrimAge/Horvath figures are **median/max absolute replicate
  difference**, not within-subject SD. Do not conflate.

**Reproducibility / provenance traps:**
- `.gitignore` excludes `generated/*/processed/betas.csv`, `out/`, and `scores*.csv`. The small M1 result
  artifacts were **force-added** intentionally so the tag is self-contained; `betas.csv` (596 MB)
  and the GEO gz are deliberately *not* committed. When adding new result artifacts to a milestone,
  force-add the *small* ones and never `betas.csv`.
- **Keep git GUIs and sync/backup clients (OneDrive/Dropbox) OFF this repo.** During M1 a concurrent
  tool mutating `.git` under `C:\Ambitious Projects` caused refs to flip-flop between two unrelated
  lineages and `Invalid argument` file locks on `scores.csv`. Commits were never lost (they stay in
  the object DB), but the working state was unstable. If a tag/ref appears to vanish, suspect this
  before assuming data loss.
- Reproduction requires the 9.7 GB gz (re-downloadable from GEO; md5 recorded) and the external
  runtimes above; provenance files record every pin needed.

---

## 13. Remaining Work (by Evidence Dimension)

**Dimension: Published-reference agreement (Tier-3) → moves claim #7.**
- Question: do reliage's GSE55763 results match published Higgins-Chen figures within *prespecified
  formal tolerances*?
- Current evidence: informal directional consistency only (PC raw ICC ≥ 0.99 matches; mean abs diff
  ~ published) — recorded in `TECHNICAL_REPORT_v0.1.md §10`, explicitly *not* a formal comparison.
- Missing: a locked tolerance specification (on spread-independent quantities — variance ratio,
  MDC95, mean/median abs diff — not raw ICC) and the executed comparison. Note: the original
  fast-path anchor (Box example data) is gone; anchor to published figures. The reproduction gate
  should be a tier hierarchy (reproduce published stats → independent GEO rebuild ✅ → consistency
  within tolerances) — see `SCORING_DECISION.md` / `status_report_0.3.1.md`; ratify it into
  `SCORING_DECISION.md` only after the comparison runs.
- Deliverables: `TIER3_PROTOCOL.md` (locked tolerances), the comparison output, CLAIMS #7 update.
- Exit criteria: all prespecified tolerances met (or a recorded, scoped "not met").

**Dimension: Independent reproducibility → moves claim #8.**
- Question: can a third party clone the repo and reproduce the results without the author?
- Current evidence: the pipeline is documented (`PIPELINE.md`), builders are deterministic, and
  provenance is complete — but no external party has executed it.
- Missing: an actual independent rerun from a clean environment.
- Deliverables: a reproduction record (environment, versions, diffs vs committed results), CLAIMS #8.
- Exit criteria: independent results within numerical tolerance of the committed ones.

**Dimension: Generalization (claims #9–#12) — out of v1 scope, listed for completeness.**
- Other datasets, EPIC vs 450K, biological (not technical) reliability, clock families beyond the
  four. Each is a separate future experiment with its own protocol; do not fold into v1.

**Minor open item:** ICC(1,1)/(3,1) sensitivity alongside the primary ICC(2,1) (cheap; the engine
already supports all three forms).

**Release:** a v1.0 discussion is in scope only after Tier-3 and the independent rerun. v1.0 would
also be the natural point to freeze the normalized Versioned Score Table spec (`VST_DESIGN_NOTES.md`).

---

## 14. Things That Should Not Change Lightly

Require a written justification (and ideally a protocol) before altering:
- **The Versioned Score Table schema / vocabulary.** It is a validated contract; changing columns
  or the `clock_id`/`variant` vocabulary breaks every producer and consumer. Extend via provenance
  values or a versioned spec bump, not ad hoc.
- **The scorer abstraction** (reliage never touches betas/formulas). Folding scoring into reliage
  would reintroduce heavy/biological dependencies and destroy scorer interchange.
- **The claim-driven workflow** (experiments update `CLAIMS.md`; the ledger is the endpoint).
- **Protocol locking before results.**
- **Evidence-dimension framing** (orthogonal axes, not a linear experiment sequence).
- **Milestone freezes** (tags are immutable; fixes commit on top).
- **The GrimAge V1 pin** and **per-clock units** (never aggregate across units).

---

## 15. FAQ

- **Why methylCIPHER as primary?** It computes all four original↔PC pairs in-package
  (`calcPCClocks`), giving a single-tool primary with clean pairings; it is pinned at a commit for
  reproducibility.
- **Why pyaging?** An *independent* re-implementation (different authors/language/preprocessing) for
  the implementation-robustness dimension (E2). It is a sensitivity check, not a replacement.
- **Why not ComputAgeBench?** It is an *accuracy* benchmark on unique biological samples (no
  technical replicates); reliability is a different question and CAB is not a dependency.
- **Why only four clocks?** They are the clock families with clean original↔PC pairs available
  in-package with matching definitions. More clocks/units belong to future dimensions.
- **Why GSE55763?** It contains 36 subjects measured in duplicate across separate batches — public,
  independently rebuildable, and a genuine cross-batch technical-noise stress test.
- **Why not biological reliability?** Out of v1 scope (Tiers B/C/D). v1 answers technical
  measurement error only; conflating the two would overclaim.
- **Why long format?** Extensibility to arbitrary clocks/scorers without schema change, and per-row
  provenance. Wide is a generated view only.
- **Why a Versioned Score Table at all?** To decouple scoring from measurement science, keep reliage
  scorer/dataset-agnostic, and make scores reproducible on their own provenance.
- **Why frozen milestones?** So the exact evidentiary state at declaration is permanently
  recoverable; editorial changes must not blur "what we knew then."
- **Why is the answer to E2 phrased so narrowly?** Because "the implementations are identical" is
  false (GrimAge offset) and any claim beyond these clocks/dataset is unearned. The precise claim is
  the only supported one.

---

## 16. Glossary (project-specific)

- **Versioned Score Table** — the long-form, provenance-carrying score table that is the contract
  between scorer and analysis.
- **Evidence Dimension** — an orthogonal axis of confidence (software correctness, statistical
  robustness, implementation robustness, published-reference agreement, independent reproducibility).
- **Claim** — a numbered, scoped assertion in `CLAIMS.md` with evidence, confidence, and status.
- **Milestone** — a tagged, immutable evidentiary snapshot (M1 = `v0.3.1-scientific-baseline`).
- **Supported / Pending / Unknown** — claim statuses (§9).
- **Tier-3** — the published-reference-agreement evidence dimension (formal tolerance comparison).
- **Implementation Robustness** — the dimension establishing that conclusions do not depend on the
  scoring implementation (E2).
- **Calibration Offset** — a constant additive score difference (r≈1, slope≈1) between scorers;
  lowest-importance divergence class (no ranking/reliability effect). The GrimAge −2.63 yr shift.
- **Selective Denoising** — reduction of within-subject (technical) variance far exceeding any
  reduction in between-subject (signal) variance; the M1 characterization of the PC effect.
- **Noise Ratio (NR)** — within-subject variance(PC)/within-subject variance(original) = the primary
  variance ratio.
- **Signal Preservation Ratio (SPR)** — between-subject variance(PC)/between-subject variance
  (original); ≈1 means structure retained.
- **Variance ratio (primary endpoint)** — NR with a paired subject-resampling bootstrap CI; < 1
  favors PC.
- **MDC95** — smallest detectable change per individual at 95% (1.96·√2·SEM), in the clock's unit.
- **Replicate map** — subject → [sample_id, …]; defines which measurements are repeats of which
  subject.

---

## 17. Final State

reliage is no longer a prototype. It is a reproducible technical-reliability measurement framework
for epigenetic clocks with **supported claims in three evidence dimensions** (software correctness,
statistical robustness, implementation robustness), an **explicit evidence ledger** (`CLAIMS.md`),
a **validated scorer contract** (the Versioned Score Table, exercised by two independent
producers), and **explicitly bounded remaining uncertainties** (published-reference agreement and
independent reproducibility, both Pending; broader generalization Unknown by design). The M1
scientific baseline is frozen and immutable; all subsequent work — including E2 — is layered on top.
A v1.0 release discussion is deliberately deferred until the two Pending dimensions are closed.
