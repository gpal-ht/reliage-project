# datasets/ — public data for validating reliage

Scaffold + per-dataset instructions. **The bytes are downloaded where the data will
live** (your machine / repo), not in the ephemeral cloud sandbox — see
`../data/download_data.sh` and `../data/DATASETS.md`. Each dataset dir has
`raw/ processed/ metadata/` + a README with source, preprocessing, replicate mapping,
and known issues.

| Dir | Accession | Tier | Role |
|---|---|---|---|
| `GSE55763/` | GSE55763 | 1 | canonical technical-replicate anchor (GEO rebuild) |

Tier 2/3 (biological/longitudinal — future milestones): E-MTAB-4664 (Tier D + normal
arm), GSE49065, SATSA/E-MTAB-7309 (Tier C longitudinal), diurnal set (accession TBD).
Added as their milestones open; see `../Contributions`… `acceptance/replication_hypotheses.yaml` tiers.
