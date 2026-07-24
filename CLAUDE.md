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

## Current state (as handed off)

- **reliage v0.3.x**, synthetic pipeline validated. **Milestone: real-data execution.**
- **Evidence state: NO real-data scientific result yet** — the core hypothesis is
  untested by this implementation. Current claims are **software + synthetic-validation
  only**.
- **Scorer LOCKED** (`docs/PIR03-C2/SCORING_DECISION.md`): **methylCIPHER (R) = pinned
  primary**; **pyaging (Python) = implementation-sensitivity check only.**

## The immediate next task (do this, don't add architecture)

Produce the first real-data result. Further conceptual/architecture refinement has
negative value now.

1. **Fast path** — score the PC-Clocks *example* replicate data with pinned
   methylCIPHER → run reliage → compare to published references.
2. **Canonical path** — rebuild the same 36-pair cohort from GSE55763 GEO files;
   score with the same pinned methylCIPHER.
3. **Do NOT claim public reproduction** until the GEO result matches the fast path
   within the prespecified tolerances in `SCORING_DECISION.md`.
4. Run the pyaging sensitivity check on overlapping clocks.

```bash
# where R + data live:
Rscript reliage/scoring/score_methylCIPHER.R  betas.csv  pheno.csv  scores.csv   # PIN COMMIT first
python -m reliage.scoring.run_analysis  scores.csv  map.csv  --out out/
# -> out/leaderboard.csv, out/contrasts.csv (primary endpoint), out/results.json, out/RESULTS.md
```

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
