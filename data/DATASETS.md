# Public datasets for the reliage reliability experiment

Registry of the public datasets this benchmark runs on. Download them with
`./download_data.sh` into the **shared external data root** — never into the repo.
Sizes are approximate; methylation matrices are large.

**Data root.** Datasets live under `$LONGEVITY_DATA_ROOT` (a single external location
reused across longevity projects), default `C:\Ambitious Projects\Longevity Project\Datasets`.
Set the env var (or pass `--data-root DIR`) to point elsewhere. Only the small
**generated** summaries (reconstructed metadata, the Versioned Score Table, analysis
outputs) are committed — in the repo's `generated/` folder, not here. See
[`generated/README.md`](../generated/README.md).

## Technical reliability (same sample measured twice)

| Name | Accession | Source | Array | Replicates | ~Size | License / access |
|---|---|---|---|---|---|---|
| **Lehne 2015 (full)** | GSE55763 | GEO | 450K | 36 duplicate pairs (of 2,711) | large (GB) | public — **the v1 anchor** |
| **SATSA** | E-MTAB-7309 | ArrayExpress | — | longitudinal/replicate | large | public |

## Biological reliability (same person, repeat draws over a short interval)

| Name | Accession | Source | Interval | Tissue | ~Size | License / access |
|---|---|---|---|---|---|---|
| **Sleep deprivation** | E-MTAB-4664 | ArrayExpress/BioStudies | ~1 day (normal vs sleep-dep) | blood | med | public — use the **normal-sleep arm** for clean reliability |
| **Sleep-dep companion** | GSE49065 | GEO | within-subject timepoints | blood | med | public |
| **Diurnal (within-day)** | TBD | GEO (behind Koncevičius 2024 / 2025 daily-rhythm papers) | hours | blood | med | public — **accession still to pin**; best scientific fit |

## Layout

Source data (external, shared) vs generated summaries (in the repo):

```
$LONGEVITY_DATA_ROOT/                 (external — the dataset SOURCE, shared across repos)
  GSE55763/raw/       GSE55763_normalized_betas.txt.gz (+ md5), series matrix
  E-MTAB-4664/raw/    processed methylation + sample meta   (biological, ~1 day)
  GSE49065/raw/ ...                                          (biological)
  E-MTAB-7309/raw/ ...                                       (technical, SATSA)

<repo>/generated/                     (in git — GENERATED summaries, not the dataset)
  GSE55763/build/     parse_metadata.py, extract_betas.sh   (the generators)
  GSE55763/metadata/  map.csv, pheno.csv, replicate_sample_ids.txt, PROVENANCE.md
  GSE55763/processed/ scores*.csv (committed) · betas.csv (gitignored, rebuilt)
  GSE55763/out*/      analysis results (committed)
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
