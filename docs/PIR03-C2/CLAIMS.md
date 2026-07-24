# CLAIMS — reliage scientific state

One page. The current scientific knowledge of the project: what is claimed, on what
evidence, at what confidence. Everything else (reports, postmortems, milestones, figures)
*supports* this ledger. Updated as evidence changes.

**Last updated:** 2026-07-25 · after Experiment E2.

## Evidence ledger

| # | Claim | Evidence | Status / Confidence |
|---|---|---|---|
| 1 | ICC engine is correct | Shrout–Fleiss canonical validation; 4-gate self-check | ✅ Supported · High |
| 2 | Variance-ratio + bootstrap implementation is correct | Synthetic recovery validation | ✅ Supported · High |
| 3 | PC clocks reduce technical measurement variance on GSE55763 | M1 (4/4 pairs, all bootstrap CIs < 1) | ✅ Supported · High |
| 4 | The effect survives adversarial robustness checks | M1: compression audit, leave-one-subject-out, Bland–Altman, outliers | ✅ Supported · High |
| 5 | The gain is selective denoising, not range compression | M1 compression audit (noise −87–96% vs signal retained 74–85%) | ✅ Supported · High |
| 6 | The reliability conclusion is robust to the scoring implementation | E2 (methylCIPHER vs pyaging; r ≥ 0.9997, ICC/VR ordering ρ = 1.0, same verdict) | ✅ Supported · High — *scoped: correctly-matched clocks, GSE55763* |
| 7 | Results match published (Higgins-Chen) references within *formal* tolerances | Tier-3 comparison | ⏳ Pending |
| 8 | Results are independently reproducible by a third party | External rerun from the repo | ⏳ Pending |
| 9 | Generalizes to other datasets | — | ❔ Unknown (not tested) |
| 10 | Generalizes to EPIC arrays (vs 450K) | — | ❔ Unknown (not tested) |
| 11 | Generalizes to biological (not just technical) reliability | — | ❔ Unknown (v2 scope) |
| 12 | Generalizes across clock families beyond these four | — | ❔ Unknown (not tested) |

## Scope of the strongest claims (3–6)
GSE55763 · 36 cross-batch technical-replicate pairs · Illumina 450K · four prespecified clock
families (Horvath1, Hannum, PhenoAge, GrimAge V1) × (original, PC). Claim 6's independence is
strongest for the **original** clocks (independently coded from public coefficients, agree
r ≈ 1.0); PC-clock agreement is partly a shared upstream (Higgins-Chen coefficients).

## What is NOT claimed
- No claim beyond this dataset, platform, replicate design, or these clocks.
- No biological / longitudinal / responsiveness claim (Tiers B–D, out of v1 scope).
- No "the two scorers are identical" claim — they differ by a benign GrimAge calibration offset.
- No v1.0 / public-release claim until #7 and #8 are resolved.

## Foundry principles earned here (candidates to elevate project-wide)
- **P1 — Believe the result only after trying to disprove it.** (M1: the robustness section is a
  sequence of failed refutations; the claim is what survived.)
- **P2 — Match measurement instruments by definition and required inputs, not by name.**
  Implementation-sensitivity studies are dominated by *definition matching*, not the algorithms.
  (E2: clock *names* lied — clinical vs DNAm PhenoAge; covariates-as-features vs obs.) Applies to
  proteomic, transcriptomic, metabolomic, and imaging biomarkers alike.
