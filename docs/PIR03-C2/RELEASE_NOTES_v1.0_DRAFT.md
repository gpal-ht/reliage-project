# reliage v1.0.0 — Release Notes (DRAFT)

> 🚧 **DRAFT — do not publish yet.** This release is gated on **CLAIMS #8 (independent
> third-party reproducibility)**, which is still Pending. Finalize per the checklist at the bottom
> once an external reproduction report is merged. Fields marked `<…>` are filled from that report.

**reliage v1.0.0** — the first stable release of an open, reproducible **measurement-science layer
for epigenetic clocks**. v1 scope: **technical reliability**. Release date: `<YYYY-MM-DD>`.

---

## Highlights

- A **scorer-agnostic reliability benchmark**: given a score table + replicate map, reliage reports
  ICC (with F-CIs and Koo–Li bands), within-subject SD / SEM / MDC95, the PC-vs-original
  within-subject **variance ratio** (primary endpoint) with paired-bootstrap CIs, an
  age-acceleration companion, a detectability screen, and a robustness suite.
- A first, **robustness-qualified scientific result** on independently rebuilt public data.
- The **Versioned Score Table** — a validated exchange *contract* between biomarker scoring and
  measurement science, exercised by two independent producers.
- v1 protocol **frozen** (`PROTOCOL_FREEZE.md`); public CI green; full reproduction package.

## The scientific result (calibrated, scoped)

On **GSE55763** (36 cross-batch technical-replicate pairs, Illumina 450K), for four prespecified
clock pairs (Horvath1, Hannum, PhenoAge, GrimAge × original/PC):

> PC-transformed clocks reduce within-subject **technical** measurement variance by **87–96%**
> versus their originals (point estimates; CI-bounded worst case ~67% for Hannum); all four
> paired-bootstrap CIs exclude the null; the effect survives leave-one-subject-out and is
> **selective denoising** (between-subject signal retained 74–85%), not range compression.

This is a **technical-reliability** finding on one 450K cross-batch cohort and these four clock
families. It is **not** a claim about biological reliability, other datasets/platforms, or other
clocks (see Scope).

## Evidence base (5 dimensions — the release requirement)

| Dimension | Status | Evidence |
|---|---|---|
| Software correctness | ✅ | ICC vs Shrout–Fleiss; 4-gate self-check; public CI (py3.10–3.13) |
| Statistical robustness | ✅ | compression audit, leave-one-subject-out, Bland–Altman, outliers (M1) |
| Implementation robustness | ✅ | E2: methylCIPHER vs pyaging — scores r ≥ 0.9997, same verdict |
| Published-reference agreement | ✅ (scoped) | Tier-3 same-cohort reproduction of Higgins-Chen 2022 (median/max \|Δ\| + ICC bands) |
| **Independent reproducibility** | **✅** | `<reproducer / affiliation>` reproduced Core from a clean clone, `<date>` — report: `<link>` |

Full ledger: `CLAIMS.md`. **v1.0 ships only when all five are met** (the fifth is what this release adds).

## What's in this release

- **Engine** (`reliage/`): `icc`, `benchmark`, `contrast`, `detectability`, `selfcheck` (numpy/pandas/scipy only).
- **Scoring producers** (`reliage/scoring/`): `score_methylCIPHER.R` (primary), `score_pyaging.py`
  (sensitivity), `run_analysis`, `age_accel_icc`, `robustness`, `icc_sensitivity`, `tier3_compare`, `figures`.
- **Dataset build** (`generated/GSE55763/build/`): metadata reconstruction + column extraction.
- **Frozen artifacts**: M1 results + figures, E2 comparison, Tier-3 comparison, provenance.
- **Docs**: `HANDOVER_v0.3.1.md`, `PIPELINE.md`, `PROTOCOL_FREEZE.md`, `FOUNDRY_PRINCIPLES.md`,
  `REPRODUCTION_PACKAGE.md`, `CLAIMS.md`, and the milestone/experiment records.

## Stability commitments (what v1.0 promises)

- **Frozen v1 protocol** (`PROTOCOL_FREEZE.md`): clock set (GrimAge V1), variance-ratio primary
  endpoint (bootstrap seed 0 / 2000), ICC(2,1) primary + 1,1/3,1 sensitivity, robustness suite,
  methylCIPHER `@9e8c1e5` pin, ratified tiered reproduction gate. Changes only via dated amendment.
- **Versioned Score Table contract** (long-form schema) is stable; any scorer emitting it runs the
  pipeline unchanged. The *normalized* VST spec remains a v1.x/v2 item.
- Semantic versioning from here; breaking changes to the engine API or the VST schema require a major bump.

## Scope & limitations (honest bounds)

- **Technical reliability only** (Tier A). Biological/longitudinal/responsiveness reliability are
  out of v1.
- **One dataset / one platform / one design**: GSE55763, 450K, cross-batch technical replicates.
  Generalization to other datasets, EPIC, or other clock families is untested (CLAIMS #9–#12: Unknown).
- **GrimAge coverage 91%** (97 imputed CpGs) on this cohort — the lowest of the five; interpret
  GrimAge/PCGrimAge accordingly.
- **PC-clock cross-implementation independence is partial** (methylCIPHER and pyaging PC clocks
  likely share the published Higgins-Chen coefficients); the original clocks carry the
  implementation-robustness weight.
- **Tier-3 is same-cohort** and scoped: two clocks' median \|Δ\| sit ~0.03 yr outside a coarse
  published range; the ICC anchors are text-extracted (figure-level confirmation is a follow-up).

## Provenance (reproduce exactly)

methylCIPHER `@9e8c1e55f53c3fdeaf32a38cc8ef109be8b2a8c8` · R 4.6.1 · GrimAge V1 · pyaging 0.3.1 ·
PC reference Zenodo `10.5281/zenodo.19455622` · GSE55763 gz md5 `64654afe3a8898641c3e321c5a5204df`.
Reproduce via `docs/PIR03-C2/REPRODUCTION_PACKAGE.md` (the package the independent reproduction used).

## Upgrade notes (from `v0.3.1-scientific-baseline`)

- No breaking API changes; v1.0 adds E2 (pyaging scorer), Tier-3, ICC sensitivity, public CI, the
  reproduction package, and the frozen protocol. The M1 baseline tag remains for historical reference.

## How to cite

`reliage v1.0.0 — open technical-reliability benchmark for epigenetic clocks. <authors>, 2026.
github.com/gpal-ht/reliage-project (tag v1.0.0).` Underlying reliability finding: Higgins-Chen et al.,
Nature Aging 2022. Data: GSE55763 (Lehne et al. 2015).

## Acknowledgments
methylCIPHER (Higgins-Chen Lab), pyaging (rsinghlab), the PC-clocks authors, and the independent
reproducer(s): `<names>`.

---

## FINALIZE-ON-#8 checklist (mechanical)
1. Merge the external reproduction report; set **CLAIMS #8 → Supported** with reproducer/date/link.
2. Fill every `<…>` above from the report; remove the DRAFT banner; set the release date.
3. Bump `pyproject.toml` version `0.1.0` → `1.0.0` (fix the stale description: drop "companion to
   ComputAgeBench").
4. Verify public CI is green on the release commit.
5. `git tag -a v1.0.0 -m "reliage v1.0.0 — stable technical-reliability benchmark (all 5 evidence
   dimensions met)"` and push the tag.
6. Update `tracker.md` Status → "v1.0.0 released"; rename this file to `RELEASE_NOTES_v1.0.md`.
7. (Optional) create a GitHub Release from the tag with these notes.
