"""GSE55763 dataset-prep step 1: reconstruct the replicate design from the GEO
series matrix (no methylation data needed).

Reads the series matrix, identifies the 72 technical-replicate samples
(Sample_description = "Technical replicate group N, sample M."), reconstructs
36 subjects x 2 batches, and emits pheno.csv, map.csv, replicate_sample_ids.txt.

Usage:
    python parse_metadata.py GSE55763_series_matrix.txt.gz OUTDIR
"""
import gzip, csv, re, sys, os

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)

rows, char_rows = {}, []
with gzip.open(src, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        if not line.startswith("!Sample_"):
            continue
        parts = line.rstrip("\n").split("\t")
        vals = [p.strip().strip('"') for p in parts[1:]]
        if parts[0] == "!Sample_characteristics_ch1":
            char_rows.append(vals)
        else:
            rows[parts[0]] = vals

titles, gsms, descs = rows["!Sample_title"], rows["!Sample_geo_accession"], rows["!Sample_description"]
n = len(gsms)

def find_char(prefix):
    for cr in char_rows:
        if cr and cr[0].lower().startswith(prefix):
            return cr
    return [""] * n
gender_row, age_row = find_char("gender:"), find_char("age:")

def sentrix(t):
    m = re.search(r"([0-9]{8,}_R\d+C\d+)", t); return m.group(1) if m else t

pat = re.compile(r"Technical replicate group (\d+), sample (\d+)")
records = []
for i in range(n):
    m = pat.search(descs[i])
    if not m:
        continue
    g = gender_row[i].split(":", 1)[-1].strip() if i < len(gender_row) else ""
    a = age_row[i].split(":", 1)[-1].strip() if i < len(age_row) else ""
    records.append(dict(sample_id=sentrix(titles[i]), gsm=gsms[i], group=int(m.group(1)),
                        indiv=int(m.group(2)), gender=g, age=a,
                        female=1 if g.upper().startswith("F") else 0))
records.sort(key=lambda r: (r["indiv"], r["group"]))
print(f"replicate samples: {len(records)}  groups: {sorted(set(r['group'] for r in records))}"
      f"  individuals: {len(set(r['indiv'] for r in records))}")

with open(os.path.join(outdir, "pheno.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["sample_id","age","female","gsm","group","individual","gender"])
    for r in records:
        w.writerow([r["sample_id"], r["age"], r["female"], r["gsm"], r["group"], r["indiv"], r["gender"]])

pairs = {}
with open(os.path.join(outdir, "map.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["subject","sample_id"])
    for r in records:
        subj = f"indiv_{r['indiv']:02d}"
        w.writerow([subj, r["sample_id"]]); pairs.setdefault(subj, []).append(r["sample_id"])

bad = {k: v for k, v in pairs.items() if len(v) != 2}
print(f"subjects: {len(pairs)} | malformed (not exactly 2 measurements): {len(bad)}")
with open(os.path.join(outdir, "replicate_sample_ids.txt"), "w") as f:
    f.write("\n".join(r["sample_id"] for r in records) + "\n")
print(f"wrote pheno.csv, map.csv, replicate_sample_ids.txt to {outdir}")
