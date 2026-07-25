# CLAUDE.md — reliage project memory

Orientation for Claude Code working in this repo. Read this first; treat
`docs/tracker.md` **Current State** block as canonical for what is true now.

## What this is

**reliage — the open, reproducible metrology layer for aging biomarkers.**
Version 1 is scoped to **epigenetic clocks, technical reliability**. It is the
reliability companion to ComputAgeBench (accuracy) but is **scorer-agnostic**: it
consumes a *score table + replicate map*, never methylation betas or clock formulas.

This is contribution **PIR03-C2** in a longevity research program (the "Frontier
Research Foundry"). It is a software/reproducibility contribution, **not new biology**.

## The v1 question (technical reliability only)

Do PC-transformed epigenetic clocks reduce **technical measurement error** vs their
originals on **independently rebuilt public replicate data**, and **what effect sizes
exceed each clock's technical measurement-noise floor**? (Not trial detectability;
not biological/longitudinal/responsiveness — those are Tiers B/C/D, out of v1 scope.)

## Current state

Canonical "what is true now": **`docs/tracker.md` Current State block** + the evidence ledger
**`docs/PIR03-C2/CLAIMS.md`**. Full engineering + scientific handover: **`docs/HANDOVER_v0.3.1.md`**.

- **Milestone 001 complete and FROZEN** at git tag `v0.3.1-scientific-baseline` (commit `61cacf0`):
  first real-data result on GSE55763 (36 cross-batch technical-replicate pairs) — PC clocks reduce
  within-subject technical variance, **supported 4/4** (all bootstrap CIs < 1), robustness-hardened
  (**selective denoising**, not compression).
- **Experiment E2 complete:** the conclusion is **implementation-robust** — an independent scorer
  (pyaging) reproduces it (per-sample scores r ≥ 0.9997, same verdict); one benign GrimAge
  calibration offset. See `IMPLEMENTATION_COMPARISON.md`.
- **Working branch `develop`**; `master` + the tag are the immutable M1 reference. Remote
  `github.com/gpal-ht/reliage-project`. Canonical local copy is under `C:\Ambitious Projects\...`
  (kept off OneDrive — sync clients corrupted `.git`; keep git GUIs/sync OFF this repo).
- **Scorer LOCKED** (`SCORING_DECISION.md`): methylCIPHER `@9e8c1e5` = pinned primary (run in M1);
  pyaging 0.3.1 = implementation-sensitivity scorer (run in E2).
- **Evidence dimensions:** software correctness ✅, statistical robustness ✅, implementation
  robustness ✅; **published-reference agreement (Tier-3) ⏳ and independent reproducibility ⏳ open.**

## The next task (fill an evidence dimension — not more architecture)

Do not re-open or re-interpret M1/E2, and do not add architecture. An experiment exists to update a
claim in `CLAIMS.md` (`FOUNDRY_PRINCIPLES.md` P7). Open dimensions, in order:

1. **Tier-3 — published-reference agreement** (→ CLAIMS #7): lock formal tolerances on
   *spread-independent* quantities (variance ratio, MDC95, mean/median abs diff — **not** raw ICC),
   then compare to published Higgins-Chen figures. Its own locked protocol (`TIER3_PROTOCOL.md`).
2. **Independent third-party rerun** (→ CLAIMS #8) from a clean environment via `PIPELINE.md`.

Only after both: consider a v1.0 release + a Versioned Score Table spec freeze (`VST_DESIGN_NOTES.md`).
Reproduction commands live in `docs/PIR03-C2/PIPELINE.md`. Known API/reproducibility pitfalls are in
`docs/HANDOVER_v0.3.1.md §12` (methylCIPHER 0.2.0 API, pyaging Python <3.14 + clinical-vs-DNAm
PhenoAge + GrimAge age/female-as-features).

## Non-negotiable rules (from locked protocol/reviews)

- **Provenance is mandatory.** Never record just "methylCIPHER". Pin repo URL, exact
  commit hash, R + package versions, clock function, preprocessing, imputation policy,
  % CpG coverage, output unit. Template: `reliage/scoring/PROVENANCE.template.md`.
  methylCIPHER has no formal releases and known clock discrepancies — commit-level
  pinning + coverage as a **gate** are required.
- **Per-clock units.** DunedinPACE = pace units (years/year), DNAmTL = kb — NEVER
  aggregate across units or label them "years".
- **ICC(2,1)** is primary; report ICC(1,1)/(3,1) as sensitivity. Report ICC WITH
  absolute error (ICC depends on between-person spread). Higgins-Chen report ICC in
  two flavors — raw age AND age-acceleration; report both.
- **Acceptance = two independent gates** (`docs/PIR03-C2/acceptance/`):
  `validation_cases.yaml` (software correctness, MUST pass) vs
  `replication_hypotheses.yaml` (scientific verdict: supported / directionally /
  partially / not / inconclusive — a "not supported" result from a correct run is a
  valid finding, never a tool failure). `published_reference_cases.yaml` holds exact
  source anchors (reproducible only under source conditions).
- **The published "3–9 yr / 0–1.5 yr" figures are median/max absolute replicate
  difference, NOT within-subject SD.** Do not conflate.
- **Trial-mode detectability is a measurement-noise SCREEN, not a power calculation.**
- **Scope discipline.** reliage answers one question: can this biomarker be trusted for
  this measurement task? Aging mechanisms / causality / intervention biology stay
  SEPARATE projects that consume reliage's outputs. Do not fold them in.
- **Depth over breadth.** PIR03-C2 is the sole active project until v1 freeze.

## Repo map

```
reliage/            the package
  icc.py            ICC(1/2/3) + F-CIs + Koo-Li bands + SEM + MDC95 (verified core)
  benchmark.py      scores -> reliability leaderboard
  contrast.py       variance ratio (PC/original) + paired bootstrap CI (PRIMARY ENDPOINT)
  detectability.py  "reliable enough for WHAT?" screen + recommend_for_effect
  clocks.py         score adapters (linear clock; optional ComputAgeBench)
  datasets.py       replicate-group builder + GSE55763 loader + synthetic generator
  selfcheck.py      4 dependency-light correctness gates  (python -m reliage.selfcheck)
  scoring/          score_methylCIPHER.R (PRIMARY), run_analysis.py (end-to-end), provenance
tests/              pytest suite (test_icc, test_benchmark)
examples/           quickstart.py, input_output_walkthrough.py
data/               download_data.sh + DATASETS.md (run where data lives)
datasets/           per-dataset raw/processed/metadata scaffold + READMEs
docs/PIR03-C2/      VISION, PROTOCOL, SCORING_DECISION, CLOCK_MANIFEST.csv,
                    acceptance/*, STATUS_REVIEW, INPUT_OUTPUT, TEST_CASES, ...
docs/tracker.md     canonical project tracker (Current State block is authoritative)
```

## Verify before trusting a change

```bash
python -m reliage.selfcheck     # 4 gates: ICC vs Shrout-Fleiss, end-to-end ICC recovery,
                                # variance-ratio recovery, detectability bands
pytest -q                       # full suite (needs pytest)
```

## Environment note

reliage core needs only numpy/pandas/scipy. Scoring needs R + methylCIPHER
(`devtools::install_github("HigginsChenLab/methylCIPHER")`; PC clocks also need the
CalcAllPCClocks reference object) and/or `pip install pyaging` for the sensitivity path.
Datasets are large — download where the data will live, not into a throwaway env.
