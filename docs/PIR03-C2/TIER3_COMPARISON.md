# Tier-3 — Published-Reference Comparison (reliage vs Higgins-Chen 2022)

**Verdict: primary reproduction PASS; overall PARTIAL.** On the specific published per-clock
figures (Horvath1, GrimAge) and every ICC-band check, reliage's frozen M1 GSE55763 results agree
with Higgins-Chen (2022) within the prespecified tolerances — a near-exact **same-cohort**
reproduction. The only excursions are two clocks' median absolute replicate difference landing
~0.03 yr outside a *coarse published range* for the non-highlighted clocks. **20 / 22 checks pass.**

Protocol (locked before this run): `TIER3_PROTOCOL.md`. Inputs: frozen M1 outputs at tag
`v0.3.1-scientific-baseline`. reliage-side numbers: `datasets/GSE55763/out_tier3/reliage_absdiff.csv`.

## Why same-cohort matters
GSE55763 is the Lehne 2015 technical-replicate data Higgins-Chen used. This is therefore a
reproduction on the *same* replicate cohort, so both the absolute replicate-difference statistics
(median/max \|Δ\|, spread-independent) **and** raw ICC (same between-subject spread) are directly
comparable — the strongest form of reference agreement.

## Primary — median / max absolute replicate difference (original clocks), years

| Clock | reliage median | published median | reliage max | published max | tol median ±0.5 / max ±1.5 |
|---|---|---|---|---|---|
| Horvath1 | **2.076** | 2.1 | **5.452** | 5.4 | ✅ / ✅ |
| GrimAge | **0.929** | 0.9 | **2.411** | 2.4 | ✅ / ✅ |

Both clocks with a *specific* published value reproduce to within **≤ 0.05 yr** on median and max.
These are the confirmable anchors (`REF-HC2022-ABSDIFF`, statistic RESOLVED).

## Secondary — "others" (Hannum, PhenoAge) vs the coarse published ranges

| Clock | reliage median | median range [0.9, 2.4] | reliage max | max range [4.5, 8.6] |
|---|---|---|---|---|
| Hannum | 0.870 | ❌ under by 0.03 | 4.562 | ✅ |
| PhenoAge | 2.429 | ❌ over by 0.029 | 8.582 | ✅ |

The two median misses are **~0.03 yr** outside a range the paper gives as an approximate span for
the non-highlighted clocks — well below any meaningful measurement threshold. Hannum is marginally
*more* reliable than the range floor; PhenoAge marginally noisier than the ceiling. Likely cause:
minor preprocessing/normalization or replicate-subset differences vs the source pipeline; there is
no specific published Hannum/PhenoAge value to miss.

## Secondary — ICC (same-cohort, directly comparable)

| Check | reliage | published | tol | verdict |
|---|---|---|---|---|
| Horvath1 orig raw ICC | 0.945 | 0.945 | ±0.02 | ✅ (exact) |
| Horvath1 orig accel ICC | 0.817 | 0.817 | ±0.03 | ✅ (exact) |
| PC raw ICC (Horvath1/Hannum/PhenoAge/GrimAge) | 0.990 / 0.996 / 0.996 / 0.998 | > 0.99 | ≥ 0.985 | ✅ ×4 |
| PC accel ICC | 0.972 / 0.986 / 0.988 / 0.988 | ~0.97 | 0.97 ± 0.03 | ✅ ×4 |
| PC \|Δ\| fraction ≤ 1.5 yr | 0.92 / 0.97 / 0.97 / 1.00 | "majority 0–1.5 yr" | ≥ 0.75 | ✅ ×4 |

## Reference-provenance caveat
The absolute-difference anchors are RESOLVED (`REF-HC2022-ABSDIFF`). The ICC anchors
(`REF-HC2022-ICC`) are recorded as **text-extracted, pending exact figure-level confirmation**; the
Horvath1 orig ICC exact match (0.945 / 0.817) is consistent with the extracted values but has not
been re-verified against the source figure/supplement. The primary verdict rests on the RESOLVED
absolute-difference statistics, which do not depend on this caveat.

## Verdict against the locked rule
- **Primary (Horvath1 + GrimAge median/max):** 4 / 4 within tolerance → the PASS condition
  ("all primary + PC-ICC bands") is satisfied.
- **Secondary "others" range checks:** 2 / 4 miss (both medians, by ~0.03 yr) → under the PARTIAL
  clause the strict overall verdict is **PARTIAL**.
- No ICC, ranking, or primary absolute-difference check missed.

Recorded conservatively as **PARTIAL**, with the substantive finding stated plainly: reliage
reproduces every *specific* published figure and ICC band for the GSE55763 cohort within tolerance;
the two excursions are 0.03-yr differences against a coarse summary range, not reproduction failures.

## Disposition
- **CLAIMS #7 → Supported (scoped):** published-reference agreement holds on all specific published
  values and ICC bands (same-cohort); two clocks' median \|Δ\| sit ~0.03 yr outside a coarse
  published range. Not a general/other-dataset claim.
- Per protocol deliverable #5 (PASS/PARTIAL), the **tiered reproduction gate is ratified** into
  `SCORING_DECISION.md`: T1 reproduce published stats ✓ · T2 independent GEO rebuild ✓ · T3
  consistency within tolerances ✓ (primary), with the two noted 0.03-yr range excursions.
- Remaining Tier-3 nicety (not blocking): figure-level confirmation of the ICC anchors.
