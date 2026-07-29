# reliage — Independent Reproduction Package (v0.3.1)

For a **third party** to reproduce reliage's results from a clean clone **without contacting the
original author**. Reproducing the core here is the evidence that moves **CLAIMS #8 (independent
reproducibility)** — the last open evidence dimension before a v1.0 discussion.

If anything in this package is ambiguous or blocks you, that is itself a finding: record it in the
report (§8) rather than working around it with private knowledge. Use only the committed repository.

---

## 1. What "reproduced" means (acceptance criteria)

Three targets, in priority order. **Core is required; Extended is recommended.**

| # | Target | Source | Required? |
|---|---|---|---|
| A | **Core — M1 primary result** on GSE55763 (variance ratios + verdict) | M1 | **Required** |
| B | **M1 robustness + Tier-3 reference agreement** | M1 + Tier-3 | Recommended |
| C | **E2 — implementation robustness** (pyaging) | E2 | Recommended |

You **reproduce successfully** (Core) if, from a clean clone and the public raw data, you obtain:
the 4/4 "supported" verdict and per-pair variance ratios within the tolerances in §6. Frozen
reference at git tag `v0.3.1-scientific-baseline` (commit `61cacf0`).

---

## 2. Prerequisites

- **git**, ~40 GB free disk (9.7 GB gz + ~30 GB decompressed transient + outputs), internet.
- **R** 4.6.x + a compiler toolchain (Rtools on Windows; build-essential on Linux/macOS) — needed
  because two R packages must be built from source (§5.2).
- **Python** for reliage's analysis: 3.10–3.14 with `numpy`, `pandas`, `scipy`.
- **(Extended C only)** a **separate** Python 3.9–3.13 environment for pyaging (it does **not**
  support 3.14). `uv` or `conda` recommended to obtain 3.13 without admin.

Use the **pinned versions below** for a strict reproduction; §6 tolerances absorb minor
platform/BLAS differences. If you deliberately use different versions, say so in the report.

Pinned: methylCIPHER **`@9e8c1e55f53c3fdeaf32a38cc8ef109be8b2a8c8`**, R **4.6.1**, GrimAge **V1**;
pyaging **0.3.1**; PC reference `PCClocks_data.qs2` from **Zenodo DOI 10.5281/zenodo.19455622**.

---

## 3. Get the code

```bash
git clone https://github.com/gpal-ht/reliage-project.git
cd reliage-project
git checkout v0.3.1-scientific-baseline    # frozen reference; or 'develop' for latest docs
```
Note: **nothing under `generated/` is in git** — the whole pipeline (reconstructed metadata,
`betas.csv`, the score table, and all results) is regenerated locally from the external source,
which is the point of *independent* reproduction. Compare your regenerated numbers to the
**expected values in §6** (the frozen `v0.3.1-scientific-baseline` tag also retains the original M1
results in git history, under the pre-rename `datasets/GSE55763/` path).

---

## 4. Get the data (public)

- **Methylation betas (9.7 GB):** `GSE55763_normalized_betas.txt.gz` from
  `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/suppl/`.
  **Expected md5: `64654afe3a8898641c3e321c5a5204df`** — verify before proceeding.
- **Series matrix (50,302 bytes, replicate design + phenotype):** `GSE55763_series_matrix.txt.gz`
  from `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/matrix/` (observed md5
  `695e35c77f46fb6b8e34c82a7707258b`; GEO may regenerate the header, so the durable check is that
  `parse_metadata.py` reproduces `map.csv`/`pheno.csv` byte-identically). Both this and the betas gz
  are fetched by `data/download_data.sh gse55763` into `$LONGEVITY_DATA_ROOT/GSE55763/raw/`.
- **PC reference (2 GB):** `PCClocks_data.qs2` — `download_methylCIPHER(clocks="PCClocks",
  source="zenodo")` (needs the R `zen4R` package) or the direct Zenodo file for the DOI above.

Keep the 9.7 GB gz **outside any cloud-synced folder** (see §7).

