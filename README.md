# reliage

[![CI](https://github.com/gpal-ht/reliage-project/actions/workflows/ci.yml/badge.svg)](https://github.com/gpal-ht/reliage-project/actions/workflows/ci.yml)

**reliage is an open-source Python package (library + command-line tool)
implementing the measurement-science framework for aging biomarkers. Version 1
benchmarks the technical reliability of epigenetic clocks.**

- **Today (v1):** technical reliability of epigenetic clocks.
- **Long-term mission:** the reference implementation of measurement science for
  aging biomarkers — agreement, uncertainty, calibration, limits of detection,
  responsiveness, on the same architecture. See [`docs/PIR03-C2/VISION.md`](docs/PIR03-C2/VISION.md).

---

## The problem

You are designing a longevity intervention study. You will measure each
participant's epigenetic age before and after, and you expect the intervention to
turn back the clock by, say, **1.5 years**. Before you spend the money, one
question decides whether the study can work at all:

> **If I measured the *same* person's blood twice, how far apart would the two
> readings be — from the assay alone, with no biological change?**

If that measurement noise is ±2 years, a 1.5-year effect is *invisible*: you
cannot tell a real reversal from run-to-run jitter. If it is ±0.3 years, the
effect is easily detectable. Same clock, same sample — the answer depends entirely
on the clock's **technical reliability**, and it is different for every clock.

## Questions reliage answers

- **How reliable is this clock?** How much do two measurements of the *same*
  sample disagree — the within-subject error (SD / SEM), ICC, and repeatability.
- **What change can I trust?** What is the smallest change that exceeds this
  clock's measurement noise (**MDC95**) — so a participant's 3-year drop can be
  called *real* or *noise*.
- **Which clock should I run for my trial?** Given the effect size I expect (say
  1.5 years), which clocks can actually detect it and which are too noisy — chosen
  *before* committing to a design, not after a null result.
- **Is the "more reliable" version actually more reliable?** How much less
  within-subject noise does a PC-transformed clock have than its original (the
  variance-ratio endpoint) — measured on independently rebuilt public data, so the
  claim is checkable, not taken on trust.

## Questions reliage does *not* answer

- **Is the clock *accurate*?** (Close to true chronological/biological age — that
  is [ComputAgeBench](https://github.com/ComputationalAgingLab/ComputAge)'s job.)
- **Is a change *biologically* meaningful?** A clock can be rock-solid technically
  and still be biologically noisy; reliage measures the technical floor those other
  questions sit on top of.

## Who this is for

**reliage is for you if you** develop or compare aging biomarkers, design
intervention studies, benchmark measurement reliability, or run reproducibility
studies on epigenetic clocks.

**reliage is *not* the tool if you need** methylation preprocessing, clock
*calculation* itself (that is the scorer's job — methylCIPHER / pyaging),
biological-age prediction, or interpretation of what a change *means* biologically.
reliage sits one layer above scoring and one layer below biology.

## How it works

reliage's **measurement engine is scorer-agnostic** — it never touches raw
methylation data. It consumes a *score table + replicate map* through the
**Versioned Score Table** contract:

```
        Raw methylation data
                 │
                 ▼
   External scorer  (methylCIPHER / pyaging / your own clock)
                 │
                 ▼
      Versioned Score Table      ← the contract
                 │
                 ▼
            reliage              ← ICC · within-subject error · variance ratio
                 │
                 ▼
     Measurement capability      ← "reliable enough for WHAT?"
```

The **Versioned Score Table is the contract between biomarker scoring and
measurement science**: any scorer that produces this artifact can be evaluated by
reliage without modification. Experiment E2 showed this is a *validated* contract,
not just an architectural idea — methylCIPHER and pyaging both drove the same
pipeline to the same verdict.

So reliage's contribution is not "it computes ICC." It is that every reliability
result is **independently reconstructable, scorer-agnostic, provenance-aware, and
reproducible** from a clean environment — depending on **neither** ComputAgeBench
nor any methylation pipeline.

This is contribution **PIR03-C2** in the Frontier Research Foundry engineering
tracker (Project Intelligence Report 0003, "Can We Measure Aging?", Project 2:
a test-retest reliability harness).

---

## Using reliage

You need **Python 3.10+** and **git**. reliage is not on PyPI yet, so it installs
from this repository.

### Run the demo — copy, paste, done

These four commands go from an empty terminal to a full reliability report. They
run on a small example dataset bundled in the repo, so **nothing else to download**:

```bash
git clone https://github.com/gpal-ht/reliage-project.git
cd reliage-project
pip install .
python -m reliage.scoring.run_analysis examples/example_scores.csv examples/example_map.csv --out out/
```

Then open the results in `out/` (see [what you get](#what-you-get) below). The
bundled example is a synthetic score table with four original↔PC clock pairs, drawn
with *equal* reliability per pair — so the report is a neutral illustration of the
output format, not a staged result. On real data (below), the PC variants separate
from their originals.

### Run on your own data

reliage works on clock **scores**, not raw methylation data. You give it two CSVs:

- **`scores.csv`** — first column `sample_id`, then one column per clock:

  | sample_id | Horvath1 | PCHorvath1 | … |
  |---|---|---|---|
  | P01_run1 | 51.2 | 50.8 | … |
  | P01_run2 | 49.7 | 50.6 | … |

- **`map.csv`** — which samples are repeat measurements of the same person:

  | subject | sample_id |
  |---|---|
  | P01 | P01_run1 |
  | P01 | P01_run2 |

Then run the same command on your files:

```bash
python -m reliage.scoring.run_analysis scores.csv map.csv --out out/
```

The scores themselves come from an **external scorer** (reliage never touches
methylation betas). The pinned v1 primary scorer is **methylCIPHER** (in R);
**pyaging** or your own clock work too — anything emitting the **Versioned Score
Table** format:

```bash
Rscript reliage/scoring/score_methylCIPHER.R betas.csv pheno.csv scores.csv
```

### What you get

The run writes four files to `out/`:

| File | What it holds |
|---|---|
| `leaderboard.csv` | per-clock ICC + within-subject error (SD / SEM / **MDC95**) + reliability band |
| `contrasts.csv` | PC-vs-original within-subject **variance ratio** (the primary endpoint) + bootstrap CI |
| `RESULTS.md` / `results.json` | human- and machine-readable summary |

### Prefer Python?

The same benchmark runs as a library call, on tables you already hold in memory.
This snippet is self-contained — it makes its own synthetic scores, so it runs as-is:

```python
from reliage import simulate_replicate_scores, run_reliability_benchmark

scores, groups = simulate_replicate_scores(clock_iccs={"ClockA": 0.9, "ClockB": 0.6})
board = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
print(board.to_markdown())
```

For a fuller runnable walkthrough with commentary: `python examples/quickstart.py`.

### On real public data (GSE55763)

The v1 result was produced on GSE55763 (Lehne et al., *Genome Biology* 2015):
Illumina 450K, 36 samples measured in duplicate across separate batches — a
ready-made cross-batch technical-replicate design. Exact, reproducible commands are
in [`docs/PIR03-C2/PIPELINE.md`](docs/PIR03-C2/PIPELINE.md); a self-contained
independent-reproduction guide (pinned versions, data checksums, expected values
**with tolerances**) is in
[`docs/PIR03-C2/REPRODUCTION_PACKAGE.md`](docs/PIR03-C2/REPRODUCTION_PACKAGE.md).

> Contributors: `pip install -e ".[dev]"` installs the test extras; run the suite
> with `pytest -q` and the dependency-light correctness gates with
> `python -m reliage.selfcheck`.

---

## What it computes

- **ICC(2,1)** by default — two-way random effects, *absolute agreement*, single
  measurement. This is the right test-retest metric: it asks whether repeat
  measurements *agree in value*, not merely correlate. A clock with a systematic
  between-batch drift is correctly penalised by ICC(2,1) while ICC(3,1)
  consistency would miss it (the quickstart demonstrates exactly this).
- Also **ICC(1,1)** and **ICC(3,1)**, F-distribution confidence intervals, and
  Koo & Li (2016) qualitative bands (excellent / good / moderate / poor).
- **Within-subject error** (SD / SEM), coefficient of repeatability, Bland–Altman
  limits of agreement, and **MDC95** (the smallest detectable change per individual).
- **PC-vs-original within-subject variance ratio** (the primary endpoint) with
  paired-bootstrap confidence intervals.
- **Detectability screen** — for a planned effect size, whether it clears each
  clock's individual measurement-noise floor. A screen, not a power calculation.

Each metric maps to a decision you actually make:

| Metric | Supports the decision |
|---|---|
| **ICC** | Overall repeatability — can this clock rank people consistently? |
| **SEM / within-subject SD** | Typical measurement error on one reading |
| **MDC95** | Smallest change in one individual you can call real (not noise) |
| **Variance ratio** | Whether the PC transform actually improves reliability |
| **Detectability screen** | Whether a planned intervention effect clears the measurement-noise floor |

## Verification

Two independent, literature-anchored correctness checks — run without pytest:

```bash
python -m reliage.selfcheck
```

1. **ICC engine** reproduces the canonical Shrout & Fleiss (1979) worked example
   (published ICC(1,1)=0.17, ICC(2,1)=0.29, ICC(3,1)=0.71).
2. **End-to-end**, the benchmark recovers known target ICCs from a synthetic
   generator and ranks clocks in the correct reliability order.

Full test suite (needs pytest): `pytest -q`.

## Design philosophy

- **Scorer-agnostic architecture** — measurement science is separated from clock scoring.
- **Versioned Score Table contract** — one validated exchange format between the two.
- **Reproducibility by default** — pinned provenance, public data, clean-room reruns.
- **Evidence before confidence** — claims stay provisional until the evidence supports them.

---

## Why this exists (the gap)

The reliability *science* is already published; an open, reproducible *tool* is not.

| Tool | Language | Open? | Benchmarks reliability (ICC)? |
|---|---|---|---|
| **ComputAgeBench** | Python | Yes (CC BY-SA) | No — accuracy only; its data has no technical replicates |
| **PC-Clocks** | R | Yes | No — computes reliable PC-clocks, but no ICC/benchmark harness (unmaintained) |
| **methylCIPHER** | R | Yes | No — clock *calculation* library only |
| **TranslAGE** (2025) | web platform | **No — gated** | Yes, comprehensively — but web-only, dataset downloads restricted, not independently reproducible |
| **reliage** | Python | **Yes (MIT)** | **Yes — open, rerunnable, on public data** |

The reliability findings themselves are established (clocks are typically
*technically* reliable, ICC > 0.9, but far less *biologically* stable, ICC ≈
0.4–0.7; PC-transformation improves reliability). `reliage` does not claim those
findings as new. Its contribution is making the benchmark that produces them
**open, reproducible, Python-native, and scorer-agnostic** — the
Foundry Constitution's "reproducible, independently checkable, challengeable"
property, applied to clock reliability.

## Scientific status

**Real-data milestone — ACHIEVED (Milestone 001, frozen tag `v0.3.1-scientific-baseline`):** on
public GSE55763 replicate data (36 cross-batch technical-replicate pairs), PC-transformed clocks
reduce within-subject technical variance vs their originals (supported 4/4), turning a gated result
into an open, rerunnable one — and the conclusion is **implementation-robust** (Experiment E2).

**Where the science lives** (the scientific state is tracked separately from any
report — reports support the claims, they don't define them):

- [`docs/PIR03-C2/CLAIMS.md`](docs/PIR03-C2/CLAIMS.md) — the current scientific state (what is / isn't yet supported).
- [`docs/FOUNDRY_PRINCIPLES.md`](docs/FOUNDRY_PRINCIPLES.md) — how the project decides what counts as evidence.
- [`docs/tracker.md`](docs/tracker.md) — live project tracker · [`docs/HANDOVER_v0.3.1.md`](docs/HANDOVER_v0.3.1.md) — full handover.

## Roadmap

- [x] Verified ICC engine (ICC 1/2/3, CIs, Koo–Li bands)
- [x] Score-based reliability benchmark + leaderboard
- [x] Synthetic generator with known ICCs (end-to-end verification)
- [x] GSE55763 loader path + generic replicate-group builder
- [x] **Real-data run on GSE55763 with pinned methylCIPHER — supported 4/4 (M1)** — scorer is methylCIPHER, not ComputAgeBench (accuracy-only; not a dependency)
- [x] **Robustness suite: compression audit, LOSO, Bland–Altman, outliers — selective denoising (M1)**
- [x] **Implementation-robustness check vs pyaging — robust (E2)**
- [x] **Tier-3 published-reference comparison vs Higgins-Chen 2022 — agreement (scoped; two clocks PARTIAL)**
- [x] **ICC-form sensitivity (ICC 1,1 / 3,1) — verdict invariant**
- [x] **Public CI (pytest, py3.10–3.13) — green**
- [x] **v1 protocol frozen (`docs/PIR03-C2/PROTOCOL_FREEZE.md`)**
- [ ] Independent third-party rerun (package ready) — **gates the v1.0 tag** (CLAIMS #8)
- [ ] v1.0 release (held pending the independent rerun) + normalized Versioned Score Table spec freeze
- [ ] Add SATSA (E-MTAB-7309) and an EPIC-array replicate set (v2)
- [ ] Biological-reliability mode (within-subject short-interval replicates) (v2)

## References

- Shrout & Fleiss (1979) *Psychol Bull* — ICC forms.
- McGraw & Wong (1996) *Psychol Methods* — ICC confidence intervals.
- Koo & Li (2016) *J Chiropr Med* — ICC reporting & reliability bands.
- Lehne et al. (2015) *Genome Biol* — GSE55763 (450K, technical replicates).
- Higgins-Chen et al. (2022) *Nature Aging* — PC-clocks reliability.
- Kriukov et al. (2025) *KDD* — ComputAgeBench.

## License

MIT (code). GSE55763 data, methylCIPHER/pyaging, and the PC-clock reference each carry their own licenses.
