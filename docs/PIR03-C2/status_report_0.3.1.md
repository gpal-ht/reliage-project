# reliage — Real-Data Execution Status (status_report_0.3.1)

**PIR03-C2 · reliage v0.3.1 · status review · snapshot 2026-07-24**

First real-data run of the technical-reliability benchmark for epigenetic clocks:
*do PC-transformed clocks reduce technical measurement error vs their originals on
independently rebuilt public replicate data (GSE55763)?*

| | |
|---|---|
| Current gate | **Gate 1 of 3 — Execution Readiness** (see ladder below) |
| Scorer | methylCIPHER `@9e8c1e5` (locked) |
| Dataset | GSE55763 (Lehne 2015), 36 technical-replicate pairs |
| Runtime | R 4.6.1 · Rtools45 · Windows |

### Execution gate ladder

Real-data execution is not one milestone but three distinct gates. We are at the first.

```
[▣ Gate 1] Execution Readiness       ← WE ARE HERE (environment + scorer + pipeline proven)
    ↓
[▢ Gate 2] Data Successfully Processed  (GSE55763 scored → versioned score table exists)
    ↓
[▢ Gate 3] Scientific Result Produced   (pipeline run, verdict recorded as-is)
```

Crossing Gate 3 is the transition from an engineering project to a scientific contribution.

---

## ⚠ Evidence state — no real-data scientific result yet

The core hypothesis remains **untested by this implementation**. Every claim to date is
**software- and validation-only**. This report covers *execution readiness, not findings*.
A "PC reduces / does not reduce error" verdict exists only after the pipeline runs on the
downloading betas.

### Scientific claim gates

Three different things get validated at different times — validated *software*, validated
*statistics*, and validated *scientific conclusions* are not the same claim.

| Claim | Status |
|-------|--------|
| ICC implementation is correct | ✅ Software validated (vs Shrout–Fleiss) |
| Bootstrap / variance-ratio implementation is correct | ✅ Synthetic validation |
| Pipeline executes end-to-end on real data | 🟡 Awaiting GSE55763 |
| PC clocks reduce technical error | ⏳ Not yet tested |
| Published results independently reproduced | ⏳ Not yet tested |
| Open reproducible benchmark demonstrated | ⏳ Awaiting GEO rebuild |

---

## At a glance

- **Pipeline readiness:** 100% — coded and verified end-to-end.
- **Blocking on:** 1 download — `GSE55763_normalized_betas.txt.gz` (9.7 GB), in progress.
- **PC reference:** complete and read-verified (2.0 GB, Zenodo).

---

## Execution phases

| # | Phase | Status | Detail |
|---|-------|--------|--------|
| 1 | Environment | ✅ Done | R 4.6.1 + Rtools45; methylCIPHER 0.2.0 pinned to `9e8c1e5`; `qs2`/`stringfish` DLL-load failure fixed via source rebuild. |
| 2 | Scorer correctness | ✅ Done | Scorer rewritten against real 0.2.0 API; GrimAge locked to **V1** per manifest; originals + PC verified on bundled example. |
| 3 | Data acquisition | 🔵 In progress | PC reference complete & read-verified. Replicate map + pheno rebuilt from GEO metadata (36 pairs, verified). Betas (9.7 GB) downloading. |
| 4 | Build score table | ⚪ Staged | Extract 72 replicate columns → score (originals V1 + PC) → provenance-pinned `scores.csv`. Extractor validated on partial file. |
| 5 | Analysis & report | ⚪ Staged | Leaderboard (ICC / SEM / MDC95) + variance-ratio paired contrasts (primary endpoint) + detectability screen → first real `RESULTS.md`. |
| 6 | Interpret & record | ⚪ Staged | Read verdict honestly (a "not supported" from a correct run is a valid finding); write `PROVENANCE.md`; update `docs/tracker.md`. |

---

## Key changes this session

- **[Correction] GrimAge original: V2 → V1.** The scorer used `calcGrimAgeV2`; the locked
  `CLOCK_MANIFEST.csv` pairs original GrimAge as **V1** with PCGrimAge. The unresolved
  "PIN V1 vs V2" TODO is now closed to V1 and recorded in provenance.
