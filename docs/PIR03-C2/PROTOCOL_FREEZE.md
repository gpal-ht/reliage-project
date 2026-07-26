# reliage v1 — Protocol Freeze

**Frozen: 2026-07-26.** The v1 analytic protocol is frozen as of this date. The decisions below are
immutable for v1 and may change only via a **dated, versioned protocol amendment** (never a silent
edit). Milestone snapshots remain immutable (FOUNDRY_PRINCIPLES P5).

**The v1.0 release tag is deliberately NOT created here.** Per the release criteria, the `v1.0`
git tag is **held until independent third-party reproducibility (CLAIMS #8) is Supported** — i.e.
until an external party executes `REPRODUCTION_PACKAGE.md` and returns a passing report. This
document freezes the *protocol*; it does not declare the *release*.

## What is frozen (v1)

| Decision | Frozen value | Source of truth |
|---|---|---|
| Scope | technical reliability of epigenetic clocks on public replicate data (Tier A only) | `VISION.md`, `PROTOCOL.md` |
| Clock set | Horvath1, Hannum, PhenoAge, GrimAge × (original, PC); **GrimAge = V1** | `CLOCK_MANIFEST.csv` |
| Primary endpoint | within-subject **variance ratio** (PC/original) + paired bootstrap CI (**seed 0, 2000 iters**) | `reliage.contrast` |
| Reliability index | **ICC(2,1)** primary; ICC(1,1)/(3,1) sensitivity (done — invariant, `ICC_SENSITIVITY.md`); reported **with** absolute error (SEM, MDC95) | `reliage.icc` |
| Companion | age-acceleration ICC | `reliage.scoring.age_accel_icc` |
| Robustness suite | compression audit, leave-one-subject-out, Bland–Altman, outlier audit | `reliage.scoring.robustness` |
| Primary scorer | methylCIPHER **@9e8c1e5** (R 4.6.1) — pinned; pyaging = sensitivity | `SCORING_DECISION.md`, `CLOCK_MANIFEST.csv` |
| Reproduction gate | **tiered (T1 reproduce published stats · T2 independent GEO rebuild · T3 consistency within tolerances)** — ratified | `SCORING_DECISION.md`, `TIER3_PROTOCOL.md` |
| Anchor dataset | GSE55763 — 36 cross-batch technical-replicate pairs (450K) | `datasets/GSE55763/` |
| Versioned Score Table | the **long-form schema** (`sample_id, clock_id, variant, score, unit, + provenance`) is the frozen v1 **contract** | `HANDOVER_v0.3.1.md §8` |

Note: the *normalized* VST spec (metadata.yaml + run_id header + subjects/samples split,
`VST_DESIGN_NOTES.md`) is **not** part of the v1 freeze — the frozen v1 contract is the current
long-form schema, validated by two independent producers (E2). Formalizing the normalized spec is a
v1.x / v2 item.

## Evidence state at freeze (see `CLAIMS.md`)

| Evidence dimension | Status |
|---|---|
| Software correctness | ✅ (+ public CI green, py3.10–3.13) |
| Statistical robustness | ✅ |
| Implementation robustness | ✅ (E2) |
| Published-reference agreement | ✅ scoped (Tier-3, same-cohort) |
| **Independent reproducibility** | **⏳ Pending — the sole gate on the v1.0 tag** |

## Amendment & release process
- **Protocol amendment:** append a dated entry to `PROTOCOL.md` / `SCORING_DECISION.md`; bump the
  freeze date here; never rewrite a frozen decision in place.
- **v1.0 release:** when CLAIMS #8 → Supported (external reproduction report merged), create the
  annotated tag `v1.0`, bump `pyproject.toml` to `1.0.0`, and write release notes referencing this
  freeze + the reproduction report. Until then, `develop`/`master` carry the frozen-protocol code
  and the v1.0 tag does not exist.
