# scoring/ — clock scoring → reliage (LOCKED: methylCIPHER primary)

reliage never touches betas; these scripts turn a beta matrix into the versioned
**score table** reliage consumes. Run where R + data live (not the cloud sandbox).

## Primary path (methylCIPHER)
```bash
Rscript score_methylCIPHER.R  betas.csv  pheno.csv  scores_methylCIPHER.csv
python -m reliage.scoring.run_analysis  scores_methylCIPHER.csv  map.csv  --out out/
```
- **Pin provenance first** (edit COMMIT etc. in the R script; fill `PROVENANCE.template.md`).
- Produces `out/leaderboard.csv`, `out/contrasts.csv` (the primary variance-ratio
  endpoint), `out/results.json`, `out/RESULTS.md`.

## Sensitivity path (pyaging, independent check)
Score the overlapping clocks with pyaging, then compare score-for-score against
methylCIPHER: do implementations agree numerically? same reliability ranking? same
variance-ratio verdict? If not — coefficients, preprocessing, missing-CpG handling,
transformations, or units? (Advisory, not a gate; a verdict flip must be explained.)

## Execution order (per SCORING_DECISION.md)
1. Fast path: `pcclocks_example` RData → score → analyze → compare to published refs.
2. Canonical: rebuild the same cohort from GSE55763 GEO files → score → analyze.
3. Claim public reproduction ONLY when GEO result matches fast path within the
   prespecified tolerances in `SCORING_DECISION.md`.
4. Run pyaging sensitivity check.

## The score table contract (long form)
`sample_id, clock_id, variant, score, unit, implementation, repo_url, commit,
r_version, pkg_version, clock_function, imputation` (+ coverage in provenance).
`run_analysis.py` also accepts a wide table (sample_id + one column per clock label,
originals as `<Clock>`, PC as `PC<Clock>`).
