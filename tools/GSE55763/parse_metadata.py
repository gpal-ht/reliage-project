"""GSE55763 dataset-prep step 1: reconstruct the replicate design from the GEO
series matrix (no methylation data needed).

Reads the series matrix, identifies the 72 technical-replicate samples
(Sample_description = "Technical replicate group N, sample M."), reconstructs
36 subjects x 2 batches, and emits pheno.csv, map.csv, replicate_sample_ids.txt.

The series matrix is a SOURCE file (not committed); it lives in the external data
root, fetched by `bash data/download_data.sh gse55763` into
`$LONGEVITY_DATA_ROOT/GSE55763/raw/`. See docs/PIR03-C2/GENERATED_FILES.md.

Usage:
    python parse_metadata.py <GSE55763_series_matrix.txt.gz> <OUTDIR>
"""
import gzip, csv, re, sys, os

USAGE = ("usage: python tools/GSE55763/parse_metadata.py "
         "<GSE55763_series_matrix.txt.gz> <OUTDIR>")
EXPECT_SAMPLES, EXPECT_SUBJECTS = 72, 36

# --- guard: arguments ---------------------------------------------------------
if len(sys.argv) != 3:
    sys.exit(USAGE)
src, outdir = sys.argv[1], sys.argv[2]

# --- guard: the source series matrix must exist -------------------------------
if not os.path.exists(src):
    sys.exit(f"Series matrix not found: {src!r}\n"
             f"  It is a SOURCE file (not committed). Fetch it with:\n"
             f"    bash data/download_data.sh gse55763"
             f"   -> $LONGEVITY_DATA_ROOT/GSE55763/raw/GSE55763_series_matrix.txt.gz\n"
             f"  See docs/PIR03-C2/GENERATED_FILES.md")
os.makedirs(outdir, exist_ok=True)

# --- guard: it must be a readable gzip ----------------------------------------
rows, char_rows = {}, []
try:
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
except (OSError, EOFError) as e:
    sys.exit(f"Could not read {src!r} as gzip ({type(e).__name__}: {e}).\n"
             f"  Expected the gzipped GEO series matrix; re-download if truncated/corrupt.")

# --- guard: it must actually be a series matrix (has !Sample_* metadata) -------
need = ("!Sample_title", "!Sample_geo_accession", "!Sample_description")
missing = [k for k in need if k not in rows]
if missing:
    sys.exit(f"{src!r} is missing {missing} lines - is this the GSE55763 series matrix?\n"
             f"  (Expected GEO '!Sample_*' metadata lines; a beta matrix or a wrong file won't parse.)")

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

# --- guard: never write an empty / broken design silently ---------------------
pairs = {}
for r in records:
    pairs.setdefault(f"indiv_{r['indiv']:02d}", []).append(r["sample_id"])
if not records:
    sys.exit(f"Found 0 'Technical replicate group N, sample M' descriptions in {src!r}.\n"
             f"  This does not look like the GSE55763 series matrix (expected {EXPECT_SAMPLES} "
             f"replicate samples). Refusing to write empty metadata.")
bad = {k: v for k, v in pairs.items() if len(v) != 2}
if bad:
    sys.exit(f"Malformed replicate design: {len(bad)} subject(s) without exactly 2 measurements "
             f"(e.g. {list(bad)[:5]}). Refusing to write a broken map.csv/pheno.csv.")
if len(records) != EXPECT_SAMPLES or len(pairs) != EXPECT_SUBJECTS:
    print(f"WARNING: expected {EXPECT_SAMPLES} replicate samples / {EXPECT_SUBJECTS} subjects, "
          f"got {len(records)} / {len(pairs)} - proceeding, but verify this is GSE55763.",
          file=sys.stderr)

print(f"replicate samples: {len(records)}  groups: {sorted(set(r['group'] for r in records))}"
      f"  individuals: {len(pairs)}")

# --- write (validated) --------------------------------------------------------
with open(os.path.join(outdir, "pheno.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["sample_id","age","female","gsm","group","individual","gender"])
    for r in records:
        w.writerow([r["sample_id"], r["age"], r["female"], r["gsm"], r["group"], r["indiv"], r["gender"]])

with open(os.path.join(outdir, "map.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["subject","sample_id"])
    for r in records:
        w.writerow([f"indiv_{r['indiv']:02d}", r["sample_id"]])

with open(os.path.join(outdir, "replicate_sample_ids.txt"), "w") as f:
    f.write("\n".join(r["sample_id"] for r in records) + "\n")

print(f"subjects: {len(pairs)} | malformed (not exactly 2 measurements): {len(bad)}")
print(f"wrote pheno.csv, map.csv, replicate_sample_ids.txt to {outdir}")
