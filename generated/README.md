# generated/ — generated summaries of external datasets

This folder holds the small, committed artifacts that reliage's build + scoring
logic **generates** from a dataset: reconstructed metadata, the Versioned Score
Table, and analysis outputs. **These are not the dataset.**

The raw dataset — the multi-GB source download — lives **outside the repo**, in the
shared data root `$LONGEVITY_DATA_ROOT` (default
`C:\Ambitious Projects\Longevity Project\Datasets`), so it can be referenced from
multiple longevity projects and kept out of git. See `../data/DATASETS.md`.

Per dataset (e.g. `GSE55763/`):

| Subfolder | Contents | Committed? |
|---|---|---|
| `build/` | the generator scripts (parse metadata, extract betas) | yes |
| `metadata/` | generated `map.csv`, `pheno.csv`, `replicate_sample_ids.txt` + authored `PROVENANCE.md` | yes |
| `processed/` | generated `scores*.csv` (Versioned Score Table) | yes |
| `processed/betas.csv` | generated 596 MB beta matrix | **no — gitignored, rebuilt from the external source** |
| `out/`, `out_E2/`, `out_tier3/` | generated analysis results | yes |

The dataset **source** for each lives at `$LONGEVITY_DATA_ROOT/<DATASET>/raw/`
(for GSE55763: the md5-verified `GSE55763_normalized_betas.txt.gz`).

| Dir | Accession | Tier | Role |
|---|---|---|---|
| `GSE55763/` | GSE55763 | 1 | canonical technical-replicate anchor (GEO rebuild) |

Future biological/longitudinal datasets (E-MTAB-4664, GSE49065, SATSA/E-MTAB-7309,
diurnal) get their own `generated/<DATASET>/` folder as their milestones open.
