# reliage — Independent Reproduction Report (fill in and return)

Copy this file, complete **every** field, and return it (PR/issue on
`github.com/gpal-ht/reliage-project`). Report what you actually observed — a "did not reproduce"
or "deviated" result is as valuable as a pass. See `REPRODUCTION_PACKAGE.md` for the procedure and
the expected values (§6) with tolerances.

## 0. Reporter & scope
- Reporter (name / affiliation): `__________`   Date: `__________`
- Contact with the original author during this run? **[ ] none** / [ ] some (explain): `__________`
- Repo state used: tag `v0.3.1-scientific-baseline` (commit `61cacf0`)? [ ] yes / [ ] other: `______`
- Targets attempted: [ ] A Core (required)  [ ] B Robustness+Tier-3  [ ] C E2 (pyaging)

## 1. Environment (exact)
- OS / arch: `__________`
- R version: `______`  · methylCIPHER commit: `______________`  · GrimAge variant used: `V1` [ ]
- qs2/stringfish rebuilt from source? [ ] yes [ ] no [ ] n/a
- Python (reliage): `______`  · numpy `____` pandas `____` scipy `____`
- Python (pyaging, if C): `______`  · pyaging version: `______`
- Deliberate version deviations from the pinned set? [ ] no / [ ] yes: `__________`

## 2. Data verification
- `GSE55763_normalized_betas.txt.gz` md5 you computed: `________________________________`
  · matches `64654afe3a8898641c3e321c5a5204df`? [ ] yes [ ] no
- PC reference `PCClocks_data.qs2` obtained from: [ ] Zenodo DOI 10.5281/zenodo.19455622  [ ] other: `____`

## 3. Cohort rebuild (§5.1)
- parse_metadata: replicate samples `___` (expect 72) · individuals `___` (expect 36) · malformed `___` (expect 0)
- `pheno.csv` / `map.csv` identical to committed? [ ] yes (diff empty) [ ] no (attach diff)
- extract_betas: matched columns `___` (expect 72) · CpG rows `_______` (~473,864)

## 4. Scoring (§5.3)
- score rows written: `____` (expect 576) · originals + PC? [ ] yes
- all-NA CpGs dropped: `___` (expect 4) · GrimAge coverage: `___%` (expect ~91) · others `___%` (expect 100)

## 5. Primary endpoint — variance ratio (tolerance ±0.02; verdict must match)
| Pair | expected | your value | within ±0.02? | CI entirely < 1? |
|---|---|---|---|---|
| PhenoAge→PCPhenoAge | 0.036 | `_____` | [ ] | [ ] |
| GrimAge→PCGrimAge | 0.128 | `_____` | [ ] | [ ] |
| Horvath1→PCHorvath1 | 0.133 | `_____` | [ ] | [ ] |
| Hannum→PCHannum | 0.135 | `_____` | [ ] | [ ] |
- Joint primary verdict: `__________` (expect **supported (4/4)**) — matches? [ ] yes [ ] no

## 6. ICC & Tier-3 (tolerance ICC ±0.005; |Δ| ±0.1 yr) — Recommended
- ICC(2,1) spot check: PCGrimAge `_____` (0.998) · Horvath1 `_____` (0.945) · PhenoAge `_____` (0.918)
- Age-accel ICC spot check: PhenoAge orig `_____` (0.756) · PCPhenoAge `_____` (0.988)
- Tier-3 median/max |Δ|: Horvath1 `____/____` (2.08/5.45) · GrimAge `____/____` (0.93/2.41)
- `reliage.selfcheck` 4 gates pass? [ ] yes [ ] no

## 7. E2 — implementation robustness (Extended C)
- methylCIPHER-vs-pyaging per-sample score Pearson r (min across clocks): `_____` (expect ≥ 0.999)
- pyaging joint verdict: `__________` (expect supported 4/4) · GrimAge offset observed: `_____` yr (~−2.63)

## 8. Overall outcome
- **Core (A) reproduced?**  [ ] PASS (shape ok + 4 VRs within ±0.02 + verdict supported 4/4)
  [ ] PARTIAL  [ ] NOT REPRODUCED
- Recommended (B) / Extended (C) outcome: `__________`

## 9. Deviations, friction, and package defects
- Numerical deviations beyond tolerance (which metric, by how much, suspected cause): `__________`
- Steps that were ambiguous, missing, or wrong in the package/PIPELINE: `__________`
- Environment/build problems and how you resolved them: `__________`
- Anything you needed that was NOT in the committed repo: `__________`

## 10. Sign-off
- Summary (1–3 sentences): `__________`
- Attachments: [ ] `out_repro/` CSVs  [ ] console logs  [ ] diffs
- Reporter signature / handle: `__________`
