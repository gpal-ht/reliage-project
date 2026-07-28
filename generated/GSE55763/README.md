# GSE55763 — Lehne et al. 2015 (technical replicates, Tier 1 anchor)

**Role:** the canonical public technical-reliability dataset (Milestone 3, full
public reproduction). Illumina HumanMethylation450. GEO record: 2,664 individuals
plus **36 samples measured in duplicate**, the two measurements deliberately
processed in **separate batches** (a useful technical-noise stress test).

## Download source
GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE55763
- Supplementary dir: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/suppl/`
- or `python -c "import GEOparse; GEOparse.get_GEO('GSE55763', destdir='raw')"`
(Run where the data will live — several GB. See `../../data/download_data.sh gse55763`.)

## Layout
- `raw/` — series matrix + supplementary normalized-beta files as downloaded.
- `processed/` — subset beta matrix for the 72 replicate samples + scores.csv.
- `metadata/` — replicate map, DATA_PROVENANCE.md, preprocessing record.

## Preprocessing requirements
Obtain normalized betas; subset to the 72 replicate samples; record normalization/
pipeline exactly.

## Replicate mapping requirements
Build `subject → [measurement_1, measurement_2]` for the 36 pairs. **Executable audit
(VAL-DATA-AUDIT-GSE55763):** verify unique biological samples, assay measurements,
complete pairs, and exclusions — establish "36 samples measured in duplicate" from
data, not prose.

## Known issues
- Cross-batch by design → estimates reliability under that specific setup.
- Large download; only 72 of ~2,700 samples are needed for reliability.
- 450K platform only (no EPIC); n=36 pairs → wide ICC CIs.
