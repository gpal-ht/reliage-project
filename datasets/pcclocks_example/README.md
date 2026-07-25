# pcclocks_example — Lehne technical-replicate subset (fast start, Tier 1)

> ⚠ **UNAVAILABLE / not used.** The example replicate data (`Example_PCClock_Data.RData`) lived on a
> Yale Box link that has been **removed**, and the PC-Clocks repo git-clone does **not** contain it.
> Milestone 001 therefore used the **GEO canonical path (`../GSE55763/`) directly** — this fast-path
> dataset was never used for the result. Retained only as historical context.

**Role (original intent):** debug/validation path. Fastest way to exercise the whole
pipeline before the full GEO rebuild. NOT full public reproduction — an intermediate
artifact prepared by the original PC-Clocks authors.

## Download source (dead)
`git clone --depth 1 https://github.com/MorganLevineLab/PC-Clocks.git`
→ `Example_PCClock_Data.RData` — **hosted on Yale Box, now removed; the git repo ships only scripts,
not this RData.** Repo is unmaintained and directs users to methylCIPHER.

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
