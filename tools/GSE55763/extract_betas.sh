#!/usr/bin/env bash
# Stream the GSE55763 normalized-beta matrix and keep ONLY the 72 replicate
# beta columns (skip the paired "Detection Pval" columns). Output: CpGs in rows
# (ID_REF first col), 72 replicate samples in columns -> betas.csv.
#
# Integrity: pipefail surfaces any zcat truncation error; we also assert the
# output has 73 columns (ID_REF + 72) and a plausible CpG row count.
set -euo pipefail
IDS="$1"; GZ="$2"; OUT="$3"

# gzip integrity check first (definitive; catches a partial/corrupt download).
echo ">> gzip -t integrity check on $(basename "$GZ") ..."
gzip -t "$GZ" && echo "   integrity: OK"

echo ">> extracting 72 replicate beta columns ..."
set -o pipefail
zcat "$GZ" | awk -F'\t' -v OFS=',' -v idfile="$IDS" '
  BEGIN { while ((getline line < idfile) > 0) if (line != "") want[line]=1 }
  NR==1 {
    n=0; printf "ID_REF"
    for (i=2;i<=NF;i++){ h=$i; gsub(/\r/,"",h); if (h in want){ keep[++n]=i; printf ",%s", h } }
    printf "\n"
    if (n != 72) { print "FATAL: expected 72 beta columns, matched " n > "/dev/stderr"; exit 3 }
    print "   matched " n " beta columns" > "/dev/stderr"
    next
  }
  { cg=$1; gsub(/\r/,"",cg); printf "%s", cg
    for (j=1;j<=n;j++) printf ",%s", $(keep[j]); printf "\n" }
' > "$OUT"

rows=$(wc -l < "$OUT"); cols=$(head -1 "$OUT" | awk -F',' '{print NF}')
echo "   wrote $rows lines (incl header), $cols columns -> $OUT"
if [ "$cols" -ne 73 ]; then echo "FATAL: expected 73 cols, got $cols"; exit 4; fi
if [ "$rows" -lt 400000 ]; then echo "FATAL: only $rows rows — matrix looks truncated"; exit 5; fi
echo ">> extract OK"
