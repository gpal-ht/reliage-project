# PIR03-C2 — Delivery Notes

**Contribution:** `reliage` — an open, reproducible test-retest reliability benchmark for epigenetic aging clocks.
**Source:** Project Intelligence Report 0003 ("Can We Measure Aging?"), Project 2 — a test-retest reliability harness.
> ⚠ **SUPERSEDED — historical v0.1.0 planning notes; retained for provenance, not current.**
> Current state: Milestone 001 (frozen `v0.3.1-scientific-baseline`) + Experiment E2 complete.
> Canonical now: [`../tracker.md`](../tracker.md) · [`CLAIMS.md`](CLAIMS.md) · [`../HANDOVER_v0.3.1.md`](../HANDOVER_v0.3.1.md).
> The "Not yet" items below (within-subject error, MDC95, real-data GSE55763 run) are all done.

**Status (v0.1.0, historical):** Build started, `reliage` v0.1.0 working and verified. Distribution not yet executed.

---

## 1. What the artifact is meant to be (full spec)

> A harness that, given public datasets containing technical replicates or repeat draws, computes intraclass correlation and within-subject error for each clock, and reports the minimum detectable intervention effect per clock.

Three outputs, in plain terms (bathroom-scale analogy):

1. **Intraclass correlation (ICC)** — of the number a clock reports, how much is real between-person signal vs. measurement noise (0–1). *Does the scale reflect real weight differences or just jitter?*
2. **Within-subject error** — the same information in years: measure one sample twice, how far apart are the two readings from noise alone. *This scale is typically off by ±0.8 kg.*
3. **Minimum detectable intervention effect (the punchline)** — given that noise, the smallest true effect a study could actually detect above it. *A diet that took off 0.3 kg is invisible on this scale; you'd need ≥2 kg.* → "With this clock, don't run a trial hoping to catch a 1-year effect; its floor is ~4 years."

The finished artifact is a **buyer's guide for clocks**: for each clock, three columns — how noisy (ICC), how noisy in years (within-subject error), and the smallest real effect it can detect (MDE). The third column is the actionable one: it tells a trial designer which clocks are usable before spending money.

## 2. Build status against that spec (honest)

| Output | Status in v0.1.0 |
|---|---|
| ICC (1,1 / 2,1 / 3,1) + CIs + Koo–Li bands | **Done, verified** (reproduces Shrout & Fleiss 1979 canonical values; end-to-end recovery of known ICCs) |
| Within-subject error (in years) | **Not yet** — but the within-subject variance is already computed inside the ANOVA; small addition |
| Minimum detectable effect per clock | **Not yet** — derives directly from within-subject error; the highest-value missing column |
| Real-data run (GSE55763, 36 duplicate pairs) | **Not yet** — needs the ~few-GB download, then reproduce published technical-reliability ICCs as acceptance test |

Package delivered as `reliage-0.1.0.tar.gz`. Verify with `python -m reliage.selfcheck` (no pytest needed); demo leaderboard via `python examples/quickstart.py`.

## 3. Positioning (why this exists, honestly)

The reliability *science* is already published and the *findings are not novel*. What is genuinely absent:

- **No open, rerunnable reliability tool.** TranslAGE (2025) does reliability comprehensively but is a **gated web platform** — restricted data, not independently reproducible. ComputAgeBench is open but benchmarks **accuracy only**, and its data has no technical replicates. PC-Clocks / methylCIPHER are R clock-*calculation* libraries, not benchmarks.
- **No open per-clock minimum-detectable-effect tool.** The concept is discussed in the reliability literature (Higgins-Chen framed reliability for "clinical trials and longitudinal tracking"; scattered power/ΔAge design notes exist) but no standardized open tool packages it.

So the contribution is **openness + reproducibility + a decision layer (MDE)**, not novel biology. That is squarely the Foundry Constitution's North Star (reproducible, independently checkable, challengeable) — but it is a second-mover contribution on the science, which shapes the delivery strategy below.

## 4. Delivery strategy (how it reaches people who need it)

Principle: for open research tools, distribution is **docking at ports that already have traffic**, not building a repo and hoping. Ranked by leverage:

1. **Upstream into ComputAgeBench (highest leverage).** Open, published (KDD 2025), actively maintained, and its users *are* the target audience (people benchmarking clocks). Its maintainers publicly named reliability as the gap they did not fill. A clean PR adding a reliability + MDE module ships the work to everyone already using their tool, with attribution as a contributor. This is the primary answer to "how do I reach people."
2. **Biomarkers of Aging Consortium / Biolearn ecosystem.** Organized community running open biomarker tooling and challenges around exactly this — taps a network instead of a search bar.
3. **JOSS software paper.** A short software/methods paper → citable DOI, indexed, real academic credit *without* needing novel biology (JOSS has a Bioinformatics section for exactly this). Answers "I can't publish."
4. **Living open leaderboard (Papers-With-Code model).** Anyone submits a new clock, gets reliability + MDE. New clocks appear constantly; TranslAGE is gated and snapshot-ish, so an open, always-current leaderboard is a genuinely different, complementary object with its own pull.
5. **Posture: collaborate, don't compete.** The gated-tool authors (Higgins-Chen lab) want clocks reproducible; an open harness that reproduces their ICCs on public data complements their platform. "I built an open thing that reproduces your findings, want to align" opens doors.

## 5. Open strategic decision (unresolved — for Gaurav)

Reproducing a contested-but-gated result is the hardest place for a solo dev to have outsized impact — second-mover by construction. The underlying question:

- If the goal is **"open up reliability specifically"** → continue PIR03-C2; execute the delivery plan above (add error + MDE, run GSE55763, upstream to ComputAgeBench, JOSS).
- If the goal is **"my work gets used / reach"** → weigh a **first-mover** candidate instead: PIR01-C2 (ITP reanalysis — raw data public, *zero* reproducible code exists) or the evidence-map trio. Easier adoption and publication story because nobody is there yet.

Not yet decided. This is the next real fork before more code.

## 6. Concrete next actions

- [ ] Decide the strategic fork in §5.
- [ ] (If continuing) add within-subject error (years) + minimum-detectable-effect columns to the leaderboard — small, high-value, derives from existing ANOVA.
- [ ] Fetch GSE55763; run real-data acceptance test (reproduce published technical-reliability ICCs with ComputAgeBench clocks).
- [ ] Draft the ComputAgeBench PR (scope it to what their maintainers would accept).
- [ ] Widen datasets: SATSA (E-MTAB-7309), an EPIC-array replicate set; add a biological-reliability mode.

## References

- ComputAgeBench — https://github.com/ComputationalAgingLab/ComputAge (KDD 2025)
- TranslAGE reliability paper — https://www.biorxiv.org/content/10.1101/2025.10.13.682176v2.full
- Higgins-Chen et al., PC-clocks, *Nature Aging* 2022 — https://www.nature.com/articles/s43587-022-00248-2
- GSE55763 (Lehne et al. 2015, anchor replicate dataset) — https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE55763
- JOSS (software publication venue) — https://joss.theoj.org/