> **The 9.7 GB gz is a build-time input, and its location is not hardcoded.** It is consumed *only*
> by `extract_betas.sh` (§5.1), which takes its path as a command-line argument (the `<path>` below)
> — put it wherever you like; nothing in the code reads a fixed `Datasets/` path (it appears only in
> `PROVENANCE.md` as a record of where the backup was kept). The gz — plus the series matrix and PC
> reference — is required to regenerate the pipeline, because **nothing under `generated/` is
> committed**: a clone rebuilds the metadata, `betas.csv`, the score table, and the results from the
> external source.

---

## 5. Reproduce — Core (A) and Recommended (B)

### 5.1 Rebuild the cohort (no scoring yet)
```bash
python tools/GSE55763/parse_metadata.py  GSE55763_series_matrix.txt.gz  generated/GSE55763/metadata
#  EXPECT: "replicate samples: 72  groups: [1, 2]  individuals: 36 ... malformed: 0"
bash   tools/GSE55763/extract_betas.sh   generated/GSE55763/metadata/replicate_sample_ids.txt  <path>/GSE55763_normalized_betas.txt.gz  generated/GSE55763/processed/betas.csv
#  EXPECT: "matched 72 beta columns" ; ~473,864 CpG rows, 73 columns
```
Determinism: `parse_metadata.py` is deterministic, so re-running it yields identical
`pheno.csv`/`map.csv`. (The `v0.3.1-scientific-baseline` tag retains a reference copy in git history,
under the pre-rename `datasets/GSE55763/metadata/` path, if you want to diff against it.)

### 5.2 Install & pin the scorer (R)
```r
install.packages("remotes")
remotes::install_github("HigginsChenLab/methylCIPHER@9e8c1e55f53c3fdeaf32a38cc8ef109be8b2a8c8", upgrade="never")
# If qs2/stringfish fail to load (Windows 'LoadLibrary' error), rebuild from source:
install.packages(c("stringfish","qs2"), type="source")
```

### 5.3 Score → Versioned Score Table
```bash
Rscript reliage/scoring/score_methylCIPHER.R  generated/GSE55763/processed/betas.csv \
        generated/GSE55763/metadata/pheno.csv  generated/GSE55763/processed/scores.csv  <path>/PCClocks_data.qs2
#  EXPECT: "wrote 576 score rows ... originals + PC" ; GrimAge coverage ~91%, others 100%; 4 all-NA CpGs dropped
```

### 5.4 Analyze (reliage engine)
```bash
python -m reliage.selfcheck                                   # 4 gates must pass
python -m reliage.scoring.run_analysis   generated/GSE55763/processed/scores.csv  generated/GSE55763/metadata/map.csv  --out out_repro
python -m reliage.scoring.age_accel_icc  generated/GSE55763/processed/scores.csv  generated/GSE55763/metadata/map.csv  generated/GSE55763/metadata/pheno.csv  out_repro/leaderboard_ageaccel.csv
python -m reliage.scoring.robustness     generated/GSE55763/processed/scores.csv  generated/GSE55763/metadata/map.csv  generated/GSE55763/metadata/pheno.csv  out_repro/robustness
python -m reliage.scoring.tier3_compare  out_repro  out_repro/tier3     # Recommended (B)
```
Compare `out_repro/` to the **§6 expected values + tolerances** (the M1 results are not committed;
the `v0.3.1-scientific-baseline` tag retains them in git history).

## 5x. Reproduce — Extended (C, pyaging)
In a **separate Python 3.9–3.13** env: `pip install pyaging`, then
`python score_pyaging.py betas.csv pheno.csv scores_pyaging.csv` (run with `PYTHONUTF8=1`), then
`run_analysis` into `out_E2_repro`. Compare per-sample scores to `scores.csv` (expect r ≥ 0.999) and
the verdict (expect supported 4/4). See §7 for the two pyaging traps.

---

## 6. Expected results + tolerances (objective verification)

Deterministic pipeline (bootstrap `seed=0`); with the pinned versions you should match closely.

**Score table (§5.3):** exactly **576 rows** = 72 samples × 4 clocks × 2 variants. Verdict line
`originals + PC`.

**Primary endpoint — variance ratio (PC/original) [tolerance ±0.02 absolute; verdict must match]:**

