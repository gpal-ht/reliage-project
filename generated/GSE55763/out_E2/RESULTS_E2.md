# reliage benchmark report
- clocks: 8 | pairs evaluated: 4
- joint primary verdict (PC reduces technical error): **supported** (4/4 pairs improve)

## Reliability leaderboard
| Clock | ICC | 95% CI | Within-subject SD | Mean abs diff | Individual MDC95 | Reliability | n | k |
|---|---|---|---|---|---|---|---|---|
| PCGrimAge | 0.998 | (0.995, 0.999) | 0.32 | 0.38 | 0.89 | excellent | 36 | 2 |
| PCPhenoAge | 0.996 | (0.993, 0.998) | 0.53 | 0.61 | 1.46 | excellent | 36 | 2 |
| PCHannum | 0.996 | (0.991, 0.998) | 0.48 | 0.51 | 1.33 | excellent | 36 | 2 |
| PCHorvath1 | 0.990 | (0.981, 0.995) | 0.71 | 0.75 | 1.97 | excellent | 36 | 2 |
| GrimAge | 0.989 | (0.979, 0.994) | 0.90 | 1.01 | 2.49 | excellent | 36 | 2 |
| Hannum | 0.978 | (0.958, 0.989) | 1.31 | 1.36 | 3.62 | excellent | 36 | 2 |
| Horvath1 | 0.945 | (0.894, 0.971) | 1.94 | 2.31 | 5.39 | excellent | 36 | 2 |
| PhenoAge | 0.917 | (0.844, 0.957) | 2.79 | 3.21 | 7.75 | excellent | 36 | 2 |

## Primary endpoint — variance ratio (PC/original), paired bootstrap CI
original transformed  variance_ratio   ci_low  ci_high   verdict  n_subjects
Horvath1  PCHorvath1        0.133328 0.065137 0.259176 supported          36
  Hannum    PCHannum        0.134840 0.057969 0.329026 supported          36
PhenoAge  PCPhenoAge        0.035515 0.020707 0.059942 supported          36
 GrimAge   PCGrimAge        0.128363 0.074533 0.220327 supported          36

## Detectability screen — effect 1.0
Not ruled out by measurement noise for: PCGrimAge (effect 1.0)

## Detectability screen — effect 2.0
Not ruled out by measurement noise for: PCGrimAge, PCHannum, PCPhenoAge, PCHorvath1 (effect 2.0)

## Detectability screen — effect 5.0
Not ruled out by measurement noise for: PCGrimAge, PCHannum, PCPhenoAge, PCHorvath1, GrimAge, Hannum (effect 5.0)
