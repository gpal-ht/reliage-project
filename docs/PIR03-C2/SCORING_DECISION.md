# ADR: v1 clock-scoring path (LOCKED)

**Decision:** **methylCIPHER (R) is the pinned PRIMARY scorer for v1. pyaging (Python)
is a SECONDARY, independent implementation-sensitivity check only.**

## Why

- The v1 scientific claim is about **original vs PC-transformed versions of the same
  clocks**. methylCIPHER is maintained by the group responsible for the PC-clock
  implementation and includes PC clocks (+ SystemsAge, CausalAge, DunedinPACE); the
  older PC-Clocks repo itself redirects to it. It is the authoritative source for the
  four protocol-locked pairs: **Horvath1, Hannum, PhenoAge, GrimAge** original↔PC.
- pyaging is attractive (Python-native, large consistent catalogue) but as the *only*
  scorer it would confound "difference from published PC-clock results" with "distinct
  implementation." So it is used to *test* implementation sensitivity, not to produce
  the primary result.

## v1 scoring design

```
GSE55763 beta matrix
    │
    ├─ PRIMARY: pinned methylCIPHER commit ─▶ versioned score table ─▶ reliage v0.3.0 ─▶ published-reference comparison
    │
    └─ SENSITIVITY: pyaging (overlapping clocks) ─▶ compare scores vs methylCIPHER
```

The sensitivity path answers: do matching implementations agree numerically? do they
produce the same reliability ranking and scientific verdict? and if not, is the
discrepancy from coefficients, preprocessing, missing-CpG handling, transformations,
or units?

## Provenance is MANDATORY (do not merely record "methylCIPHER")

methylCIPHER has no formal releases and its issue history shows some clock
implementations have had discrepancies/errors — so **commit-level provenance and
clock-specific checks are required**. Every score row must pin:

- repository owner + URL
- exact commit hash
- R version + package versions (methylCIPHER and deps)
- clock function called (e.g. `calcPCClocks` → `PCHorvath1`)
- preprocessing + imputation policy
- required CpG coverage (and % present for this dataset)
- transformation + output unit

Template: `reliage/scoring/PROVENANCE.template.md`. The score table carries these as
columns (long form) so no result is ever unattributable.

## Execution order (the instruction)

> ⚠ **Update (2026-07):** the **fast path** below (Box `Example_PCClock_Data.RData`) is
> **unavailable — the Yale Box link was removed.** M1 executed the **canonical GEO path directly**
> (step 2). The fast-path↔GEO cross-check (steps 1–3 + the tolerances below) therefore could not run
> as written and is **superseded by a tiered reproduction gate** (T1 reproduce published stats ·
> T2 independent GEO rebuild ✅ · T3 consistency within tolerances), to be **ratified here at Tier-3**.
> Steps below retained as the original locked instruction. Canonical status: `../tracker.md`, `CLAIMS.md`.

1. **Fast path:** score the PC-Clocks **example** replicate data with pinned
   methylCIPHER → run reliage v0.3.0 → compare to published references. Debug the
   whole pipeline cheaply.
2. **Canonical path:** rebuild the *same* replicate cohort from canonical **GSE55763**
   GEO files; score with the same pinned methylCIPHER; compare the GEO-derived result
   to the fast-path result.
3. **Do NOT claim public reproduction** until the GEO-derived result matches the
   author-prepared fast path **within prespecified tolerances** (below).
4. Run the pyaging sensitivity check on overlapping clocks.

## Prespecified cross-check tolerances (declared BEFORE running)

Fast-path (RData) vs GEO-rebuild, per clock, over the shared replicate samples:
- **Per-sample score agreement:** median |Δscore| ≤ 0.25 yr AND max |Δscore| ≤ 1.0 yr
  (age clocks). Larger ⇒ investigate preprocessing/normalization before any claim.
- **ICC agreement:** |ΔICC| ≤ 0.02 per clock.
- **Variance-ratio agreement:** the PC/original ratio verdict (supported / directional
  / not) must be identical; point ratio within ±0.15.
- **Same qualitative reliability ranking** of the four pairs.

methylCIPHER vs pyaging (sensitivity) tolerances are advisory (implementations differ
by design): report agreement, don't gate on it — but a verdict flip is a red flag to
explain, not ignore.