| Pair | Expected VR | 95% CI (expect entirely < 1) |
|---|---|---|
| PhenoAge→PCPhenoAge | 0.036 | (0.021, 0.060) |
| GrimAge→PCGrimAge | 0.128 | (0.075, 0.219) |
| Horvath1→PCHorvath1 | 0.133 | (0.065, 0.259) |
| Hannum→PCHannum | 0.135 | (0.058, 0.329) |
| **Joint verdict** | **supported (4/4)** | must reproduce exactly |

**Reliability ICC(2,1) [tolerance ±0.005]:** PCGrimAge 0.998, PCPhenoAge 0.996, PCHannum 0.996,
PCHorvath1 0.990, GrimAge 0.989, Hannum 0.978, Horvath1 0.945, PhenoAge 0.918.

**Age-acceleration ICC [±0.005]:** PC 0.972–0.988; originals PhenoAge 0.756, Horvath1 0.817,
Hannum 0.853, GrimAge 0.959. (SEM and variance ratio must be invariant vs raw.)

**Tier-3 median/max |replicate diff| (yr) [±0.1]:** Horvath1 2.08/5.45, GrimAge 0.93/2.41,
Hannum 0.87/4.56, PhenoAge 2.43/8.58.

**E2 (Extended):** methylCIPHER-vs-pyaging per-sample score Pearson r ≥ 0.999 (7/8 = 1.000);
verdict supported 4/4 in both; a benign GrimAge ~−2.63 yr constant offset (r = 1.0).

**Core PASS =** score table shape correct **and** all four variance ratios within ±0.02 **and**
joint verdict `supported (4/4)`.

---

## 7. Known pitfalls (read before you start — saves days)

- **methylCIPHER API:** the scorer targets methylCIPHER **0.2.0** — `calcGrimAgeV1(DNAm, pheno)`,
  `calcPCClocks(DNAm, pheno, RData)`, pheno columns capitalized `Age`/`Female`. A different
  installed version will not match.
- **all-NA CpGs:** methylCIPHER `check_DNAm` rejects CpGs NA in all samples; the scorer drops them
  (recorded count). Expect 4 dropped.
- **qs2/stringfish** CRAN binaries may fail to load (Windows) — rebuild from source (§5.2).
- **pyaging needs Python < 3.14** — isolated env. Two clock-matching traps: (a) pyaging `phenoage`
  is the **clinical** clock; use **`dnamphenoage`** (513 CpGs); (b) pyaging GrimAge reads
  **Female/Age as the last two feature columns** (`x[:,-2:]`), not `adata.obs` — pass them as columns.
  Run pyaging with `PYTHONUTF8=1` (emoji logging crashes cp1252 consoles).
- **ICC is spread-dependent** — do not compare raw ICC across *different* cohorts; here it is valid
  only because GSE55763 is the same cohort the published figures used.
- **git hygiene:** keep sync clients (OneDrive/Dropbox) and concurrent git GUIs **off** the repo
  folder — they can corrupt `.git`.

Full pitfall list: `docs/HANDOVER_v0.3.1.md §12`. Full pipeline: `docs/PIR03-C2/PIPELINE.md`.
Claims being tested: `docs/PIR03-C2/CLAIMS.md`.

---

## 8. Reproduction report (return this)

Fill in `REPRODUCTION_REPORT_TEMPLATE.md` (copy it, complete every field) and open a PR / issue on
`github.com/gpal-ht/reliage-project`, or send it back. Include: your OS + exact R/Python/package
versions, the md5 you computed, your `out_repro/` numbers vs §6, per-check pass/fail, and any
ambiguity or deviation encountered. A faithful "reproduced within tolerance" report from an
independent party is what upgrades **CLAIMS #8 → Supported**; a "could not reproduce / deviated"
report is an equally valid, recordable outcome.

---

## 9. What independence requires
- Do the run yourself, from the committed repo + public data, without author assistance.
- Do not use `generated/GSE55763/processed/betas.csv` or `scores.csv` if the author sent them — rebuild
  from GEO. (They are gitignored precisely so a clone forces a genuine rebuild.)
- Report what you actually observed, including friction — the goal is truth about reproducibility,
  not a green checkmark.
