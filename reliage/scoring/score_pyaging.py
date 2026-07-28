"""E2 SECONDARY scorer: pyaging producer for the Versioned Score Table.

Emits the IDENTICAL long-form schema as score_methylCIPHER.R so the same reliage
pipeline ingests it unchanged. Only the scoring implementation differs (that is the
E2 independent variable). Runs in an isolated Python 3.13 env (pyaging needs <3.14).

Usage:
  python score_pyaging.py betas.csv pheno.csv out_scores.csv
    betas.csv : CpGs in rows (rownames=cg ids), samples in cols  [auto-transposed]
    pheno.csv : sample_id, age, female  (age+female required for GrimAge)

Clock mapping is PINNED in docs/PIR03-C2/E2_PROTOCOL.md.
"""
import os, sys, pandas as pd, numpy as np
import pyaging as pya

betas_csv, pheno_csv, outfn = sys.argv[1], sys.argv[2], sys.argv[3]

# Generated inputs are not committed (see docs/PIR03-C2/GENERATED_FILES.md). This scorer
# runs in an isolated env without reliage importable, so guard inline rather than via
# reliage.scoring.generated_manifest.
for _p, _how in ((betas_csv, "bash tools/GSE55763/extract_betas.sh <ids> <betas.txt.gz> " + betas_csv),
                 (pheno_csv, "python tools/GSE55763/parse_metadata.py <series_matrix.txt.gz> generated/GSE55763/metadata")):
    if not os.path.exists(_p):
        sys.exit(f"Missing generated file: {_p}\n  Generate with: {_how}\n"
                 f"  See docs/PIR03-C2/GENERATED_FILES.md")

# pyaging clock -> (M1 clock_id, variant). GrimAge V1 = pyaging 'grimage'.
CLOCKS = {
    "horvath2013": ("Horvath1", "original"), "pchorvath2013": ("Horvath1", "PC"),
    "hannum":      ("Hannum",   "original"), "pchannum":      ("Hannum",   "PC"),
    "dnamphenoage": ("PhenoAge", "original"), "pcphenoage":   ("PhenoAge", "PC"),  # DNAm Levine (513 CpG), NOT clinical 'phenoage'
    "grimage":     ("GrimAge",  "original"), "pcgrimage":     ("GrimAge",  "PC"),
}

# --- load betas as samples x CpGs (methylCIPHER file is CpGs x samples) ---
betas = pd.read_csv(betas_csv, index_col=0)
if any(str(i).startswith("cg") for i in betas.index[:5]):
    betas = betas.T                      # -> rows = samples, cols = CpGs
betas.index = betas.index.astype(str)
print(f"betas: {betas.shape[0]} samples x {betas.shape[1]} CpGs", flush=True)

pheno = pd.read_csv(pheno_csv, dtype={"sample_id": str}).set_index("sample_id")
pheno = pheno.reindex(betas.index)

# --- GrimAge reads Female/Age as the LAST TWO *features* (x[:,-2], x[:,-1]),
#     named 'female' and 'age' in model.features — so they must be COLUMNS of the
#     betas matrix, NOT adata.obs. Add them before building the AnnData. ---
betas["female"] = pheno["female"].astype(int).values
betas["age"] = pheno["age"].astype(float).values
adata = pya.pp.df_to_adata(betas, verbose=False)

# --- predict all 8 clocks (downloads weights on first use) ---
pya.pred.predict_age(adata, list(CLOCKS.keys()), verbose=False)

# pyaging writes one obs column per clock (name may be exact or lowercased)
def col_for(clock):
    for c in (clock, clock.lower(), clock.upper()):
        if c in adata.obs.columns:
            return c
    hit = [c for c in adata.obs.columns if c.lower() == clock.lower()]
    return hit[0] if hit else None

pkg_version = pya.__version__
py_version = ".".join(map(str, sys.version_info[:3]))
rows = []
missing = []
for clock, (clock_id, variant) in CLOCKS.items():
    col = col_for(clock)
    if col is None:
        missing.append(clock); continue
    vals = pd.to_numeric(adata.obs[col], errors="coerce").values
    for sid, score in zip(betas.index, vals):
        rows.append(dict(
            sample_id=sid, clock_id=clock_id, variant=variant,
            score=float(score), unit="years",
            implementation="pyaging",
            repo_url="https://github.com/rsinghlab/pyaging",
            commit=f"pip-{pkg_version}",          # pyaging pins by pypi version, no per-run git commit
            r_version=f"python-{py_version}",      # runtime version (schema column reused)
            pkg_version=f"pyaging-{pkg_version}",
            clock_function=f"predict_age:{clock}",
            imputation="pyaging default (per-clock KNN/mean + gold-standard quantile norm)",
        ))
out = pd.DataFrame(rows, columns=["sample_id","clock_id","variant","score","unit",
    "implementation","repo_url","commit","r_version","pkg_version","clock_function","imputation"])
out.to_csv(outfn, index=False)
print(f"wrote {len(out)} rows to {outfn}", flush=True)
if missing:
    print("MISSING clocks (not scored):", missing, flush=True)
print("clocks scored:", [c for c in CLOCKS if c not in missing], flush=True)
