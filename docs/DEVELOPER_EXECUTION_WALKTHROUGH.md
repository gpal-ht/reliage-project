# reliage — Developer Execution Walkthrough

> **What this is.** A source-code execution walkthrough for a new maintainer. Not
> API docs, not a code reference — a guided trace of the system *exactly as the
> computer runs it*, from raw GEO files to a recorded scientific verdict. After
> reading this you should be able to trace execution end to end, understand every
> major artifact, debug the known failure modes, and modify the code safely
> without the original author.
>
> **Assumed background:** biology, methylation, epigenetic clocks, ICC, PCA,
> pyaging, methylCIPHER. **Not assumed:** anything about *this repository*.
>
> **Canonical companions** (read when you want the "why" behind a decision):
> [`docs/PIR03-C2/PIPELINE.md`](PIR03-C2/PIPELINE.md) (the run, one page),
> [`docs/PIR03-C2/CLAIMS.md`](PIR03-C2/CLAIMS.md) (the scientific state),
> [`docs/FOUNDRY_PRINCIPLES.md`](FOUNDRY_PRINCIPLES.md) (the methodology).
> Every concrete number in this document is traceable to a file cited inline.

---

## 0 · The one mental model

reliage is **two engines joined by one interface**:

```
  methylation betas ──▶ [ methylCIPHER ] ──▶ Versioned Score Table ──▶ [ reliage ] ──▶ verdict
       (biology)          scoring engine        (the interface)         measurement       (science)
                        betas → scores          scores.csv              scores + design    RESULTS.md
                                                                        → capability
```

- **methylCIPHER** (R) owns clock identity, coefficients, imputation, coverage. It
  is *swappable* — pyaging is the second producer (Experiment E2).
- **reliage** (Python) owns ICC, error bands, variance ratios, detectability. It is
  **scorer-agnostic**: it consumes *only* the score table + a replicate map, and
  **never touches methylation betas or clock formulas**.
- **The Versioned Score Table (`scores.csv`) is the contract.** Everything above it
  is scoring; everything below it is measurement science.

Hold this picture. Every file in the repo sits on one side of that seam.

### Repo map (execution-relevant files)

```
data/download_data.sh                      Stage 1  acquire raw GEO files
tools/GSE55763/parse_metadata.py  Stage 2  reconstruct the 36×2 replicate design
tools/GSE55763/extract_betas.sh   Stage 3  stream out the 72 replicate beta columns
reliage/scoring/score_methylCIPHER.R       Stage 4  PRIMARY scorer  (betas → scores.csv)
reliage/scoring/score_pyaging.py           Stage 4' SECONDARY scorer (E2)  (betas → scores.csv)
   ── Versioned Score Table seam: generated/GSE55763/processed/scores.csv ──
reliage/scoring/run_analysis.py            Stage 6  the reliage entrypoint (scores → RESULTS.md)
   reliage/benchmark.py                             ICC leaderboard
   reliage/icc.py                                   the verified ICC / SEM / MDC95 core
   reliage/contrast.py                              variance-ratio primary endpoint + bootstrap
   reliage/detectability.py                         "reliable enough for WHAT?" screen
reliage/scoring/age_accel_icc.py           Stage 7  age-acceleration ICC companion
reliage/scoring/robustness.py              Stage 8  compression / LOSO / Bland–Altman / outliers
reliage/scoring/figures.py                 Stage 9  the 5 figures
reliage/scoring/icc_sensitivity.py         Stage 6b ICC(1,1)/(3,1) sensitivity
reliage/scoring/tier3_compare.py           Stage 6c published-reference comparison
reliage/datasets.py                        replicate-group builder + GSE55763 loader + synth generator
reliage/selfcheck.py                       4 dependency-light correctness gates
```

