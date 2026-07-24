# pcclocks_example — Lehne technical-replicate subset (fast start, Tier 1)

**Role:** debug/validation path (Milestone 2). Fastest way to exercise the whole
pipeline before the full GEO rebuild. NOT full public reproduction — this is an
intermediate artifact prepared by the original PC-Clocks authors.

## Download source
`git clone --depth 1 https://github.com/MorganLevineLab/PC-Clocks.git`
→ `Example_PCClock_Data.RData` (the Lehne 2015 technical-replicate subset).
(Repo is unmaintained; it directs users to methylCIPHER. Treat this file as a
bootstrap convenience, not the canonical long-term input.)

## Layout
- `raw/` — the `.RData` as downloaded.
- `processed/` — beta matrix (samples × CpGs) + scores.csv after clock scoring.
- `metadata/` — replicate map (subject → [sample ids]); provenance notes.

## Preprocessing requirements
Extract the beta matrix + sample annotation from the RData; confirm which samples
are the technical replicates and how they pair.

## Replicate mapping requirements
Duplicate pairs → `subject → [rep_a, rep_b]`. Verify each replicate maps to exactly
one subject (VAL-PAIRING / VAL-DATA-AUDIT).

## Known issues
- Prepared by the original team → provenance is not independent (cross-check against
  the GEO rebuild in `../GSE55763/`).
- Exact preprocessing/normalization behind the file must be documented before any
  reproduction claim.
