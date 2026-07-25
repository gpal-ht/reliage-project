# PIR03-C2 — Plan: Test on Public Data, Present Findings, Represent Output

> ⚠ **Largely EXECUTED / partly superseded — historical plan; not current status.** The plan below
> was carried out in Milestone 001 + Experiment E2. Note: the "fast path" (Box `Example_PCClock_Data.RData`)
> is **unavailable (removed)**; M1 used the GEO canonical path directly. Canonical status:
> [`../tracker.md`](../tracker.md) · [`CLAIMS.md`](CLAIMS.md) · results in [`TECHNICAL_REPORT_v0.1.md`](TECHNICAL_REPORT_v0.1.md), [`IMPLEMENTATION_COMPARISON.md`](IMPLEMENTATION_COMPARISON.md).

TranslAGE is dropped as a target (gated, not reproducible). The acceptance goal
is now clean and self-contained:

> **Reproduce, on fully public data with open code, the established finding that
> PC-transformed clocks are substantially more reliable than their originals —
> and report each clock's reliability in a form a trial designer can act on.**

---

## Part A — Testing against a public dataset

### A.1 Dataset
**GSE55763** (Lehne et al. 2015, Illumina 450K) — **36 technical-replicate pairs**
(same sample measured twice). This supports **technical** reliability only; it has
no biological repeat-draws, so only Tier-A cases in `acceptance_cases.yaml` apply.
Biological reliability (Tier B) is a later milestone needing a public repeat-draw
dataset — deferred, not attempted here.

Two ways to get the replicate data:
- **Fast path (recommended):** PC-Clocks ships `Example_PCClock_Data.RData` — the
  Lehne replicate subset, already extracted and small. Start here; no multi-GB
  download.
- **Full path:** `GEOparse.get_GEO("GSE55763")`, then subset to the 72 replicate
  samples via the series metadata. Needed only to scale beyond the example set.

### A.2 Pipeline (six steps)
1. **Prereq — extend `reliage`:** add the two missing outputs (within-subject
   error in years, minimum detectable effect) to the leaderboard. Small; both
   fall out of the ANOVA already computed. Needed for case A3 and for the
   actionable columns.
2. **Get replicate data** (fast path above) → a beta matrix for the 72 samples +
   a replicate map (subject → its 2 sample ids).
3. **Compute clock scores.** Use **methylCIPHER (R)** — it produces *both* the
   original clocks (Horvath, Hannum, PhenoAge, GrimAge, DunedinPACE) *and* their
   **PC versions**, which is exactly what the PC-vs-original test needs. Export
   scores to a CSV (sample × clock). *(ComputAgeBench (Python) can supply the
   originals in-ecosystem, but not the PC versions — so methylCIPHER is the
   definitive source for the headline comparison.)*
4. **Run `reliage`** on the scores CSV + replicate map →
   ICC(2,1) leaderboard with CIs, within-subject error (yrs), and MDE (yrs).
5. **Assert acceptance** by loading `acceptance_cases.yaml` and checking Tier A:
   - A1 — PC clocks land "excellent" (ICC ≥ 0.90)
   - A2 — PC version out-reliables its original (ordering); originals ~0.7–0.8
   - A3 — within-subject error: original ≫ PC (the "9 years → 1.5 years" result)
6. **Interpret & record** in `RESULTS.md`.

### A.3 What to expect, honestly
- **n = 36 pairs is small** → confidence intervals will be wide. Report the CIs;
  don't over-read point estimates.
- **Success = pattern reproduced, not exact numbers.** The claim is "PC ≫ original,
  PC reaches excellent," which is robust; matching a specific 0.9x to two decimals
  on a different/smaller dataset is not the bar (and would be false precision).
- If PC clocks land "excellent" and beat their originals with a visible
  within-subject-error drop, the acceptance passes and the reproducibility claim
  is earned.

---

## Part B — How to present findings

Lead with **reproducibility, not novelty**: "an open, rerunnable confirmation of a
result that previously required gated tools." Three artifacts for three readers:

| Artifact | Reader | Contents |
|---|---|---|
| `RESULTS.md` | repo / reviewer | Claim → data → method → result table → caveats → "what it means for a trial designer". Foundry courtroom style (scoped, labelled, defeater named). |
| `results.csv` + `results.json` | other tools / pipelines | The leaderboard as machine-readable data. |
| **HTML leaderboard** | humans / sharing | The headline (Part C). |

Write-up spine (short, honest): *what we ran → on what public data → how (ICC(2,1),
Koo–Li bands) → the leaderboard → caveats (small n, technical-only) → the takeaway
(which clocks a study can actually use, and the smallest effect each can detect).*

---

## Part C — Accessible output format (recommended)

**Primary deliverable: a single self-contained HTML "clock reliability leaderboard"**
— a revisit-by-nature artifact (people come back to it, it updates as clocks/datasets
are added), so it's persisted as an artifact, not just a file.

Contents, top to bottom:
1. **Plain-language header** — "Can you trust this clock? And how much change can it
   actually detect?" One sentence each on ICC, within-subject error, and MDE.
2. **Sortable table** — one row per clock:
   `Clock | ICC(2,1) | 95% CI | Within-subject error (yrs) | Min. detectable effect (yrs) | Reliability` (color band chip).
3. **Forest / caterpillar plot** — ICC ± 95% CI per clock, sorted, colored by
   Koo–Li band, with threshold lines at 0.75 (good) and 0.90 (excellent). This is
   the single most legible reliability visual.
4. **Companion bar — "buyer's guide"** — minimum detectable effect (years) per
   clock. The shorter the bar, the smaller the effect that clock can detect. This
   is the view a trial designer scans.
5. **Footer** — provenance (GSE55763, 36 pairs), method (ICC(2,1), Koo–Li), the
   one-line command to reproduce, and the caveats.

Also emit **static PNGs** (for slides/README) and the **CSV/JSON** (for reuse).
Charts built via the `dataviz` skill (accessible palette, light+dark, colorblind-safe).

**Why HTML artifact:** a leaderboard is the canonical "come back to it / show
someone" object; self-contained HTML makes it shareable and updatable, and it's the
natural surface to grow into the living, always-current leaderboard from the delivery
plan.

---

## Suggested order of execution
1. Add within-subject error + MDE to `reliage` (unblocks A3 and the actionable columns).
2. Build the **HTML leaderboard shell now, using the synthetic/quickstart data** as a
   stand-in — so the format is concrete and reviewable *before* the data download.
3. Score GSE55763 replicates via methylCIPHER → CSV.
4. Run `reliage`, assert Tier A, swap real numbers into the leaderboard, write `RESULTS.md`.
5. (Later) add a public repeat-draw dataset for biological reliability (Tier B).

## Open choices (pick before step 3)
- **Clock scoring:** methylCIPHER (R, gives PC versions — recommended) vs. ComputAgeBench
  (Python, originals only). Recommendation: methylCIPHER for scoring, `reliage` (Python)
  for the reliability math; bridge via CSV.
- **Output surface:** HTML artifact (recommended) vs. a Jupyter notebook vs. static
  report. HTML is the most accessible and shareable.
