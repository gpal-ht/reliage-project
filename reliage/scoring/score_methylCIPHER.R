#!/usr/bin/env Rscript
# PRIMARY scorer for reliage v1 (LOCKED: methylCIPHER).
# Produces a long-form, provenance-pinned score table that reliage ingests.
# This script is meant to run WHERE R + the data live (not the cloud sandbox).
#
# Usage:
#   Rscript score_methylCIPHER.R betas.csv pheno.csv out_scores.csv [pc_reference]
#     betas.csv    : CpGs in rows (rownames = cg ids), samples in columns  [or transpose; auto-detected]
#     pheno.csv    : sample_id, age, female   (age + female REQUIRED for GrimAge & PC clocks)
#     out_scores.csv : long-form score table written here
#     pc_reference : OPTIONAL path to PCClocks_data.qs2 (or the dir containing it).
#                    If omitted, methylCIPHER's cache is used (download_methylCIPHER()).
#
# API: written against methylCIPHER 0.2.0 (calcGrimAgeV1/V2(DNAm, pheno);
#      calcPCClocks(DNAm, pheno, RData); pheno needs capitalized Age + Female).
#
# ---- PIN THESE (mandatory provenance; do NOT leave blank) --------------------
REPO_URL   <- "https://github.com/HigginsChenLab/methylCIPHER"
COMMIT     <- "9e8c1e55f53c3fdeaf32a38cc8ef109be8b2a8c8"  # HigginsChenLab/methylCIPHER HEAD, pinned 2026-07-24
IMPUTATION <- "mean (methylCIPHER default: PC clocks mean-impute missing clock CpGs)"
GRIMAGE_VARIANT <- "V1"   # LOCKED per CLOCK_MANIFEST.csv: original GrimAge = V1, paired with PCGrimAge
# -----------------------------------------------------------------------------

suppressWarnings(suppressMessages({
  library(methylCIPHER)   # remotes::install_github("HigginsChenLab/methylCIPHER@<COMMIT>")
}))

args  <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) stop("usage: Rscript score_methylCIPHER.R betas.csv pheno.csv out_scores.csv [pc_reference]")
# Generated inputs are not committed (see docs/PIR03-C2/GENERATED_FILES.md) — fail clearly if absent.
if (!file.exists(args[1])) stop("Missing generated file: betas.csv (", args[1], ").\n",
  "  Generate with: bash tools/GSE55763/extract_betas.sh <replicate_sample_ids.txt> <betas.txt.gz> ", args[1], "\n",
  "  See docs/PIR03-C2/GENERATED_FILES.md")
if (!file.exists(args[2])) stop("Missing generated file: pheno.csv (", args[2], ").\n",
  "  Generate with: python tools/GSE55763/parse_metadata.py <series_matrix.txt.gz> generated/GSE55763/metadata\n",
  "  See docs/PIR03-C2/GENERATED_FILES.md")
betas <- read.csv(args[1], row.names = 1, check.names = FALSE)
pheno_in <- read.csv(args[2], stringsAsFactors = FALSE)
outfn <- args[3]
pc_reference <- if (length(args) >= 4 && nzchar(args[4])) args[4] else NULL

# Orient to samples-in-rows x CpGs-in-cols (methylCIPHER convention).
if (any(grepl("^cg", rownames(betas)))) betas <- t(as.matrix(betas))
betas <- as.matrix(betas)

# Drop CpGs that are NA in ALL samples: methylCIPHER::check_DNAm rejects them
# outright (GrimAge/PC), whereas partial-NA CpGs are imputed. Dropping converts
# an all-NA probe to a "missing" probe that the clocks impute. Count recorded.
n_all_na <- sum(colSums(is.na(betas)) == nrow(betas))
if (n_all_na > 0) {
  betas <- betas[, colSums(is.na(betas)) < nrow(betas), drop = FALSE]
  message("Preprocessing: dropped ", n_all_na, " CpGs NA in all samples (-> imputed as missing).")
}
sample_ids <- rownames(betas)

# --- build a methylCIPHER-shaped pheno (capitalized Age + Female), row-aligned to betas ---
pin <- tolower(names(pheno_in))
col <- function(...) { for (n in c(...)) if (n %in% pin) return(names(pheno_in)[match(n, pin)]); NA_character_ }
sid_col    <- col("sample_id", "sampleid", "sample", "id", "geo_accession")
age_col    <- col("age")
female_col <- col("female", "sex_female", "is_female")
if (is.na(sid_col))    stop("pheno.csv needs a sample-id column (sample_id/id).")
if (is.na(age_col))    stop("pheno.csv needs an 'age' column (required for GrimAge/PC).")
if (is.na(female_col)) stop("pheno.csv needs a 'female' column 0/1 (required for GrimAge/PC).")

