# CLAIMS — reliage scientific state

One page. The current scientific knowledge of the project: what is claimed, on what
evidence, at what confidence. Everything else (reports, postmortems, milestones, figures)
*supports* this ledger. Updated as evidence changes.

**Last updated:** 2026-07-25 · after Experiment E2.

## Evidence ledger

| # | Claim | Evidence | Status / Confidence | Updated |
|---|---|---|---|---|
| 1 | ICC engine is correct | Shrout–Fleiss canonical validation; 4-gate self-check | ✅ Supported · High | 2026-07-24 |
| 2 | Variance-ratio + bootstrap implementation is correct | Synthetic recovery validation | ✅ Supported · High | 2026-07-24 |
| 3 | PC clocks reduce technical measurement variance on GSE55763 | M1 (4/4 pairs, all bootstrap CIs < 1) | ✅ Supported · High | 2026-07-24 |
| 4 | The effect survives adversarial robustness checks | M1: compression audit, leave-one-subject-out, Bland–Altman, outliers | ✅ Supported · High | 2026-07-24 |
| 5 | The gain is selective denoising, not range compression | M1 compression audit (noise −87–96% vs signal retained 74–85%) | ✅ Supported · High | 2026-07-24 |
| 6 | The reliability conclusion is robust to the scoring implementation | E2 (methylCIPHER vs pyaging; r ≥ 0.9997, ICC/VR ordering ρ = 1.0, same verdict) | ✅ Supported · High — *scoped: correctly-matched clocks, GSE55763* | 2026-07-25 |
| 7 | Results match published (Higgins-Chen) references within *formal* tolerances | Tier-3 (same-cohort GSE55763): Horvath1 2.08/5.45 vs 2.1/5.4, GrimAge 0.93/2.41 vs 0.9/2.4 yr; Horvath1 ICC 0.945/0.817 exact; PC ICC bands all met (20/22 checks) | ✅ Supported · High — *scoped: specific published values + ICC bands met near-exactly; 2 clocks' median \|Δ\| ~0.03 yr outside a coarse range (strict rule: PARTIAL)* | 2026-07-25 |
| 8 | Results are independently reproducible by a third party | Reproduction package + report template ready (`REPRODUCTION_PACKAGE.md`, `REPRODUCTION_REPORT_TEMPLATE.md`); awaiting an independent party's run | ⏳ Pending — *package ready, external execution needed* | 2026-07-25 |
| 9 | Generalizes to other datasets | — | ❔ Unknown (not tested) | — |
| 10 | Generalizes to EPIC arrays (vs 450K) | — | ❔ Unknown (not tested) | — |
| 11 | Generalizes to biological (not just technical) reliability | — | ❔ Unknown (v2 scope) | — |
| 12 | Generalizes across clock families beyond these four | — | ❔ Unknown (not tested) | — |

## Scope of the strongest claims (3–6)
GSE55763 · 36 cross-batch technical-replicate pairs · Illumina 450K · four prespecified clock
families (Horvath1, Hannum, PhenoAge, GrimAge V1) × (original, PC). Claim 6's independence is
strongest for the **original** clocks (independently coded from public coefficients, agree
r ≈ 1.0); PC-clock agreement is partly a shared upstream (Higgins-Chen coefficients).

## Evidence dimensions (coverage map)

Confidence accumulates along **orthogonal** axes, not a linear experiment sequence. The project
progresses by *filling cells*, not advancing a timeline:

| Evidence dimension | Status | Established by |
|---|---|---|
| Software correctness | ✅ | canonical (Shrout–Fleiss) validation, self-check |
| Statistical robustness | ✅ | M1 refutation suite (compression / LOSO / Bland–Altman / outliers) |
| Implementation robustness | ✅ | E2 (methylCIPHER vs pyaging) |
| Published-reference agreement | ✅ (scoped) | Tier-3 same-cohort reproduction — specific published figures + ICC bands met (claim #7) |
| Independent reproducibility | ⏳ (package ready) | `REPRODUCTION_PACKAGE.md` drafted; awaiting an external party's run → moves claim #8 |

Each dimension is separately strengthenable; the gaps are explicit. A "release decision" is a
function of this coverage, not of an experiment count.

## What is NOT claimed
- No claim beyond this dataset, platform, replicate design, or these clocks.
- No biological / longitudinal / responsiveness claim (Tiers B–D, out of v1 scope).
- No "the two scorers are identical" claim — they differ by a benign GrimAge calibration offset.
- No v1.0 / public-release claim until #7 and #8 are resolved.

## Methodology
The principles that produced this evidence are now canonical in
[`../FOUNDRY_PRINCIPLES.md`](../FOUNDRY_PRINCIPLES.md) — lock protocols before results (P1);
disprove before strengthening (P2); match by biological definition, not name (P3); separate
software/statistical/scientific evidence (P4); preserve immutable milestone snapshots (P5);
record remaining uncertainties (P6). This ledger *is* the living scientific state; each future
experiment updates a row rather than restating the whole.
