#!/usr/bin/env bash
# Download the public datasets for the reliage reliability experiment.
#
# RUN THIS WHERE THE DATA SHOULD LIVE (your machine / the repo's data dir),
# NOT in an ephemeral cloud sandbox: the methylation matrices are large and the
# sandbox is reclaimed after inactivity.
#
# Requires: wget, gunzip, git. For the GEO route, optionally Python + GEOparse.
# Usage:   bash download_data.sh [pcclocks|gse55763|emtab4664|gse49065|satsa|all]
set -euo pipefail
DATA_DIR="$(cd "$(dirname "$0")" && pwd)"
target="${1:-all}"

fetch() { echo ">> $1"; }

# --- 1. PC-Clocks example replicate data (Lehne subset) — FASTEST START -------
get_pcclocks() {
  fetch "PC-Clocks example replicate data (technical; small)"
  mkdir -p "$DATA_DIR/pcclocks_example"
  # The repo ships Example_PCClock_Data.RData (Lehne 2015 technical replicates).
  git clone --depth 1 https://github.com/MorganLevineLab/PC-Clocks.git \
    "$DATA_DIR/pcclocks_example/PC-Clocks" || true
  echo "   -> $DATA_DIR/pcclocks_example/PC-Clocks/ (see *.RData)"
}

# --- 2. GSE55763 (Lehne 2015 full; 450K; 36 duplicate pairs) ------------------
get_gse55763() {
  fetch "GSE55763 (technical; LARGE, several GB)"
  mkdir -p "$DATA_DIR/GSE55763"
  # Supplementary files (normalized betas etc.) live under the series suppl dir:
  wget -r -np -nH --cut-dirs=6 -R "index.html*" \
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE55nnn/GSE55763/suppl/" \
    -P "$DATA_DIR/GSE55763/" || true
  echo "   -> pick the normalized beta matrix from $DATA_DIR/GSE55763/"
  # Python alternative:
  #   python -c "import GEOparse; GEOparse.get_GEO('GSE55763', destdir='$DATA_DIR/GSE55763')"
}

# --- 3. E-MTAB-4664 (sleep deprivation; biological ~1 day; blood) -------------
get_emtab4664() {
  fetch "E-MTAB-4664 (biological; use normal-sleep arm)"
  mkdir -p "$DATA_DIR/E-MTAB-4664"
  wget -r -np -nH --cut-dirs=8 -R "index.html*" \
    "https://ftp.ebi.ac.uk/biostudies/fire/E-MTAB-/664/E-MTAB-4664/Files/" \
    -P "$DATA_DIR/E-MTAB-4664/" || \
    echo "   (if that path 404s, browse https://www.ebi.ac.uk/biostudies/studies/E-MTAB-4664 for the Files link)"
}

# --- 4. GSE49065 (sleep-dep companion; biological) ----------------------------
get_gse49065() {
  fetch "GSE49065 (biological companion)"
  mkdir -p "$DATA_DIR/GSE49065"
  wget -r -np -nH --cut-dirs=6 -R "index.html*" \
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE49nnn/GSE49065/suppl/" \
    -P "$DATA_DIR/GSE49065/" || true
}

# --- 5. SATSA E-MTAB-7309 (technical) -----------------------------------------
get_satsa() {
  fetch "E-MTAB-7309 / SATSA (technical)"
  mkdir -p "$DATA_DIR/E-MTAB-7309"
  wget -r -np -nH --cut-dirs=8 -R "index.html*" \
    "https://ftp.ebi.ac.uk/biostudies/fire/E-MTAB-/309/E-MTAB-7309/Files/" \
    -P "$DATA_DIR/E-MTAB-7309/" || \
    echo "   (browse https://www.ebi.ac.uk/biostudies/studies/E-MTAB-7309 if the path changed)"
}

# NOTE: the within-day DIURNAL dataset (best biological-reliability fit) still
# needs its accession pinned from the Koncevicius 2024 / 2025 daily-rhythm papers;
# add a get_diurnal() block once resolved.

case "$target" in
  pcclocks)  get_pcclocks ;;
  gse55763)  get_gse55763 ;;
  emtab4664) get_emtab4664 ;;
  gse49065)  get_gse49065 ;;
  satsa)     get_satsa ;;
  all)       get_pcclocks; get_emtab4664; get_gse49065; get_satsa; get_gse55763 ;;
  *) echo "usage: bash download_data.sh [pcclocks|gse55763|emtab4664|gse49065|satsa|all]"; exit 1 ;;
esac
echo "Done. See DATASETS.md for the download -> reliage steps."
