# reliage

[![CI](https://github.com/gpal-ht/reliage-project/actions/workflows/ci.yml/badge.svg)](https://github.com/gpal-ht/reliage-project/actions/workflows/ci.yml)

**The open reference implementation of measurement science for epigenetic clocks.**
_Version 1: technical reliability. (Roadmap: agreement, uncertainty, calibration,
limits of detection, responsiveness — same architecture. See `Contributions/PIR03-C2/VISION.md`.)_

`reliage` benchmarks clock **reliability** — a different axis from *accuracy* tools like
[ComputAgeBench](https://github.com/ComputationalAgingLab/ComputAge): **how stable is a clock's
estimate when the same biological sample is measured more than once?** It is **scorer-agnostic** —
it consumes a *score table + replicate map* from any scoring engine (v1 uses methylCIPHER) via the
**Versioned Score Table** contract, then reports an ICC leaderboard, within-subject error, and the
PC-vs-original within-subject variance ratio — so a clock's reliability can be audited, reproduced,
and challenged from a clean environment. It depends on **neither** ComputAgeBench nor any
methylation pipeline.

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
**open, reproducible, Python-native, and scorer-agnostic** — the
Foundry Constitution's "reproducible, independently checkable, challengeable"
property, applied to clock reliability.

---

## Install

```bash
pip install -e .            # core engine (numpy, pandas, scipy)
pip install -e ".[dev]"     # + pytest
```

Scoring (betas → scores) is done by an **external scorer**, not reliage: the pinned v1 primary is
**methylCIPHER** (R); **pyaging** is the implementation-sensitivity check. reliage never touches
betas — it consumes the score table they emit. See `docs/PIR03-C2/PIPELINE.md` and
`docs/PIR03-C2/REPRODUCTION_PACKAGE.md`.

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
needs — whatever produced the scores (methylCIPHER, pyaging, your own
clock), reliability is computed identically.

## On real public data (GSE55763)

The v1 result was produced on **GSE55763** (Lehne et al., *Genome Biology* 2015): Illumina 450K,
with **36 samples measured in duplicate across separate batches** — a ready-made cross-batch
technical-replicate design (the same replicate data the published reliability figures used). The
end-to-end pipeline is:

```
raw betas (GEO)  →  reconstruct replicate design  →  score with pinned methylCIPHER (R)
   →  Versioned Score Table (scores.csv)  →  reliage engine  →  reliability + variance-ratio verdict
```

Exact, reproducible commands: **`docs/PIR03-C2/PIPELINE.md`**. A self-contained
independent-reproduction guide (pinned versions, data md5, expected values **with tolerances**) is
in **`docs/PIR03-C2/REPRODUCTION_PACKAGE.md`**. Because reliage consumes only the score table +
replicate map, any scorer emitting the Versioned Score Table schema runs the pipeline unchanged
(demonstrated in E2, where pyaging reproduced the result).

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

**Real-data milestone — ACHIEVED (Milestone 001, frozen tag `v0.3.1-scientific-baseline`):** on
public GSE55763 replicate data (36 cross-batch technical-replicate pairs), PC-transformed clocks
reduce within-subject technical variance vs their originals (supported 4/4), turning a gated result
into an open, rerunnable one — and the conclusion is **implementation-robust** (Experiment E2).
Canonical status: `docs/tracker.md`, `docs/PIR03-C2/CLAIMS.md`; full handover `docs/HANDOVER_v0.3.1.md`.

---

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
