#!/usr/bin/env bash
# Download public datasets into the SHARED external data root — NOT into this repo.
# The methylation matrices are large; keeping them in one external location lets
# multiple longevity repos reference the same dataset, avoids per-repo duplication,
# and keeps multi-GB blobs out of git and out of any cloud-synced folder.
#
# Data root resolution (first match wins):
#   1. --data-root DIR        (explicit)
#   2. $LONGEVITY_DATA_ROOT    (env var; set this once per machine)
#   3. default: C:/Ambitious Projects/Longevity Project/Datasets
#
# Layout written:  $DATA_ROOT/<DATASET>/raw/   (processed/ + metadata/ are built later)
#
# Requires: wget, gunzip, git. For the GEO route, optionally Python + GEOparse.
# Usage:  bash download_data.sh [--data-root DIR] [gse55763|emtab4664|gse49065|satsa|all]
set -euo pipefail

DATA_ROOT="${LONGEVITY_DATA_ROOT:-C:/Ambitious Projects/Longevity Project/Datasets}"
if [ "${1:-}" = "--data-root" ]; then DATA_ROOT="$2"; shift 2; fi
target="${1:-all}"
mkdir -p "$DATA_ROOT"
echo "Data root: $DATA_ROOT   (override with LONGEVITY_DATA_ROOT or --data-root DIR)"

fetch() { echo ">> $1"; }

# --- 1. GSE55763 (Lehne 2015 full; 450K; 36 duplicate pairs) ------------------
get_gse55763() {
  fetch "GSE55763 (technical; betas LARGE + series matrix small)"
  raw="$DATA_ROOT/GSE55763/raw"
  mkdir -p "$raw"
  # Two SOURCE files, in two different GEO dirs; fetch each independently (skip if present).
  # (a) normalized beta matrix (~9.7 GB) — the DATA — lives under the series suppl dir:
  if [ -f "$raw/GSE55763_normalized_betas.txt.gz" ]; then
    echo "   betas already present — skipping"
  else
    wget -r -np -nH --cut-dirs=6 -R "index.html*" \
      "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/suppl/" \
      -P "$raw/" || true
  fi
  # (b) series matrix (~50 KB) — the sample METADATA / replicate design (Stage 2) — lives
  #     under the series matrix dir. Needed to rebuild map.csv / pheno.csv.
  if [ -f "$raw/GSE55763_series_matrix.txt.gz" ]; then
    echo "   series matrix already present — skipping"
  else
    wget -P "$raw/" \
      "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/matrix/GSE55763_series_matrix.txt.gz" || true
  fi
  echo "   -> beta matrix + series matrix under $raw/"
  # Python alternative:
  #   python -c "import GEOparse; GEOparse.get_GEO('GSE55763', destdir='$raw')"
}

# --- 2. E-MTAB-4664 (sleep deprivation; biological ~1 day; blood) -------------
get_emtab4664() {
  fetch "E-MTAB-4664 (biological; use normal-sleep arm)"
  mkdir -p "$DATA_ROOT/E-MTAB-4664/raw"
  wget -r -np -nH --cut-dirs=8 -R "index.html*" \
    "https://ftp.ebi.ac.uk/biostudies/fire/E-MTAB-/664/E-MTAB-4664/Files/" \
    -P "$DATA_ROOT/E-MTAB-4664/raw/" || \
    echo "   (if that path 404s, browse https://www.ebi.ac.uk/biostudies/studies/E-MTAB-4664 for the Files link)"
}

# --- 3. GSE49065 (sleep-dep companion; biological) ----------------------------
get_gse49065() {
  fetch "GSE49065 (biological companion)"
  mkdir -p "$DATA_ROOT/GSE49065/raw"
  wget -r -np -nH --cut-dirs=6 -R "index.html*" \
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE49nnn/GSE49065/suppl/" \
    -P "$DATA_ROOT/GSE49065/raw/" || true
}

# --- 4. SATSA E-MTAB-7309 (technical) -----------------------------------------
get_satsa() {
  fetch "E-MTAB-7309 / SATSA (technical)"
  mkdir -p "$DATA_ROOT/E-MTAB-7309/raw"
  wget -r -np -nH --cut-dirs=8 -R "index.html*" \
    "https://ftp.ebi.ac.uk/biostudies/fire/E-MTAB-/309/E-MTAB-7309/Files/" \
    -P "$DATA_ROOT/E-MTAB-7309/raw/" || \
    echo "   (browse https://www.ebi.ac.uk/biostudies/studies/E-MTAB-7309 if the path changed)"
}

# NOTE: the within-day DIURNAL dataset (best biological-reliability fit) still
# needs its accession pinned from the Koncevicius 2024 / 2025 daily-rhythm papers;
# add a get_diurnal() block once resolved.

case "$target" in
  gse55763)  get_gse55763 ;;
  emtab4664) get_emtab4664 ;;
  gse49065)  get_gse49065 ;;
  satsa)     get_satsa ;;
  all)       get_emtab4664; get_gse49065; get_satsa; get_gse55763 ;;
  *) echo "usage: bash download_data.sh [--data-root DIR] [gse55763|emtab4664|gse49065|satsa|all]"; exit 1 ;;
esac
echo "Done. Data root: $DATA_ROOT. See DATASETS.md for the build -> reliage steps."
