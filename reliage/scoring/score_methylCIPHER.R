#!/usr/bin/env Rscript
# PRIMARY scorer for reliage v1 (LOCKED: methylCIPHER).
# Produces a long-form, provenance-pinned score table that reliage ingests.
# This script is meant to run WHERE R + the data live (not the cloud sandbox).
#
# Usage:
#   Rscript score_methylCIPHER.R betas.csv pheno.csv out_scores.csv
#     betas.csv : CpGs in rows (rownames = cg ids), samples in columns  [or transpose; auto-detected]
#     pheno.csv : sample_id, age, female   (age/female required for GrimAge)
#
# ---- PIN THESE (mandatory provenance; do NOT leave blank) --------------------
REPO_URL   <- "https://github.com/HigginsChenLab/methylCIPHER"
COMMIT     <- "<PIN_EXACT_COMMIT_HASH>"     # e.g. git rev-parse HEAD in the cloned repo
IMPUTATION <- "none"                          # methylCIPHER default: imputation OFF
# -----------------------------------------------------------------------------

suppressWarnings(suppressMessages({
  library(methylCIPHER)   # devtools::install_github("HigginsChenLab/methylCIPHER")
}))

args  <- commandArgs(trailingOnly = TRUE)
betas <- read.csv(args[1], row.names = 1, check.names = FALSE)
pheno <- read.csv(args[2], stringsAsFactors = FALSE)
outfn <- args[3]

# Orient to samples-in-rows x CpGs-in-cols (methylCIPHER convention).
if (any(grepl("^cg", rownames(betas)))) betas <- as.data.frame(t(betas))

r_version   <- paste(R.version$major, R.version$minor, sep = ".")
pkg_version <- as.character(packageVersion("methylCIPHER"))

# Coverage per clock (getClockProbes returns present/total/percent).
coverage <- tryCatch(getClockProbes(betas), error = function(e) NULL)

# --- compute the four protocol-locked pairs + extras --------------------------
# Originals:
orig <- data.frame(sample_id = rownames(betas))
orig$Horvath1  <- calcHorvath1(betas)
orig$Hannum    <- calcHannum(betas)
orig$PhenoAge  <- calcPhenoAge(betas)
orig$GrimAge   <- calcGrimAgeV2(betas, age = pheno$age, female = pheno$female)  # PIN V1 vs V2
# PC versions (single call returns PCHorvath1, PCHannum, PCPhenoAge, PCGrimAge, ...):
pc <- calcPCClocks(betas, PCClocks_object = NULL)   # supply the CalcAllPCClocks reference object

# --- assemble LONG-FORM provenance-pinned score table -------------------------
mk <- function(sample_id, clock_id, variant, score, unit, fn) {
  data.frame(sample_id = sample_id, clock_id = clock_id, variant = variant,
             score = score, unit = unit,
             implementation = "methylCIPHER", repo_url = REPO_URL, commit = COMMIT,
             r_version = r_version, pkg_version = pkg_version, clock_function = fn,
             imputation = IMPUTATION, stringsAsFactors = FALSE)
}
rows <- rbind(
  mk(orig$sample_id, "Horvath1", "original", orig$Horvath1, "years", "calcHorvath1"),
  mk(orig$sample_id, "Hannum",   "original", orig$Hannum,   "years", "calcHannum"),
  mk(orig$sample_id, "PhenoAge", "original", orig$PhenoAge, "years", "calcPhenoAge"),
  mk(orig$sample_id, "GrimAge",  "original", orig$GrimAge,  "years", "calcGrimAgeV2"),
  mk(rownames(pc),   "Horvath1", "PC",       pc$PCHorvath1, "years", "calcPCClocks:PCHorvath1"),
  mk(rownames(pc),   "Hannum",   "PC",       pc$PCHannum,   "years", "calcPCClocks:PCHannum"),
  mk(rownames(pc),   "PhenoAge", "PC",       pc$PCPhenoAge, "years", "calcPCClocks:PCPhenoAge"),
  mk(rownames(pc),   "GrimAge",  "PC",       pc$PCGrimAge,  "years", "calcPCClocks:PCGrimAge")
)
write.csv(rows, outfn, row.names = FALSE)
cat("wrote", nrow(rows), "score rows to", outfn, "\n")
cat("PIN CHECK — commit:", COMMIT, "| pkg:", pkg_version, "| R:", r_version, "\n")
if (!is.null(coverage)) cat("coverage computed via getClockProbes (attach to provenance)\n")
