# Versioned Score Table (VST) — design notes (NOT yet a spec)

Status: **design note / deferred.** Decision (2026-07-24): do **not** build the VST
spec yet — finish the science first (age-acceleration ICC, Tier-3 reproduction,
pyaging sensitivity), then design the standard once a **second scorer (pyaging)** and a
**second dataset (SATSA)** can stress-test the schema. Designing an interchange format
from a single producer + single dataset is the premature-standardization trap.

The ambition: VST becomes to measurement-science what a **BAM file** is to genomics or an
**AnnData** object to single-cell — a standard exchange format that multiple scoring engines
*produce* and multiple reliability/measurement tools *consume*. reliage stays scorer-agnostic;
VST is the interface.

## What the canonical `scores.csv` already is (v0.1 instance)
Long-form, one row per (sample × clock × variant), with per-row provenance:
`sample_id, clock_id, variant, score, unit, implementation, repo_url, commit, r_version,
pkg_version, clock_function, imputation`. Demographics are already separate (in `pheno.csv`),
not in the score table. The **wide** `scores_wide.csv` is a generated convenience view only.

## Decisions recorded
1. **Canonical form = long**, not wide. Wide is a derived view (scales poorly: 40–60+ clocks).
2. **Provenance model = normalized `run_id` header (BAM `@RG`/`@PG` model).** A metadata header
   defines each *scorer run* once (implementation + commit + versions + imputation + per-clock
   coverage), keyed by `run_id`; each measurement row carries a `run_id` foreign key rather than
   repeating strings. Resolves the "provenance per measurement" vs "separate metadata block"
   tension and makes multi-scorer tables (methylCIPHER + pyaging in one table) trivial.
3. **Keep DRAFT/unfrozen** until second scorer + second dataset exercise it. Validator + freeze
   come at v1.0, not before.

## Proposed VST v0.1 file set (to build later)
```
metadata.yaml   # table_version, table_uuid, spec_version, created, experiment_id, dataset,
                #   source{url, md5}, manifest_version,
                #   scorer_runs: [{run_id, implementation, repo_url, commit, r_version,
                #                  pkg_version, imputation, coverage:{clock: pct}}]
subjects.csv    # subject_id, age, sex
samples.csv     # sample_id, subject_id, batch, measurement_design
scores.csv      # subject_id, sample_id, clock, variant, score, unit, run_id  (FK -> scorer_runs)
```

## Gaps this closes vs the current v0.1 instance
| Field / artifact | Status now | VST v0.1 |
|---|---|---|
| one row = one measurement | ✅ | keep |
| per-row provenance | ✅ (denormalized) | normalize via `run_id` |
| demographics separated | ✅ (`pheno.csv`) | `subjects.csv` |
| **table_version / table_uuid** | ❌ | **add** (self-identifying artifact; RESULTS cites "VST v1.0") |
| **experiment_id / dataset** | ❌ (implicit in path) | **add** |
| **measurement_design** | ❌ | **add** (`technical_replicate` now; future: longitudinal, biological, intervention) |
| **coverage in-band** | ❌ (only in `PROVENANCE.md`) | **add** to `scorer_runs` header |
| **machine-readable metadata** | ❌ (`PROVENANCE.md` is prose) | **add** `metadata.yaml` |

## Evolution roadmap
- **v0.1 (now):** long-form `scores.csv` + prose `PROVENANCE.md` + `pheno.csv` — this experiment.
- **v1.0 (after pyaging + 2nd dataset):** `metadata.yaml` + `subjects.csv` + `samples.csv` +
  `scores.csv` with `run_id`. Marked stable once two producers agree.
- **v2+:** `scores.parquet`, formal schema + validator, VST specification document.
