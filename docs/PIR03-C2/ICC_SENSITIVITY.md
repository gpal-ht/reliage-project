# ICC-form sensitivity (ICC 1,1 / 2,1 / 3,1)

Protocol requires ICC(2,1) as primary with ICC(1,1) and ICC(3,1) reported as sensitivity. This
confirms the M1 reliability conclusion is not an artifact of the ICC form. Computed on the frozen
M1 score table via `reliage.scoring.icc_sensitivity`; values in `generated/GSE55763/out/icc_sensitivity.csv`.

## Result

| Clock | ICC(1,1) | **ICC(2,1)** | ICC(3,1) | band |
|---|---|---|---|---|
| PCGrimAge | 0.998 | 0.998 | 0.998 | excellent |
| PCPhenoAge | 0.996 | 0.996 | 0.996 | excellent |
| PCHannum | 0.996 | 0.996 | 0.996 | excellent |
| PCHorvath1 | 0.990 | 0.990 | 0.990 | excellent |
| GrimAge | 0.989 | 0.989 | 0.989 | excellent |
| Hannum | 0.978 | 0.978 | 0.978 | excellent |
| Horvath1 | 0.945 | 0.945 | 0.943 | excellent |
| PhenoAge | 0.918 | 0.918 | 0.917 | excellent |

**Max spread across forms for any clock: 0.0014.** Under all three forms: every PC clock is
"excellent" (≥ 0.90) and PC > original for all four pairs. The clock ranking is unchanged.

## Interpretation
- **ICC(2,1) ≈ ICC(3,1)** (differences ≤ 0.002). ICC(2,1) is absolute agreement (counts systematic
  between-batch bias as error); ICC(3,1) is consistency (excludes it). Their near-identity means the
  systematic between-batch bias is negligible — consistent with M1's Bland–Altman analysis
  (|bias| ≤ 0.53 yr).
- **ICC(1,1)** (one-way, no occasion term) also matches to ≤ 0.002.
- The **primary endpoint (variance ratio)** is ICC-form-independent by construction (it uses the
  within-subject variance directly), so the scientific verdict was never at risk; this check confirms
  the ICC-based *reliability leaderboard* is equally robust to the form choice.

## Disposition
Strengthens claims #3–#5 (the M1 reliability finding is stable across ICC forms). Not a new claim.
Reproduce: `python -m reliage.scoring.icc_sensitivity generated/GSE55763/processed/scores.csv generated/GSE55763/metadata/map.csv generated/GSE55763/out/icc_sensitivity.csv`.
