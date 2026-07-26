"""ICC-form sensitivity: report ICC(1,1) and ICC(3,1) alongside the primary ICC(2,1).

Protocol requires ICC(2,1) primary with ICC(1,1)/(3,1) as sensitivity. This confirms the
reliability conclusion (PC clocks 'excellent'; PC > original) is stable across ICC forms.
Runs on a frozen score table. ICC(2,1) counts systematic between-batch bias as error
(absolute agreement); ICC(3,1) excludes it (consistency); ICC(1,1) is one-way (no
occasion term). With small batch bias, (2,1) and (3,1) should be near-identical.

Usage:  python -m reliage.scoring.icc_sensitivity  scores.csv  map.csv  [out.csv]
"""
import sys, pandas as pd
from reliage.scoring.run_analysis import load_scores_wide, load_map
from reliage.benchmark import build_replicate_matrix
from reliage.icc import compute_icc, koo_li_band

scores_csv, map_csv = sys.argv[1], sys.argv[2]
out_csv = sys.argv[3] if len(sys.argv) > 3 else "datasets/GSE55763/out/icc_sensitivity.csv"
wide = load_scores_wide(scores_csv)
groups = load_map(map_csv)
labels = [c for c in wide.columns]

rows = []
for lab in labels:
    m = build_replicate_matrix(wide[lab], groups, k=2)
    rec = {"clock": lab}
    for form in ("ICC1", "ICC2", "ICC3"):
        r = compute_icc(m, form=form)
        rec[f"{form}"] = round(r.icc, 4)
        rec[f"{form}_lo"] = round(r.ci_low, 4)
        rec[f"{form}_hi"] = round(r.ci_high, 4)
        rec[f"{form}_band"] = koo_li_band(r.icc)
    rows.append(rec)
df = pd.DataFrame(rows).set_index("clock")
order = ["PCGrimAge","PCPhenoAge","PCHannum","PCHorvath1","GrimAge","Hannum","Horvath1","PhenoAge"]
df = df.reindex([c for c in order if c in df.index])
df.reset_index().to_csv(out_csv, index=False)

print("=== ICC by form (point estimate | Koo-Li band) ===")
print(f"{'clock':<12}{'ICC1':>8}{'ICC2(1)':>10}{'ICC3':>8}   bands(1/2/3)")
for c, r in df.iterrows():
    print(f"{c:<12}{r.ICC1:>8.3f}{r.ICC2:>10.3f}{r.ICC3:>8.3f}   {r.ICC1_band}/{r.ICC2_band}/{r.ICC3_band}")

pc = ["PCGrimAge","PCPhenoAge","PCHannum","PCHorvath1"]
pairs = [("Horvath1","PCHorvath1"),("Hannum","PCHannum"),("PhenoAge","PCPhenoAge"),("GrimAge","PCGrimAge")]
print("\n=== stability checks across forms ===")
for form in ("ICC1","ICC2","ICC3"):
    all_pc_excellent = all(df.loc[p, form] >= 0.90 for p in pc)
    pc_gt_orig = all(df.loc[t, form] > df.loc[o, form] for o, t in pairs)
    print(f"  {form}: all PC >= 0.90 (excellent)? {all_pc_excellent} | PC > original for all 4 pairs? {pc_gt_orig}")
max_spread = (df[["ICC1","ICC2","ICC3"]].max(axis=1) - df[["ICC1","ICC2","ICC3"]].min(axis=1)).max()
print(f"  max ICC spread across forms (any clock): {max_spread:.4f}")
print(f"wrote {out_csv}")
