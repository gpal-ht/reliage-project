# Score provenance — GSE55763 GEO rebuild (first real-data run)

Run: 2026-07-24. This record is mandatory; no score is valid without it.

## Scorer
- dataset: **GSE55763** (Lehne 2015) — independent GEO rebuild (NOT the Box fast-path; that
  artifact is unavailable/removed)
- scorer: **methylCIPHER (PRIMARY)**
- repository owner + URL: HigginsChenLab / https://github.com/HigginsChenLab/methylCIPHER
- **exact commit hash:** `9e8c1e55f53c3fdeaf32a38cc8ef109be8b2a8c8`
- R version: **4.6.1** (Windows; Rtools45)
- package versions: **methylCIPHER 0.2.0**; key deps: `qs2` 0.2.2 + `stringfish` (both rebuilt
  from source — CRAN binaries failed to load), `DunedinPoAm38`, `prcPhenoAge`, `RcppParallel` 6.0.0
- clocks + functions: Horvath1(`calcHorvath1`), Hannum(`calcHannum`), PhenoAge(`calcPhenoAge`),
  **GrimAge(`calcGrimAgeV1`) — LOCKED to V1 per CLOCK_MANIFEST.csv**, PC via `calcPCClocks`
- PC reference object: **`PCClocks_data.qs2`** — Zenodo DOI `10.5281/zenodo.19455622`
  (open access; no-auth path via `download_methylCIPHER(source="zenodo")`), 2,038 MB

## Data
- source file: `GSE55763_normalized_betas.txt.gz`
  (`https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/suppl/`)
- size: **10,378,167,001 bytes** · **md5 `64654afe3a8898641c3e321c5a5204df`**
- backup retained: `C:\Ambitious Projects\Longevity Project\Datasets\GSE55763_normalized_betas.txt.gz`
- cohort: **72 technical-replicate samples = 36 individuals × 2 batches** (group 1 / group 2),
  identified from the series-matrix `Sample_description`. Every subject has exactly 2 measurements
  (0 malformed). The two measurements were processed in **separate batches by design** (cross-batch
  reliability).

## Preprocessing
- extracted the **72 replicate beta columns** from the full matrix (each sample carries a beta
  column + a paired `Detection Pval` column; only the beta column was kept)
- matrix: 72 samples × **473,864 CpGs**
- dropped **4 CpGs that were NA in all samples** (methylCIPHER `check_DNAm` rejects all-NA probes;
  dropping → treated as missing → imputed). Final: 473,860 CpGs.
- imputation policy: **mean** (methylCIPHER PC-clock default; originals use `imputation=TRUE`)
- normalization: as published by GEO/Lehne 2015 (consumed as normalized betas; reliage is
  scorer-agnostic and does not re-normalize)

## CpG coverage (% present for this dataset — GATE)
| Clock | Present / Total | % |
|---|---|---|
| Horvath1 | 353 / 353 | **100%** |
| Hannum | 71 / 71 | **100%** |
| PhenoAge | 513 / 513 | **100%** |
| GrimAge (V1) | 1042 / 1139 | **91%** (97 CpGs imputed) |
| PC clocks (shared CpG set) | 78,464 / 78,464 | **100%** |

## Output
- transformation + output unit: **years** (all 4 locked pairs; no DunedinPACE/DNAmTL in this run,
  so no cross-unit aggregation)
- GrimAge phenotype inputs used: **age + sex (Female)** from GEO series-matrix metadata
- score table: `datasets/GSE55763/processed/scores.csv` (576 rows = 72 × 4 clocks × 2 variants)

## Notes / known issues
- **GrimAge 91% coverage** (97 imputed CpGs) — above typical gates but the lowest of the five; note
  when interpreting GrimAge/PCGrimAge reliability.
- Result is **raw-age ICC** only; the age-acceleration ICC flavor (Higgins-Chen report both) is not
  yet computed.
- ICC form: ICC(2,1), k=2 (primary). ICC(1,1)/(3,1) sensitivity not yet run.