The full ordered command sequence is in [§11 Reproduction](#11--full-reproduction-command-sequence).

---

## Stage 1 — Acquire the raw data

**Purpose.** Get the three inputs the run needs, with integrity you can prove
later. reliage rebuilds its cohort from public GEO files — it never trusts an
author-prepared convenience artifact (see the Box→GEO pivot in
[Debugging](#stage-1-debugging)).

**Files involved**
```
data/download_data.sh                         the downloader
generated/GSE55763/metadata/PROVENANCE.md      records source, size, md5
```

**Entry command**
```bash
bash data/download_data.sh gse55763        # or: … all
```

**Execution flow**
```
download_data.sh gse55763
   ↓ dispatch  (case "$1")            data/download_data.sh:74
   ↓
get_gse55763()                        data/download_data.sh:27-37
   ↓ wget -r -np the series suppl dir
   ↓
$DATA_DIR/GSE55763/…/GSE55763_normalized_betas.txt.gz
```

The core command (`data/download_data.sh:31-34`):
```bash
wget -r -np -nH --cut-dirs=6 -R "index.html*" \
  "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/suppl/" \
  -P "$DATA_DIR/GSE55763/" || true
```

**Data in → out**

| Input | Value | Source |
|---|---|---|
| GEO record | `GSE55763` (Lehne et al. 2015, 450K) | `generated/GSE55763/README.md:1` |
| Beta matrix file | `GSE55763_normalized_betas.txt.gz` | `PROVENANCE.md:20` |
| …size | `10,378,167,001 bytes` (~9.7 GB; ~30 GB unzipped) | `PROVENANCE.md:21` |
| …md5 | `64654afe3a8898641c3e321c5a5204df` | `PROVENANCE.md:22` |
| Series matrix | `GSE55763_series_matrix.txt.gz` (~50 KB) | used by Stage 2 |
| PC reference | `PCClocks_data.qs2` (~2 GB), Zenodo `10.5281/zenodo.19455622` | `PROVENANCE.md:16-17` |

> **Why rebuild from GEO?** The public-reproducibility claim is only earned on the
> canonical GEO files, not the author-prepared RData fast path. That is a locked
> protocol rule ([`PROTOCOL.md`](PIR03-C2/PROTOCOL.md) §5).

<a id="stage-1-debugging"></a>**Debugging — Stage 1**

- **Fast-path source is dead.** The Yale Box link for `Example_PCClock_Data.RData`
  was removed. The pipeline pivoted to canonical GSE55763 GEO — which was the
  reproduction target anyway (`docs/PIR03-C2/status_report_0.3.1.md:85-87`).
- **PC reference from Zenodo, not Box.** methylCIPHER's `download_methylCIPHER`
  offers a no-auth Zenodo path (DOI `10.5281/zenodo.19455622`), avoiding the
  auth-gated 2 GB Box object (`status_report_0.3.1.md:88-90`).
- **Corrupt/partial download** is caught downstream by `gzip -t` in Stage 3 and the
  md5 in `PROVENANCE.md` — verify both before trusting a run.

---

## Stage 2 — Reconstruct the replicate design

**Purpose.** GSE55763 contains thousands of samples; only a subset are technical
replicates. This stage identifies **which 72 samples are the 36 duplicate pairs**,
and extracts age + sex — using *only* the ~50 KB series matrix, never the 9.7 GB
betas.

> Total-cohort size is stated two ways in the repo: `README.md:2` = "2,664
> individuals + 36 in duplicate"; `data/DATASETS.md:12` = "36 duplicate pairs (of
> 2,711)". The **72 / 36 / 473,864** figures are internally consistent everywhere;
> only the full-cohort denominator differs. Don't cite a single total as exact.

**Files involved**
```
tools/GSE55763/parse_metadata.py      the reconstructor
generated/GSE55763/metadata/{pheno,map}.csv     outputs
generated/GSE55763/metadata/replicate_sample_ids.txt
```

**Entry command**
```bash
python tools/GSE55763/parse_metadata.py \
       $LONGEVITY_DATA_ROOT/GSE55763/raw/GSE55763_series_matrix.txt.gz  generated/GSE55763/metadata
```

**Execution flow**
```
parse_metadata.py
   ↓ read gzip, keep "!Sample_" lines                     :17-26
   ↓ pull !Sample_title / _geo_accession / _description   :28
   ↓ regex the pairing key on _description                :41,45
   ↓ Sentrix barcode from title                           :38-39
   ↓ sort by (indiv, group); pairing audit                :52,68-69
   ↓ write pheno.csv / map.csv / replicate_sample_ids.txt :56-71
```

**The pairing key** — this single regex is what selects the 72 (`parse_metadata.py:41`):
```python
pat = re.compile(r"Technical replicate group (\d+), sample (\d+)")
# group 1 = batch (1 or 2)  ;  group 2 = subject index
m = pat.search(descs[i])
if not m: continue        # non-replicate samples are skipped here
```
Samples whose `!Sample_description` matches become the cohort; group 1 is the
**batch**, group 2 the **subject**. The Sentrix barcode (e.g. `7786915023_R02C02`)
is pulled from the title by `sentrix()` (`:38-39`, regex `([0-9]{8,}_R\d+C\d+)`) and
becomes the `sample_id` used everywhere downstream.

**Data transformation**
```
series matrix (~2,700 sample records)
        ↓  keep records whose _description matches "Technical replicate group N, sample M"
72 replicate samples  =  36 subjects × 2 batches
        ↓  split, audit, write
pheno.csv (72 rows)  ·  map.csv (72 rows = 36 subject→sample pairs)  ·  replicate_sample_ids.txt (72)
```

**Outputs**

- `pheno.csv` — header `sample_id,age,female,gsm,group,individual,gender`; `group`
  1/2 is the batch, `female` is derived from `gender` M/F → 0/1.
- `map.csv` — header `subject,sample_id`; subject label `indiv_{NN}` (`:65`).
- `replicate_sample_ids.txt` — the 72 Sentrix ids, one per line (the input to Stage 3).

**Pairing audit** (`parse_metadata.py:68-69`) — the correctness gate:
```python
bad = {k: v for k, v in pairs.items() if len(v) != 2}
print(f"subjects: {len(pairs)} | malformed (not exactly 2 measurements): {len(bad)}")
```
Result: **36 subjects, 0 malformed** — every subject has exactly 2 measurements.

**Debugging — Stage 2**

- **"Which samples are the pairs?"** is not stated in the betas file. It is
  reconstructed from series-matrix metadata (`status_report_0.3.1.md:91-93`,
  "36-pair structure rebuilt from metadata"). If the regex ever matches ≠ 72, the
  series-matrix format changed — inspect `!Sample_description` before trusting it.
- **Determinism requirement.** Malformed/incomplete pairs must be handled
  deterministically (documented drop-or-flag, never silent corruption) —
  `validation_cases.yaml:51`. The `bad` audit above is that gate.
- A formal executable audit `VAL-DATA-AUDIT-GSE55763` is still open work
  (`docs/tracker.md:27`); the pairing is verified but not yet a hard test.

---

## Stage 3 — Extract the cohort's betas

**Purpose.** Pull the 72 replicate beta columns out of the multi-GB matrix in a
single streaming pass — no 30 GB in RAM.

**Files involved**
```
tools/GSE55763/extract_betas.sh       streaming extractor
generated/GSE55763/processed/betas.csv          output (596 MB)
```

**Entry command**
```bash
bash tools/GSE55763/extract_betas.sh \
     generated/GSE55763/metadata/replicate_sample_ids.txt \
     /path/to/GSE55763_normalized_betas.txt.gz \
     generated/GSE55763/processed/betas.csv
```

**Execution flow**
```
extract_betas.sh  IDS GZ OUT
   ↓ gzip -t "$GZ"                integrity gate     :12-13
   ↓ zcat "$GZ" | awk … > OUT     streaming extract  :17-29
   │    BEGIN: load wanted IDs into want[]           :18
   │    header: keep col if header ∈ want            :19-26
   │    assert n == 72 beta columns  else exit 3     :23
   │    data rows: print ID_REF + kept cols          :27-28
   ↓ post-check: cols==73 (exit4), rows≥400k (exit5) :31-35
```

The extraction keeps **only beta columns** (it skips the paired `Detection Pval`
columns) by matching each header against the replicate-id set, and hard-asserts the
count (`extract_betas.sh:23`):
```awk
if (n != 72) { print "FATAL: expected 72 beta columns, matched " n > "/dev/stderr"; exit 3 }
```

**Data transformation**
```
GSE55763_normalized_betas.txt.gz   (~30 GB uncompressed, ~2,711 samples × 2 cols each)
        ↓  zcat | awk, keep 72 beta columns matching the replicate ids
betas.csv   473,864 CpGs × 72 samples   (ID_REF + 72 cols = 73 columns; 596 MB)
```

**Assertions** (all in-script): gzip integrity OK · exactly 72 matched columns · 73
output columns · ≥ 400,000 rows. These convert a silent truncated download into a
loud non-zero exit.

**Debugging — Stage 3**

- **`FATAL: expected 72 beta columns, matched N`** → the id list and the matrix
  headers disagree (regenerate `replicate_sample_ids.txt`, or the matrix column
  naming changed).
- **`matrix looks truncated` (exit 5)** → `zcat` stopped early; `set -o pipefail`
  (`:16`) surfaces it. Re-download and re-check md5.
- Rows are **473,864** here; four all-NA CpGs are dropped *later*, in the scorer
  (Stage 4), giving 473,860 — don't expect that drop to happen in this stage.

---

## Stage 4 — Score (the methylCIPHER engine)

**Purpose.** Turn betas into the **8 clock scores per sample** (4 original families ×
{original, PC}) and emit them as the provenance-pinned Versioned Score Table. This
is the primary scorer; it runs *where R + the data live*, not in a cloud sandbox.

**Files involved**
```
reliage/scoring/score_methylCIPHER.R       the PRIMARY scorer  (walked below)
generated/GSE55763/processed/scores.csv     the Versioned Score Table (output)
generated/GSE55763/metadata/PROVENANCE.md   coverage + pins recorded here
```

**Entry command**
```bash
Rscript reliage/scoring/score_methylCIPHER.R \
        generated/GSE55763/processed/betas.csv \
        generated/GSE55763/metadata/pheno.csv \
        generated/GSE55763/processed/scores.csv \
        /path/to/PCClocks_data.qs2
```

**Execution flow (line-by-line)**
```
score_methylCIPHER.R
   ↓ PIN block (repo, commit, imputation, GrimAge V1)   :18-22
   ↓ library(methylCIPHER)                              :24-26
   ↓ read betas / pheno / out / pc_reference args       :28-33
   ↓ orient betas → samples×CpGs (auto-transpose)       :35-37
   ↓ DROP all-NA CpGs, record count                     :39-46
   ↓ build methylCIPHER pheno (Age, Female, aligned)    :49-67
   ↓ coverage = getClockProbes(betas)                   :72-73
   ↓ ORIGINAL clocks: Horvath1/Hannum/PhenoAge/GrimAgeV1 :76-81
   ↓ PC clocks: calcPCClocks(betas, pheno, RData)       :83-87
   ↓ assemble LONG-FORM provenance-pinned rows          :89-111
   ↓ write.csv(rows, outfn)  +  PIN CHECK console line  :112-121
```

**The pins** (mandatory provenance, `score_methylCIPHER.R:18-22`):
```r
REPO_URL   <- "https://github.com/HigginsChenLab/methylCIPHER"
COMMIT     <- "9e8c1e55f53c3fdeaf32a38cc8ef109be8b2a8c8"  # pinned 2026-07-24
IMPUTATION <- "mean (methylCIPHER default: PC clocks mean-impute missing clock CpGs)"
GRIMAGE_VARIANT <- "V1"   # LOCKED: original GrimAge = V1, paired with PCGrimAge
```

**All-NA probe drop** (a genuine gotcha — `score_methylCIPHER.R:39-46`):
```r
# methylCIPHER::check_DNAm REJECTS a probe that is NA in ALL samples (GrimAge/PC),
# whereas partial-NA probes are imputed. Dropping converts an all-NA probe to a
# "missing" probe the clocks impute. Count recorded.
n_all_na <- sum(colSums(is.na(betas)) == nrow(betas))
if (n_all_na > 0) betas <- betas[, colSums(is.na(betas)) < nrow(betas), drop = FALSE]
```
On GSE55763 this drops **4** CpGs (473,864 → 473,860).

**The GrimAge Age/Female requirement** (the most documented gotcha —
`score_methylCIPHER.R:59-62`, `80-81`):
```r
ph <- data.frame(Sample_ID = as.character(pheno_in[[sid_col]]),
                 Age = as.numeric(pheno_in[[age_col]]),
                 Female = as.integer(pheno_in[[female_col]] %in%
                          c(1, "1", TRUE, "TRUE", "F", "female", "Female")))
# …row-aligned 1:1 to betas rows, then:
grim <- calcGrimAgeV1(betas, pheno)    # V1 per manifest → column 'GrimAgeV1'
```
GrimAge/PCGrimAge fold chronological **age** and **sex** into the prediction, so the
pheno frame must carry capitalized `Age` and `Female` (1=female, 0=male), aligned to
the betas. Missing either column is a hard `stop()` (`:55-57`).

**The score rows** (`score_methylCIPHER.R:97-111`) — every row carries its full
provenance via `mk()`. Originals from `calcHorvath1/Hannum/PhenoAge/calcGrimAgeV1`;
PC clocks from the single `calcPCClocks` call returning
`PCHorvath1/PCHannum/PCPhenoAge/PCGrimAge`.

**Data transformation**
```
betas.csv  (473,860 CpGs × 72 samples, after all-NA drop)
        ↓  4 original clock fns + calcPCClocks (mean impute; coverage recorded)
scores.csv  =  72 samples × 4 clocks × 2 variants  =  576 long-form rows
```

**CpG coverage (the gate, from `PROVENANCE.md:40-46`)**

| Clock | present/required | % |
|---|---|---|
| Horvath1 | 353/353 | 100 |
| Hannum | 71/71 | 100 |
| PhenoAge | 513/513 | 100 |
| **GrimAge V1** | **1042/1139** | **91 (97 imputed)** |
| PC clocks | 78,464/78,464 | 100 |

> **Why coverage is a gate, not a warning.** A pair is invalid if the original and
> PC member used different coverage/imputation. GrimAge's 91% is the lowest of the
> five — flag it whenever interpreting GrimAge/PCGrimAge (`PIPELINE.md:172,226`).

**Debugging — Stage 4**

- **Scorer API mismatch (resolved).** An earlier scorer targeted an older
  methylCIPHER API (wrong argument names, lowercase pheno columns). Rewritten
  against 0.2.0: `calcGrimAgeV1(DNAm, pheno)`, `calcPCClocks(DNAm, pheno, RData)`,
  capitalized `Age`/`Female`, row-aligned pheno, plus a PC-failure fallback that
  still emits the originals leaderboard (`status_report_0.3.1.md:81-84`; fallback at
  `score_methylCIPHER.R:84-87,103-111`).
- **GrimAge V2 → V1 (resolved).** The scorer originally called `calcGrimAgeV2`; the
  locked `CLOCK_MANIFEST.csv` pairs original GrimAge as **V1** with PCGrimAge. Pinned
  to V1 (`score_methylCIPHER.R:21,80`). (`PROVENANCE.template.md:12` still shows the
  old V2 placeholder — evidence the choice was genuinely open, not a live default.)
- **`qs2`/`stringfish` DLL-load failure.** These packages (needed to read the PC
  reference `.qs2`) failed to load compiled DLLs; fixed by rebuilding from source
  (`status_report_0.3.1.md:67`).
- **PC clocks fail → originals only.** `calcPCClocks` is wrapped in `tryCatch`; if the
  reference is missing/incompatible it logs and the run still writes the 4 originals
  (the `if (!is.null(pc))` guard at `:103`). The console PIN CHECK line reports
  `ORIGINALS ONLY - PC failed`.

### Stage 4' — The pyaging producer (Experiment E2)

**Purpose.** Prove the Versioned Score Table is a real *contract* by producing it
from a completely different engine (Python/pyaging) and running the *unchanged*
reliage pipeline on it.

**File:** `reliage/scoring/score_pyaging.py` — emits the **identical 12-column
schema** as the R scorer (`score_pyaging.py:76-77`). Two subtleties, both real and
both in-code:

- **Match by biological definition, not name** (`score_pyaging.py:23`):
  ```python
  "dnamphenoage": ("PhenoAge", "original"),   # DNAm Levine (513 CpG), NOT clinical 'phenoage'
  ```
  pyaging ships *both* a `phenoage` (the clinical blood-chemistry composite) and a
  `dnamphenoage` (the DNAm clock). Only the latter matches methylCIPHER's
  `calcPhenoAge`. Choosing by name would silently compare two different biomarkers
  (Foundry Principle P3). *(Note: this is a pyaging clock-mapping subtlety, not a
  broader "clinical PhenoAge bug" — no such story exists elsewhere in the repo.)*
- **GrimAge features live in the matrix, not obs** (`score_pyaging.py:37-42`):
  pyaging's GrimAge reads Female/Age as the **last two feature columns** (`x[:,-2]`,
  `x[:,-1]`), so they must be appended as *columns of the beta matrix* before
  building the AnnData — the mirror image of the R Age/Female gotcha.

E2's documented outcome (`CLAIMS.md:18`): scores `r ≥ 0.9997`, ICC/variance-ratio
ordering `ρ = 1.0`, **same 4/4 verdict**; the two scorers differ only by a benign
GrimAge calibration offset. That is the evidence the VST is a validated contract,
not merely an architectural idea.

---

## Stage 5 — The Versioned Score Table (the contract)

This is the seam of the whole system, so it gets its own chapter.

**What it is.** A long-form CSV — **one row per (sample, clock, variant)** — where
every row carries its own complete provenance. On GSE55763: **576 rows** = 72
samples × 4 clocks × 2 variants. File: `generated/GSE55763/processed/scores.csv`.

**Every column, where it comes from, why it exists**

| Column | Written by | Why it exists |
|---|---|---|
| `sample_id` | Stage 2 (Sentrix id) | joins to the replicate map |
| `clock_id` | scorer | the clock family (`Horvath1`, `Hannum`, `PhenoAge`, `GrimAge`) |
| `variant` | scorer | `original` or `PC` — the paired-contrast axis |
| `score` | clock function | the age estimate |
| `unit` | scorer | `years` here; **never aggregate across units** (DunedinPACE, DNAmTL differ) |
| `implementation` | scorer | `methylCIPHER` or `pyaging` — the E2 axis |
| `repo_url`, `commit` | pin block | exact source of the coefficients |
| `r_version`, `pkg_version` | runtime | environment reproducibility |
| `clock_function` | scorer | e.g. `calcGrimAgeV1`, `calcPCClocks:PCGrimAge` |
| `imputation` | pin block | missing-CpG policy (must match across a pair) |

The schema is defined once in R (`score_methylCIPHER.R:90-96`, the `mk()` helper) and
mirrored exactly in Python (`score_pyaging.py:76-77`).

**Who writes it:** a scorer (Stage 4 / 4'). **Who reads it:**
`run_analysis.load_scores_wide` (Stage 6) and every downstream analysis
(age-acceleration, robustness, ICC-sensitivity, Tier-3). None of them can see a
beta value — the table is the entire interface.

**Long vs wide.** The canonical artifact is *long* (one fact per row, self-describing,
unit- and provenance-tagged). `run_analysis` pivots it to wide in memory
(`load_scores_wide`, `run_analysis.py:36-50`): if it sees `clock_id`+`score` columns
it pivots, prefixing PC variants with `PC` to make column labels like `PCHorvath1`. A
convenience `scores_wide.csv` (72 × 8, with `subject/batch/age/gender`) is also
written for humans.

> **Why long format?** A single "error in years" column is invalid across clocks
> (units differ), and every score must be independently attributable. Long form makes
> the table a durable scientific record, not just a matrix — see
> [`PROTOCOL.md`](PIR03-C2/PROTOCOL.md) §2.

---

## Stage 6 — Reliability analysis (the reliage engine)

**Purpose.** Turn the score table + replicate map into the leaderboard, the primary
endpoint, and the verdict. This is reliage's own entrypoint.

**Files involved**
```
reliage/scoring/run_analysis.py   orchestrator + I/O
reliage/benchmark.py              per-clock ICC leaderboard
reliage/icc.py                    the verified ICC / SEM / MDC95 core
reliage/contrast.py               variance-ratio primary endpoint + bootstrap
reliage/detectability.py          "reliable enough for WHAT?" screen
→ out/{leaderboard.csv, contrasts.csv, results.json, RESULTS.md}
```

**Entry command**
```bash
python -m reliage.scoring.run_analysis \
       generated/GSE55763/processed/scores.csv \
       generated/GSE55763/metadata/map.csv \
       --out generated/GSE55763/out
```

**Execution flow**
```
run_analysis.main()                                     run_analysis.py:121-129
   ↓ run()
   ↓ load_scores_wide(scores.csv)  → wide DF            :36-50
   ↓ load_map(map.csv)  → {subject: [sample_ids]}       :53-59
   ↓ 1. run_reliability_benchmark(...)  → leaderboard   :70   → benchmark.py
   ↓ 2. run_paired_contrasts(...)  → contrasts          :75   → contrast.py
   ↓ 3. recommend_for_effect(...)  → detectability      :84   → detectability.py
   ↓ 4. verdict roll-up  (n_improve == n_pairs ?)       :87-92
   ↓ write leaderboard.csv / contrasts.csv / results.json / RESULTS.md
```

**Important intermediate objects**

- `scores` — wide DataFrame, index = `sample_id`, one column per clock label.
- `groups` — `dict{subject → [sample_id, …]}`, the replicate map in memory.
- `board.frame` — the leaderboard DataFrame (→ `leaderboard.csv`).
- `contrasts` — the paired variance-ratio table (→ `contrasts.csv`).

### 6.1 The leaderboard — `benchmark.py`

`run_reliability_benchmark` loops clocks; for each it builds a balanced matrix and
computes an ICC.

**`build_replicate_matrix`** (`benchmark.py:37-68`) — assemble an `(n_subjects × k)`
matrix for one clock, dropping subjects with fewer than `k` non-missing replicates:
```python
for _subject, sample_ids in replicate_groups.items():
    vals = [scores[s] for s in sample_ids if s in scores.index]
    vals = [v for v in vals if pd.notna(v)]
    if len(vals) >= k:
        rows.append(vals[:k])
```
Row `i` = subject `i`'s `k` replicate scores. On GSE55763 this is `(36, 2)`.

**`compute_icc`** (`icc.py:175-240`) — the verified core. It does a two-way ANOVA
decomposition (`_anova_mean_squares`, `:147-172` → MSR, MSC, MSE, MSW) and forms the
Shrout–Fleiss single-measurement ICC. The default `ICC2` (absolute agreement)
(`icc.py:214-216`):
```python
denom = msr + (k - 1) * mse + (k / n) * (msc - mse)
icc = (msr - mse) / denom
```
It also returns **SEM** = within-subject SD = `sqrt(MSE)` (`:229-230`), and the result
object exposes **MDC95** = `1.96·√2·SEM` (`icc.py:107-113`). CIs are
F-distribution-based (McGraw & Wong 1996, `_icc_confidence_interval`, `:243-286`).

> **Why ICC(2,1)?** Test-retest reliability must ask whether repeat measurements
> *agree in value*, not merely correlate, and treats the measurement occasion (here:
> batch) as a random draw. A clock with systematic between-batch drift is correctly
> penalised by ICC(2,1) while ICC(3,1) consistency would miss it. Reported *with*
> absolute error, because ICC scales with between-person spread (`icc.py:11-20`).

**Result (`out/leaderboard.csv`)** — 8 clocks, all "excellent", ICC 0.918–0.998; SEM
0.32 yr (PCGrimAge) to 2.79 yr (PhenoAge). Every PC variant beats its original.

### 6.2 The primary endpoint — `contrast.py`

The headline question is not "is clock X reliable?" but "does the PC transform reduce
its technical noise?". The metric is the **within-subject variance ratio**, computed
paired on the same subjects so between-person spread cancels
(`contrast.py:63-124`):
```python
v_o = _var_within(a)          # two-way residual MSE, original
v_t = _var_within(b)          # two-way residual MSE, transformed (PC)
ratio = v_t / v_o             # < 1 favours PC
# paired bootstrap: resample SUBJECTS (the clustering unit), 2000×, seed 0
idx = rng.integers(0, n, n)
```
**Verdict rule** (`contrast.py:103-110`): whole CI below 1 → `supported`; point < 1 but
CI includes 1 → `directionally_supported`; point ≥ 1 → `not_supported`.

> **Why variance ratio (not ICC) for the primary endpoint?** ICC depends on
> between-person heterogeneity; the variance ratio does not, which makes it portable
> across cohorts. **Why bootstrap subjects, not measurements?** Subjects are the
> independent sampling unit; resampling individual measurements would understate
> uncertainty (`contrast.py:1-16`).

**Result (`out/contrasts.csv`)** — all four pairs `supported`, every 95% CI below 1:

| pair | variance ratio | 95% CI |
|---|---|---|
| Horvath1→PC | 0.133 | (0.065, 0.259) |
| Hannum→PC | 0.135 | (0.058, 0.329) |
| PhenoAge→PC | 0.036 | (0.021, 0.060) |
| GrimAge→PC | 0.128 | (0.075, 0.219) |

Joint verdict (`results.json`): **supported, 4/4 pairs improve**.

### 6.3 Detectability — `detectability.py`

`recommend_for_effect` (`detectability.py:88-112`) answers "given an expected effect,
which clocks can detect it?" using each clock's SEM. Individual threshold = MDC95;
`recommend_for_effect` ranks clocks by SEM and reports which clear the effect. On
GSE55763: effect 1.0 yr → only PCGrimAge; 2.0 → all four PC clocks; 5.0 → six clocks
(`RESULTS.md`).

> **This is a measurement-noise SCREEN, not a power calculation** — it accounts only
> for technical error. "Detectable" means "not ruled out by measurement noise," never
> "the trial is powered" (`detectability.py:19-24`).

**Debugging — Stage 6**

- **`compute_icc` raises on NaN.** By contract it needs a complete rectangular matrix
  (`icc.py:203-204`); incomplete subjects must be dropped *before* the call —
  `build_replicate_matrix` is what does that. If you feed it raw scores you'll hit the
  NaN guard.
- **A clock silently missing from a contrast.** `run_analysis` only contrasts
  `usable_pairs` — pairs where *both* labels exist in the wide frame
  (`run_analysis.py:74`). If PC scoring failed (Stage 4 fallback), the wide frame has
  no `PC*` columns and `contrasts.csv` is empty → verdict `inconclusive`.
- **Non-determinism.** The bootstrap is seeded (`seed=0`, `contrast.py:70`); a changed
  CI means changed inputs or a changed seed, not randomness.

---

## Stage 7 — Age-acceleration ICC (companion)

**Purpose.** Higgins-Chen report ICC two ways — raw age and age-acceleration — so
reliage does too. Age acceleration = the residual of the score regressed on
chronological age.

**File:** `reliage/scoring/age_accel_icc.py` · **Entry:**
```bash
python -m reliage.scoring.age_accel_icc scores.csv map.csv pheno.csv
```

**The OLS** (`age_accel_icc.py:24-28`) — a per-clock degree-1 `np.polyfit`, subtract the fit:
```python
for c in wide.columns:
    y = wide[c].astype(float).values
    b1, b0 = np.polyfit(age.values, y, 1)      # OLS score ~ age
    accel[c] = y - (b0 + b1 * age.values)      # residual = age acceleration
```
Then it reruns `run_reliability_benchmark` and `run_paired_contrasts` on the residuals.

> **Why the variance ratio and SEM are invariant here:** both replicates of a subject
> share the same chronological age, so residualizing subtracts an *identical* value
> from each member of a pair — within-subject (technical) variance is unchanged; only
> between-subject variance shrinks, so ICC drops. This is a *predicted* invariance and
> a useful sanity check (`age_accel_icc.py:1-9`). Output: `out/leaderboard_ageaccel.csv`.

---

## Stage 8 — Robustness audit

**Purpose.** Try to *break* the result four ways before trusting it (disprove-first,
Principle P2). Uses reliage's own engine so every recomputation matches the headline.

**File:** `reliage/scoring/robustness.py` · **Entry:**
```bash
python -m reliage.scoring.robustness scores.csv map.csv pheno.csv out/robustness
```

**The four parts**

1. **Compression / signal-preservation audit** (`robustness.py:32-67`). For every
   clock: within-var (two-way MSE), between-subject var, age correlation, ranking
   preservation. Then per pair: `noise_ratio = PC/orig within` and
   `signal_preservation_ratio = PC/orig between`. This is the answer to "is PC just
   compressing the scale?" — **no**: noise falls 87–96% while between-subject signal
   is retained 74–85% (`CLAIMS.md:17`). → `compression_audit.csv`, `compression_summary.csv`
2. **Leave-one-subject-out** (`robustness.py:69-88`). Recompute the variance ratio and
   ICC with each subject omitted; check no verdict flips. → `loso.csv`
3. **Pair-level replicate differences** (`robustness.py:90-101`). Every subject's
   batch1/batch2/`absdiff` per clock — the raw material for the largest-discrepancy and
   batch-bias checks. → `pair_diffs.csv`
4. **Bland–Altman** (`robustness.py:103-116`). Bias, limits of agreement, and a
   proportional-bias test (`|diff|` vs mean). → `bland_altman.csv`

**Debugging — Stage 8:** every part reuses `_var_within`, `compute_icc`,
`variance_ratio_contrast` from the core — if a robustness number disagrees with the
headline, suspect the *inputs* (wrong scores/map), not a second implementation, because
there isn't one.

---

## Stage 9 — Figures

**Purpose.** Render the robustness-qualified result. Pure consumer of Stage 6/8 CSVs —
it computes nothing new.

**File:** `reliage/scoring/figures.py` · **Entry:**
```bash
python -m reliage.scoring.figures generated/GSE55763/out generated/GSE55763/out/figures
```

**Which CSV → which figure** (`figures.py:20-24` reads; each block writes one PNG):

| Figure | Reads | Shows |
|---|---|---|
| `1_forest.png` | `contrasts.csv` | variance ratios + 95% CI, null at 1 |
| `2_paired_error.png` | `robustness/pair_diffs.csv` | per-subject \|diff\|, original→PC |
| `3_bland_altman.png` | `pair_diffs.csv` + `bland_altman.csv` | B-A panels, original vs PC |
| `4_signal_vs_noise.png` | `robustness/compression_summary.csv` | signal retained vs noise removed |
| `5_loso.png` | `robustness/loso.csv` | variance ratio by omitted subject |

`matplotlib.use("Agg")` (`figures.py:12`) — headless, no display needed.

---

## Secondary analyses (same seam, same engine)

- **ICC-form sensitivity** — `reliage/scoring/icc_sensitivity.py`. Reruns ICC(1,1),
  (2,1), (3,1) on the frozen table and checks the conclusion (PC excellent; PC >
  original) is stable across forms. Entry:
  `python -m reliage.scoring.icc_sensitivity scores.csv map.csv`.
- **Tier-3 published-reference comparison** — `reliage/scoring/tier3_compare.py`.
  Compares reliage's frozen outputs to pinned Higgins-Chen anchors within locked
  tolerances (median/max |replicate diff| + ICC bands). Verdict PASS/PARTIAL/NOT MET.
  Entry: `python -m reliage.scoring.tier3_compare generated/GSE55763/out`.

Both read the Versioned Score Table and the frozen `out/` artifacts — never betas.

---

## Important objects (who creates, who consumes)

| Object | File | Created by | Consumed by |
|---|---|---|---|
| **Versioned Score Table** | `processed/scores.csv` | a scorer (Stage 4/4') | every reliage analysis |
| **Replicate map** | `metadata/map.csv` | Stage 2 | `load_map` in every analysis |
| **Leaderboard** | `out/leaderboard.csv` | `benchmark.py` | figures, Tier-3, humans |
| **Contrasts** | `out/contrasts.csv` | `contrast.py` | figures, verdict roll-up |
| **RESULTS.md** | `out/RESULTS.md` | `run_analysis.py` | humans; supports CLAIMS |
| **CLAIMS.md** | `docs/PIR03-C2/CLAIMS.md` | maintainer (by hand) | the scientific state of record |

> **Reading order for a new maintainer:** README → this walkthrough → run the demo →
> `CLAIMS.md` (what's actually established) → `FOUNDRY_PRINCIPLES.md` (why). Reports,
> milestones, and figures **support** the CLAIMS ledger; they do not define it
> (`CLAIMS.md:1-5`). `CLAIMS.md` is hand-maintained — no code writes it.

---

## Consolidated design decisions (the "why")

| Decision | Why | Where |
|---|---|---|
| **Scorer-agnostic** (score table, not betas) | the reliability question is about *scores*; the verified core never touches a multi-GB matrix, and any scorer can be swapped | `benchmark.py:18-20`, PIPELINE §5 |
| **Long-form VST** | units differ across clocks; every score must be independently attributable | `PROTOCOL.md` §2 |
| **ICC(2,1) primary** | absolute agreement treats batch as random and penalises drift; ICC(1,1)/(3,1) as sensitivity | `icc.py:11-20` |
| **Variance ratio as primary endpoint** | independent of between-person spread → portable across cohorts | `contrast.py:1-16` |
| **Bootstrap resamples subjects** | subjects are the independent unit; seeded for determinism | `contrast.py:70,92` |
| **Coverage as a gate** | a pair is invalid if original/PC used different coverage/imputation | `PROVENANCE.md`, CLAUDE.md |
| **Rebuild from GEO, not the RData fast path** | public-reproducibility is only earned on canonical files | `PROTOCOL.md` §5 |
| **Match clocks by biological definition, not name** | pyaging `dnamphenoage` ≠ `phenoage`; GrimAge V1 ≠ V2 | `score_pyaging.py:23`, P3 |

---

## Common debugging — quick index

| Symptom | Stage | Cause / fix |
|---|---|---|
| `FATAL: expected 72 beta columns` | 3 | id list ≠ matrix headers; regenerate `replicate_sample_ids.txt` |
| `matrix looks truncated` (exit 5) | 3 | `zcat` stopped early; re-download, re-check md5 |
| R `stop("pheno.csv needs an 'age'/'female' column")` | 4 | GrimAge/PC need capitalized `Age`+`Female` (0/1) |
| `check_DNAm` rejects a probe | 4 | an all-NA CpG; the pre-drop at `:39-46` handles it — regenerate betas if bypassed |
| `qs2`/`stringfish` DLL-load failure | 4 | rebuild those packages from source |
| PIN CHECK says `ORIGINALS ONLY - PC failed` | 4 | PC reference missing/incompatible; check the `.qs2` path/Zenodo DOI |
| `contrasts.csv` empty / verdict `inconclusive` | 6 | no `PC*` columns (PC scoring failed upstream) |
| `compute_icc` raises on NaN | 6 | feed it a complete matrix via `build_replicate_matrix`, not raw scores |
| GrimAge scores look off in pyaging | 4' | Female/Age must be the last two *columns* of the matrix, not `obs` |
| PhenoAge disagrees between scorers | 4' | map to pyaging `dnamphenoage`, not clinical `phenoage` |

---

## 11 · Full reproduction command sequence

Environment: R 4.6.1 + Rtools45, methylCIPHER `@9e8c1e5` (+ `qs2`/`stringfish` built
from source), Python with numpy/pandas/scipy. (Verbatim from
[`PIPELINE.md`](PIR03-C2/PIPELINE.md) §7.)

```bash
# 1. replicate design from the series matrix
python tools/GSE55763/parse_metadata.py \
       $LONGEVITY_DATA_ROOT/GSE55763/raw/GSE55763_series_matrix.txt.gz  generated/GSE55763/metadata

# 2. extract the 72 replicate beta columns from the 9.7 GB matrix
bash tools/GSE55763/extract_betas.sh \
       generated/GSE55763/metadata/replicate_sample_ids.txt \
       /path/to/GSE55763_normalized_betas.txt.gz \
       generated/GSE55763/processed/betas.csv

# 3. score (methylCIPHER engine) — pin the commit inside the R script first
Rscript reliage/scoring/score_methylCIPHER.R \
       generated/GSE55763/processed/betas.csv \
       generated/GSE55763/metadata/pheno.csv \
       generated/GSE55763/processed/scores.csv \
       /path/to/PCClocks_data.qs2

# 4. reliability analysis (reliage engine) -> RESULTS.md
python -m reliage.scoring.run_analysis \
       generated/GSE55763/processed/scores.csv \
       generated/GSE55763/metadata/map.csv \
       --out generated/GSE55763/out

# 5. age-acceleration ICC (companion)
python -m reliage.scoring.age_accel_icc \
       generated/GSE55763/processed/scores.csv \
       generated/GSE55763/metadata/map.csv \
       generated/GSE55763/metadata/pheno.csv
```

Verify the engine independently of any data:
```bash
python -m reliage.selfcheck     # 4 gates: ICC vs Shrout–Fleiss, end-to-end ICC
                                # recovery, variance-ratio recovery, detectability bands
pytest -q                       # full suite
```

---

## Cross-reference table (file → function → approx. line)

| Stage | File | Function / anchor | Line |
|---|---|---|---|
| 1 | `data/download_data.sh` | `get_gse55763()` | 27-37 |
| 2 | `tools/GSE55763/parse_metadata.py` | pairing regex | 41 |
| 2 | ″ | pairing audit | 68-69 |
| 3 | `tools/GSE55763/extract_betas.sh` | `zcat \| awk` extract | 17-29 |
| 3 | ″ | 72-column assert | 23 |
| 4 | `reliage/scoring/score_methylCIPHER.R` | pin block | 18-22 |
| 4 | ″ | all-NA drop | 39-46 |
| 4 | ″ | Age/Female pheno | 59-62 |
| 4 | ″ | original clocks | 76-81 |
| 4 | ″ | `calcPCClocks` | 84-87 |
| 4' | `reliage/scoring/score_pyaging.py` | clock mapping | 20-25 |
| 4' | ″ | GrimAge features | 37-42 |
| 6 | `reliage/scoring/run_analysis.py` | `run()` | 62-118 |
| 6 | `reliage/benchmark.py` | `build_replicate_matrix` | 37-68 |
| 6 | `reliage/benchmark.py` | `run_reliability_benchmark` | 142-209 |
| 6 | `reliage/icc.py` | `compute_icc` | 175-240 |
| 6 | `reliage/icc.py` | `smallest_detectable_change` (MDC95) | 116-127 |
| 6 | `reliage/contrast.py` | `variance_ratio_contrast` | 63-124 |
| 6 | `reliage/detectability.py` | `recommend_for_effect` | 88-112 |
| 7 | `reliage/scoring/age_accel_icc.py` | OLS residual | 24-28 |
| 8 | `reliage/scoring/robustness.py` | 4 parts | 32-116 |
| 9 | `reliage/scoring/figures.py` | 5 figures | 26-105 |

---

*This document reflects the frozen `v0.3.1-scientific-baseline` state. If a cited
line moves, trust the function name and the surrounding comment over the number, and
update this file. The scientific state of record is always
[`CLAIMS.md`](PIR03-C2/CLAIMS.md), not any report.*
