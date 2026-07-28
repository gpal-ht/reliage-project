# MILESTONE 001 — First robustness-qualified scientific result

*The point at which reliage became a real scientific project: when the first
independently reconstructed GSE55763 benchmark produced a robustness-qualified
scientific claim.*

**Date:** 2026-07-24 · **Tag:** `v0.3.1-scientific-baseline` · **Chapter:** Architecture → Implementation → Validation → Real data → Robustness → Technical Report v0.1

---

## Question
Do PC-transformed epigenetic clocks reduce **technical measurement error** versus their
originals on independently rebuilt public replicate data — and is any gain genuine
denoising rather than score compression?

## Artifact
The reproducible workflow, not just the number:
independently reconstructed cohort → locked scorer + provenance → **Versioned Score
Table** → scorer-agnostic **reliage** measurement engine → robustness-qualified claim,
under explicit evidence and claim gates.

Frozen deliverables at this tag:
- `generated/GSE55763/processed/scores.csv` — Versioned Score Table (576 rows)
- `generated/GSE55763/out/RESULTS.md` — primary reliability result
- `generated/GSE55763/out/ROBUSTNESS.md` + `robustness/` — refutation attempts
- `generated/GSE55763/out/figures/` — 5 figures (Fig 3 = signal-vs-noise)
- `generated/GSE55763/metadata/PROVENANCE.md` — commit, versions, coverage, md5
- `docs/PIR03-C2/TECHNICAL_REPORT_v0.1.md`, `PIPELINE.md`

## Dataset
GSE55763 (Lehne 2015), Illumina 450K. **36 individuals × 2 batches = 72 cross-batch
technical replicates**, reconstructed from GEO metadata (0 malformed pairs).

## Result
Four prespecified clock pairs (Horvath1, Hannum, PhenoAge, GrimAge). PC-transformed
clocks showed **87–96% lower within-subject technical variance**; all four
paired-bootstrap CIs excluded the null; unchanged in every leave-one-subject-out
analysis. PC retained **74–85%** of between-subject variance (SPR) with age association
and subject ranking preserved (ρ 0.87–0.96): **selective denoising with modest — not
zero — compression.** Directionally consistent with published Higgins-Chen figures.

## Remaining risks
- Single dataset, single scorer commit, cross-batch 450K only.
- Formal Tier-3 tolerance comparison to published figures not yet run.
- Mechanism limited to selective statistical denoising (no biological claim).
- GrimAge coverage 91% (97 imputed CpGs).
- Generalizability beyond these bounds unestablished.

## Next experiment
**E2 — Implementation sensitivity:** does the conclusion depend on the scoring
implementation? methylCIPHER vs **pyaging**, as a separate experiment with its own
protocol and report — not "one more thing before v1."

---
*Evidence layers established: software (engine verified) · statistical (robustness) ·
scientific (GSE55763). v1.0 freeze withheld pending E2 + reference comparison +
independent rerun.*
