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

## Sensitivity path (pyaging, independent check) — RUN in Experiment E2
```bash
# pyaging needs Python <3.14 → isolated env (see HANDOVER_v0.3.1 §12); betas.csv is the same file.
<py3.13-env>/python  score_pyaging.py  betas.csv  pheno.csv  scores_pyaging.csv
python -m reliage.scoring.run_analysis  scores_pyaging.csv  map.csv  --out out_E2/
```
E2 result: **implementation-robust** — pyaging reproduces methylCIPHER (per-sample scores
r ≥ 0.9997, same verdict), one benign GrimAge calibration offset. Full comparison:
`docs/PIR03-C2/IMPLEMENTATION_COMPARISON.md`. (Advisory sensitivity check, not a gate; a verdict
flip must be explained. Clock-definition matching is the hard part — e.g. pyaging `dnamphenoage`,
not `phenoage`; GrimAge reads age/female as features.)

## Status (canonical: `docs/tracker.md`, `docs/PIR03-C2/CLAIMS.md`)
- **M1 done** — GSE55763 GEO cohort (36 replicate pairs) scored with pinned methylCIPHER →
  supported 4/4. **The author-prepared "fast path" (Box `Example_PCClock_Data.RData`) is
  UNAVAILABLE (removed); M1 used the GEO canonical path directly.**
- **E2 done** — pyaging sensitivity check → implementation-robust.
- **Pending** — formal Tier-3 published-reference comparison. The fast-path↔GEO tolerance gate in
  `SCORING_DECISION.md` is superseded by a tiered reproduction gate, to be ratified at Tier-3.

## The score table contract (long form)
`sample_id, clock_id, variant, score, unit, implementation, repo_url, commit,
r_version, pkg_version, clock_function, imputation` (+ coverage in provenance).
`run_analysis.py` also accepts a wide table (sample_id + one column per clock label,
originals as `<Clock>`, PC as `PC<Clock>`).
