# reliage

**The open reference implementation of measurement science for epigenetic clocks.**
_Version 1: technical reliability. (Roadmap: agreement, uncertainty, calibration,
limits of detection, responsiveness — same architecture. See `Contributions/PIR03-C2/VISION.md`.)_

`reliage` is the *reliability* companion to [ComputAgeBench](https://github.com/ComputationalAgingLab/ComputAge)
(which benchmarks clock *accuracy*). It answers a different question: **how
stable is a clock's estimate when the same biological sample is measured more
than once?** It computes an intraclass-correlation (ICC) leaderboard across
clocks on public technical-replicate data, so a clock's reliability can be
audited, reproduced, and challenged from a clean environment.

This is contribution **PIR03-C2** in the Frontier Research Foundry engineering
tracker (Project Intelligence Report 0003, "Can We Measure Aging?", Project 2:
a test-retest reliability harness).

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
**open, reproducible, Python-native, and composable with ComputAgeBench** — the
Foundry Constitution's "reproducible, independently checkable, challengeable"
property, applied to clock reliability.

---

## Install

```bash
pip install -e .            # core (numpy, pandas, scipy)
pip install -e ".[computage]"   # + score beta matrices with ComputAgeBench clocks
pip install -e ".[dev]"         # + pytest
```

## Quickstart (no downloads)

```bash
python examples/quickstart.py
```

```python
from reliage import run_reliability_benchmark, simulate_replicate_scores

scores, groups = simulate_replicate_scores(clock_iccs={"ClockA": 0.95, "ClockB": 0.6})
board = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
print(board.to_markdown())
```

`scores` is a table indexed by sample id with one column per clock; `groups`
maps each subject to its replicate sample ids. That's all the reliability core
needs — whatever produced the scores (ComputAgeBench, methylCIPHER, your own
clock), reliability is computed identically.

## On real public data (GSE55763)

The confirmed public anchor dataset is **GSE55763** (Lehne et al., *Genome
Biology* 2015): Illumina 450K, 2,711 samples of which **36 are measured in
duplicate** — a ready-made technical-replicate design, and the same set shipped
as PC-Clocks' example replicate data.

```python
from reliage import load_gse55763, score_samples, run_reliability_benchmark
from reliage.clocks import computage_clock

betas, groups = load_gse55763("data/gse55763/betas.parquet",
                              "data/gse55763/meta.parquet")
scores = score_samples(betas, {"PhenoAge": computage_clock("PhenoAge"),
                               "Hannum":   computage_clock("Hannum")})
board = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
print(board.to_markdown())
```

(You fetch GSE55763 once yourself; `load_gse55763` parses what you downloaded so
the run stays reproducible with an explicit provenance trail. See its docstring.)

---

## What it computes

- **ICC(2,1)** by default — two-way random effects, *absolute agreement*, single
  measurement. This is the right test-retest metric: it asks whether repeat
  measurements *agree in value*, not merely correlate. A clock with a systematic
  between-batch drift is correctly penalised by ICC(2,1) while ICC(3,1)
  consistency would miss it (the quickstart demonstrates exactly this).
- Also **ICC(1,1)** and **ICC(3,1)**, F-distribution confidence intervals, and
  Koo & Li (2016) qualitative bands (excellent / good / moderate / poor).

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

**Acceptance target for the real-data milestone:** reproduce the published
technical-reliability ICCs for named clocks from the reliability literature
(e.g. PC-clocks reliable, several second-gen clocks technically reliable but
biologically less so) on public replicate data — turning a gated result into an
open, rerunnable one.

---

## Roadmap

- [x] Verified ICC engine (ICC 1/2/3, CIs, Koo–Li bands)
- [x] Score-based reliability benchmark + leaderboard
- [x] Synthetic generator with known ICCs (end-to-end verification)
- [x] GSE55763 loader path + generic replicate-group builder
- [ ] Run on downloaded GSE55763 with ComputAgeBench clocks (real-data acceptance)
- [ ] Add SATSA (E-MTAB-7309) and an EPIC-array replicate set
- [ ] Biological-reliability mode (within-subject short-interval replicates)
- [ ] Publish leaderboard; propose upstreaming to ComputAgeBench

## References

- Shrout & Fleiss (1979) *Psychol Bull* — ICC forms.
- McGraw & Wong (1996) *Psychol Methods* — ICC confidence intervals.
- Koo & Li (2016) *J Chiropr Med* — ICC reporting & reliability bands.
- Lehne et al. (2015) *Genome Biol* — GSE55763 (450K, technical replicates).
- Higgins-Chen et al. (2022) *Nature Aging* — PC-clocks reliability.
- Kriukov et al. (2025) *KDD* — ComputAgeBench.

## License

MIT (code). GSE55763 and ComputAgeBench data carry their own licenses.