ph <- data.frame(Sample_ID = as.character(pheno_in[[sid_col]]),
                 Age = as.numeric(pheno_in[[age_col]]),
                 Female = as.integer(pheno_in[[female_col]] %in% c(1, "1", TRUE, "TRUE", "F", "female", "Female")),
                 stringsAsFactors = FALSE)
ord <- match(sample_ids, ph$Sample_ID)
if (any(is.na(ord))) stop("Some betas samples are missing from pheno.csv: ",
                          paste(head(sample_ids[is.na(ord)]), collapse = ", "))
pheno <- ph[ord, , drop = FALSE]           # now aligned 1:1 with betas rows
rownames(pheno) <- pheno$Sample_ID

r_version   <- paste(R.version$major, R.version$minor, sep = ".")
pkg_version <- as.character(packageVersion("methylCIPHER"))

# Coverage per clock (getClockProbes: present/total/percent) -> attach to provenance.
coverage <- tryCatch(getClockProbes(betas), error = function(e) NULL)

# --- ORIGINAL clocks (the four protocol-locked families) ---------------------
orig <- data.frame(sample_id = sample_ids, stringsAsFactors = FALSE)
orig$Horvath1 <- as.numeric(calcHorvath1(betas))
orig$Hannum   <- as.numeric(calcHannum(betas))
orig$PhenoAge <- as.numeric(calcPhenoAge(betas))
grim <- calcGrimAgeV1(betas, pheno)                       # V1 per manifest -> column 'GrimAgeV1'
orig$GrimAge  <- as.numeric(grim[[grep("GrimAge", names(grim), value = TRUE)[1]]])

# --- PC clocks (single call returns PCHorvath1/PCHannum/PCPhenoAge/PCGrimAge/...) ---
pc <- tryCatch(
  calcPCClocks(betas, pheno, RData = pc_reference),
  error = function(e) { message("PC clocks FAILED (reference missing/incompatible?): ", conditionMessage(e)); NULL }
)

# --- assemble LONG-FORM provenance-pinned score table ------------------------
mk <- function(sample_id, clock_id, variant, score, unit, fn) {
  data.frame(sample_id = sample_id, clock_id = clock_id, variant = variant,
             score = as.numeric(score), unit = unit,
             implementation = "methylCIPHER", repo_url = REPO_URL, commit = COMMIT,
             r_version = r_version, pkg_version = pkg_version, clock_function = fn,
             imputation = IMPUTATION, stringsAsFactors = FALSE)
}
rows <- rbind(
  mk(orig$sample_id, "Horvath1", "original", orig$Horvath1, "years", "calcHorvath1"),
  mk(orig$sample_id, "Hannum",   "original", orig$Hannum,   "years", "calcHannum"),
  mk(orig$sample_id, "PhenoAge", "original", orig$PhenoAge, "years", "calcPhenoAge"),
  mk(orig$sample_id, "GrimAge",  "original", orig$GrimAge,  "years", "calcGrimAgeV1")
)
if (!is.null(pc)) {
  pc_sid <- if (!is.null(pc$Sample_ID)) as.character(pc$Sample_ID) else sample_ids
  rows <- rbind(rows,
    mk(pc_sid, "Horvath1", "PC", pc$PCHorvath1, "years", "calcPCClocks:PCHorvath1"),
    mk(pc_sid, "Hannum",   "PC", pc$PCHannum,   "years", "calcPCClocks:PCHannum"),
    mk(pc_sid, "PhenoAge", "PC", pc$PCPhenoAge, "years", "calcPCClocks:PCPhenoAge"),
    mk(pc_sid, "GrimAge",  "PC", pc$PCGrimAge,  "years", "calcPCClocks:PCGrimAge")
  )
}
write.csv(rows, outfn, row.names = FALSE)

cat("wrote", nrow(rows), "score rows to", outfn,
    "(", if (is.null(pc)) "ORIGINALS ONLY - PC failed" else "originals + PC", ")\n")
cat("PIN CHECK - commit:", COMMIT, "| pkg:", pkg_version, "| R:", r_version,
    "| GrimAge:", GRIMAGE_VARIANT, "| all-NA CpGs dropped:", n_all_na, "\n")
if (!is.null(coverage)) {
  cat("coverage via getClockProbes (attach to provenance):\n")
  print(utils::head(coverage))
}
