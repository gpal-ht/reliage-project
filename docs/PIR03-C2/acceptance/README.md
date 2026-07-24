# PIR03-C2 acceptance specification

The single `acceptance_cases.yaml` is **superseded** by three files, because it
mixed four different things that must stay separate (a scientifically correct tool
could otherwise "fail" merely because a small external dataset didn't hit a chosen
threshold):

| File | Question | Gate / disposition |
|---|---|---|
| `validation_cases.yaml` | Does reliage compute correctly? (ICC, CIs, SEM, MDC95, pairing, units, determinism, data audit) | **Tool-validation gate — must pass.** Deterministic right answers. |
| `published_reference_cases.yaml` | What exactly did the source papers report, and under what conditions is it reproducible? | Reference anchors; reproducible **only** under source dataset/clocks/preprocessing. |
| `replication_hypotheses.yaml` | Does the published pattern recur on independent public data? | **Scientific-replication verdict** — supported / directionally / partially / not / inconclusive. Never pass-only. |

## Two independent gates

- **Tool-validation** failing ⇒ reliage is not validated (blocking).
- **Scientific-replication** returning "not supported" ⇒ a *valid scientific
  finding*, possibly from a completely correct reliage run. Not a tool failure.

Never write "Tier A must pass to claim capabilities" — that converts replication
into confirmation.

## Key framing decisions (from review)

- **Milestone name:** "Open **external replication** of the PC-clock technical-
  reliability advantage on GSE55763." Reserve "exact reproduction" for
  same-data/same-method/same-numbers (only after confirming Higgins-Chen computed
  the cited figures from this same Lehne subset under the same preprocessing).
- **Primary endpoint:** `within_subject_variance_ratio = var_within(PC)/var_within(original)`,
  reported alongside ICC — tests the PC mechanism directly, less spread-dependent.
- **Four-tier taxonomy:** A technical | B short-interval-stable | C longitudinal |
  D acute-responsiveness. SATSA (E-MTAB-7309) is **Tier C (longitudinal)**, not a
  clean technical/biological set. E-MTAB-4664 normal arm ≈ Tier B (caveated),
  sleep-dep arm = Tier D.
- **Resolved statistic:** the published "3–9 years / 0–1.5 years" figures are
  **median & maximum absolute replicate difference**, NOT within-subject SD (see
  `published_reference_cases.yaml` REF-HC2022-ABSDIFF).
- **Dataset claim softened:** "we have currently verified two relevant public
  datasets," not "only two are cleanly public" (no exhaustiveness claim).
- **CI-aware banding:** report the point-estimate band *and* the CI-compatible band
  range; never a lone colored chip.
