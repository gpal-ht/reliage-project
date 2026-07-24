# Public datasets for the reliage reliability experiment

Registry of the public datasets this benchmark runs on. Download them with
`./download_data.sh` (runs where the data should live — not in an ephemeral
cloud sandbox). Sizes are approximate; methylation matrices are large.

## Technical reliability (same sample measured twice)

| Name | Accession | Source | Array | Replicates | ~Size | License / access |
|---|---|---|---|---|---|---|
| **PC-Clocks example** | — | GitHub `MorganLevineLab/PC-Clocks` | 450K | Lehne replicates, pre-subset | small (MB) | open (repo) — **fastest start** |
| **Lehne 2015 (full)** | GSE55763 | GEO | 450K | 36 duplicate pairs (of 2,711) | large (GB) | public |
| **SATSA** | E-MTAB-7309 | ArrayExpress | — | longitudinal/replicate | large | public |

## Biological reliability (same person, repeat draws over a short interval)

| Name | Accession | Source | Interval | Tissue | ~Size | License / access |
|---|---|---|---|---|---|---|
| **Sleep deprivation** | E-MTAB-4664 | ArrayExpress/BioStudies | ~1 day (normal vs sleep-dep) | blood | med | public — use the **normal-sleep arm** for clean reliability |
| **Sleep-dep companion** | GSE49065 | GEO | within-subject timepoints | blood | med | public |
| **Diurnal (within-day)** | TBD | GEO (behind Koncevičius 2024 / 2025 daily-rhythm papers) | hours | blood | med | public — **accession still to pin**; best scientific fit |

## Layout after download

```
data/
  pcclocks_example/   Example_PCClock_Data.RData          (technical, fast start)
  GSE55763/           series matrix + normalized betas     (technical, full)
  E-MTAB-4664/        processed methylation + sample meta   (biological, ~1 day)
  GSE49065/           ...                                   (biological)
  E-MTAB-7309/        ...                                   (technical, SATSA)
```

## From download → reliage

Raw arrays are not beta matrices in reliage's format yet. Per dataset:
1. Obtain a **beta matrix** (samples × CpGs) + **sample metadata** (which samples
   are replicates of the same subject/person).
2. **Score clocks** — run methylCIPHER (R; gives original *and* PC clocks) or
   ComputAgeBench (Python; originals) on the beta matrix → a `scores` CSV.
3. **Run reliage** on the scores + replicate map → the leaderboard (see
   `examples/input_output_walkthrough.py` for the exact shapes).

The replicate map is built with `reliage.replicate_groups_from_metadata(meta,
subject_col=...)`; for E-MTAB-4664, restrict to the normal-sleep timepoints for a
clean reliability ICC (the sleep-dep arm measures *responsiveness*, not reliability).