- **[Correction] Scorer API mismatch.** The script targeted an older methylCIPHER API (wrong
  argument names, lowercase pheno columns). Rewritten against 0.2.0:
  `calcGrimAgeV1(DNAm, pheno)`, `calcPCClocks(DNAm, pheno, RData)`, capitalized `Age`/`Female`,
  row-aligned pheno, and a PC-failure fallback that still emits the originals leaderboard.
- **[Pivot] Fast-path data source dead.** The Yale Box link for `Example_PCClock_Data.RData`
  is removed/unavailable. Pivoted to the canonical GSE55763 GEO route — which was the
  public-reproduction target anyway.
- **[Pivot] PC reference from Zenodo, not Box.** methylCIPHER's `download_methylCIPHER` offers
  a no-auth Zenodo path (DOI `10.5281/zenodo.19455622`), avoiding the 2 GB Box
  `CalcAllPCClocks.RData` entirely.
- **[Recovered] 36-pair structure rebuilt from metadata.** 72 replicate samples = batch-1 &
  batch-2 of 36 individuals; every subject has exactly 2 measurements (0 malformed). Built
  entirely from the 50 KB series matrix — no dependence on the 9.7 GB file.

---

## Locked provenance

| Item | Pinned value | Status |
|------|--------------|--------|
| Scorer | `methylCIPHER 0.2.0 @ 9e8c1e5` | installed |
| GrimAge variant | `V1 (calcGrimAgeV1)` | locked · manifest |
| Clock pairs | Horvath1 · Hannum · PhenoAge · GrimAge | 4 × original↔PC |
| PC reference | `PCClocks_data.qs2` · Zenodo `10.5281/zenodo.19455622` | downloaded · read-OK |
| Betas | `GSE55763_normalized_betas.txt.gz` | downloading |
| Imputation | mean (PC clocks) | recorded |

### External artifact availability (historical note for future readers)

| | |
|---|---|
| Original fast-path dataset | `Example_PCClock_Data.RData` (Yale Box) — **unavailable (removed)** |
| Canonical source | GEO **GSE55763** (retained public archive) |
| Reason for change | External artifact disappeared; pivoted to the canonical public archive |

This is why the fast-path/canonical two-step collapsed into a single canonical-only route.

---

## For review — decisions & open items

- **[Protocol · to ratify after first result] Reproduction gate → tiered hierarchy.**
  `SCORING_DECISION.md` gated the public-reproduction claim on GEO results matching the *Box
  fast-path* within tolerances. The Box artifact no longer exists, so that exact cross-check is
  impossible. Rather than simply substitute "match published figures," redefine the gate as a
  hierarchy that keeps the emphasis on *independent reconstruction*, not only matching numbers:
    - **Tier 1 — Reproduce** published summary statistics (anchor: Higgins-Chen PC raw ICC > 0.99;
      accel ICC ~0.97).
    - **Tier 2 — Rebuild** the GEO cohort independently from source (GSE55763, in progress).
    - **Tier 3 — Consistency** — the independently rebuilt cohort yields results consistent with
      published findings within prespecified tolerances.

  Agreed direction; **ratify into `SCORING_DECISION.md` only after the first `RESULTS.md` exists**
  (no protocol rewrite before the result).
- **[Caveat] Scoring not yet run at full scale.** The pipeline is proven on 5 samples × 4,818
  CpGs; the real run is 72 samples × ~485k CpGs (originals + a 2 GB PC reference held in
  memory). Expect a heavier compute pass; coverage will be far better than the truncated example.
- **[Confirmed] n = 36 pairs.** Small n → wide ICC confidence intervals by design; report ICC
  *with* absolute error and Koo–Li bands, never a bare point estimate.
- **[Note] Cross-batch by design.** The two measurements were deliberately processed in separate
  batches — this estimates reliability under that specific stress, which should be stated as a
  scope condition.

---

*reliage · open metrology layer for aging biomarkers · software + synthetic-validation claims
only · no result claimed.*
