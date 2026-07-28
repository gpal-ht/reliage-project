"""Single source of truth for the pipeline's GENERATED files + hard input guards.

Nothing under ``generated/`` is committed (see ``data/DATASETS.md``): every such file
is a build output that may be **absent on a fresh clone** or left half-written by a
failed step. So any code that *reads* one must fail loudly and helpfully, never with a
bare ``FileNotFoundError`` or a cryptic pandas ``KeyError``.

This module provides:

* ``MANIFEST`` - for every generated file: which step produces it, what it is, the
  columns it must have, and what it needs upstream.
* ``require_file`` / ``require_csv`` - guards that raise a clear, actionable message
  (naming the generating step + expected shape + a pointer to the debug doc) when a
  file is missing, empty, unreadable, or malformed.
* ``render_markdown`` - renders ``docs/PIR03-C2/GENERATED_FILES.md`` from ``MANIFEST``
  so the human debug guide can never drift from the guards. Run:
  ``python -m reliage.scoring.generated_manifest``  (writes/prints the doc).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DEBUG_DOC = "docs/PIR03-C2/GENERATED_FILES.md"


@dataclass(frozen=True)
class GenFile:
    key: str                       # logical id used by the guards
    path: str                      # canonical example path (GSE55763)
    stage: str                     # human-readable pipeline stage
    generated_by: str              # the exact command that produces it
    what: str                      # one-line description
    example: str                   # what a valid file looks like (header / shape)
    upstream: str = ""             # inputs it needs first
    columns: tuple = ()            # required columns (CSV); empty = existence-only
    match: tuple = ()              # basenames that resolve to this entry


# Ordered by pipeline stage. `columns` are checked only where the schema is stable
# (scores.csv is intentionally existence-only: it may be long OR wide form).
MANIFEST: tuple[GenFile, ...] = (
    GenFile(
        key="replicate_ids",
        path="generated/GSE55763/metadata/replicate_sample_ids.txt",
        stage="Stage 2 - reconstruct replicate design",
        generated_by="python tools/GSE55763/parse_metadata.py <series_matrix.txt.gz> generated/GSE55763/metadata",
        what="The 72 replicate Sentrix sample ids, one per line.",
        example="72 lines, e.g. `7786915023_R02C02`",
        upstream="the external GSE55763_series_matrix.txt.gz (source)",
        match=("replicate_sample_ids.txt",),
    ),
    GenFile(
        key="map",
        path="generated/GSE55763/metadata/map.csv",
        stage="Stage 2 - reconstruct replicate design",
        generated_by="python tools/GSE55763/parse_metadata.py <series_matrix.txt.gz> generated/GSE55763/metadata",
        what="Replicate map: which samples are repeats of the same subject.",
        example="header `subject,sample_id`; 72 rows (36 subjects x 2)",
        upstream="the external GSE55763_series_matrix.txt.gz (source)",
        columns=("subject", "sample_id"),
        match=("map.csv",),
    ),
    GenFile(
        key="pheno",
        path="generated/GSE55763/metadata/pheno.csv",
        stage="Stage 2 - reconstruct replicate design",
        generated_by="python tools/GSE55763/parse_metadata.py <series_matrix.txt.gz> generated/GSE55763/metadata",
        what="Per-sample phenotype (age + sex are required by GrimAge/PC).",
        example="header `sample_id,age,female,gsm,group,individual,gender`; 72 rows",
        upstream="the external GSE55763_series_matrix.txt.gz (source)",
        columns=("sample_id", "age", "female"),
        match=("pheno.csv",),
    ),
    GenFile(
        key="betas",
        path="generated/GSE55763/processed/betas.csv",
        stage="Stage 3 - extract the cohort",
        generated_by="bash tools/GSE55763/extract_betas.sh <replicate_sample_ids.txt> <path>/GSE55763_normalized_betas.txt.gz generated/GSE55763/processed/betas.csv",
        what="CpGs x 72 replicate-sample beta matrix (596 MB).",
        example="header `ID_REF` + 72 sample columns; ~473,864 CpG rows",
        upstream="the external GSE55763_normalized_betas.txt.gz (source) + replicate_sample_ids.txt",
        match=("betas.csv",),
    ),
    GenFile(
        key="scores",
        path="generated/GSE55763/processed/scores.csv",
        stage="Stage 4 - score (methylCIPHER / pyaging)",
        generated_by="Rscript reliage/scoring/score_methylCIPHER.R <betas.csv> <pheno.csv> generated/GSE55763/processed/scores.csv <PCClocks_data.qs2>",
        what="Versioned Score Table - one row per (sample, clock, variant), with provenance.",
        example="long form: `sample_id,clock_id,variant,score,unit,implementation,...` (576 rows) "
                "OR wide: `sample_id` + one column per clock label",
        upstream="betas.csv (Stage 3) + pheno.csv (Stage 2) + the external PC reference",
        match=("scores.csv", "scores_pyaging.csv", "scores_wide.csv"),
    ),
    GenFile(
        key="leaderboard",
        path="generated/GSE55763/out/leaderboard.csv",
        stage="Stage 6 - reliability analysis",
        generated_by="python -m reliage.scoring.run_analysis <scores.csv> <map.csv> --out generated/GSE55763/out",
        what="Per-clock ICC + within-subject error (SEM) + band.",
        example="columns include `clock,icc,ci_low,ci_high,band,sem,mean_abs_diff,mdc95`",
        upstream="scores.csv + map.csv",
        columns=("clock", "icc", "sem"),
        match=("leaderboard.csv",),
    ),
    GenFile(
        key="leaderboard_ageaccel",
        path="generated/GSE55763/out/leaderboard_ageaccel.csv",
        stage="Stage 7 - age-acceleration ICC",
        generated_by="python -m reliage.scoring.age_accel_icc <scores.csv> <map.csv> <pheno.csv> generated/GSE55763/out/leaderboard_ageaccel.csv",
        what="Age-acceleration ICC companion leaderboard.",
        example="same columns as leaderboard.csv",
        upstream="scores.csv + map.csv + pheno.csv",
        columns=("clock", "icc", "sem"),
        match=("leaderboard_ageaccel.csv",),
    ),
    GenFile(
        key="contrasts",
        path="generated/GSE55763/out/contrasts.csv",
        stage="Stage 6 - reliability analysis (primary endpoint)",
        generated_by="python -m reliage.scoring.run_analysis <scores.csv> <map.csv> --out generated/GSE55763/out",
        what="PC-vs-original within-subject variance ratio + paired-bootstrap CI.",
        example="columns `original,transformed,variance_ratio,ci_low,ci_high,verdict,n_subjects`",
        upstream="scores.csv + map.csv (needs the 4 original<->PC pairs present)",
        columns=("original", "transformed", "variance_ratio", "verdict"),
        match=("contrasts.csv",),
    ),
    GenFile(
        key="pair_diffs",
        path="generated/GSE55763/out/robustness/pair_diffs.csv",
        stage="Stage 8 - robustness",
        generated_by="python -m reliage.scoring.robustness <scores.csv> <map.csv> <pheno.csv> generated/GSE55763/out/robustness",
        what="Per-subject, per-clock batch1/batch2 replicate differences.",
        example="columns `clock,subject,batch1,batch2,signed,absdiff,pair_mean`",
        upstream="scores.csv + map.csv + pheno.csv",
        columns=("clock", "subject", "batch1", "batch2", "absdiff"),
        match=("pair_diffs.csv",),
    ),
    GenFile(
        key="compression_summary",
        path="generated/GSE55763/out/robustness/compression_summary.csv",
        stage="Stage 8 - robustness",
        generated_by="python -m reliage.scoring.robustness <scores.csv> <map.csv> <pheno.csv> generated/GSE55763/out/robustness",
        what="Per-pair signal-preservation vs noise-reduction summary.",
        example="columns include `pair,noise_ratio,signal_preservation_ratio`",
        upstream="scores.csv + map.csv + pheno.csv",
        columns=("pair", "noise_ratio", "signal_preservation_ratio"),
        match=("compression_summary.csv",),
    ),
    GenFile(
        key="loso",
        path="generated/GSE55763/out/robustness/loso.csv",
        stage="Stage 8 - robustness",
        generated_by="python -m reliage.scoring.robustness <scores.csv> <map.csv> <pheno.csv> generated/GSE55763/out/robustness",
        what="Leave-one-subject-out variance ratio / ICC per omitted subject.",
        example="columns include `pair,omitted,variance_ratio`",
        upstream="scores.csv + map.csv + pheno.csv",
        columns=("pair", "omitted", "variance_ratio"),
        match=("loso.csv",),
    ),
    GenFile(
        key="bland_altman",
        path="generated/GSE55763/out/robustness/bland_altman.csv",
        stage="Stage 8 - robustness",
        generated_by="python -m reliage.scoring.robustness <scores.csv> <map.csv> <pheno.csv> generated/GSE55763/out/robustness",
        what="Per-clock Bland-Altman bias + limits of agreement.",
        example="columns include `clock,batch_bias,sd_diff,loa_low,loa_high`",
        upstream="scores.csv + map.csv + pheno.csv",
        columns=("clock", "batch_bias", "sd_diff"),
        match=("bland_altman.csv",),
    ),
)

_BY_KEY = {g.key: g for g in MANIFEST}


class MissingGeneratedFile(FileNotFoundError):
    """A required generated file is absent (or empty)."""


class MalformedGeneratedFile(ValueError):
    """A generated file exists but is unreadable or missing required columns."""


def _resolve(path: str, key: str | None) -> GenFile | None:
    if key:
        return _BY_KEY.get(key)
    base = os.path.basename(path)
    for g in MANIFEST:
        if base in g.match or base == os.path.basename(g.path):
            return g
    return None


def _message(path: str, g: GenFile | None, problem: str) -> str:
    lines = [f"{problem}: {path!r}", ""]
    lines.append("Nothing under generated/ is committed - it is a local build area, so this "
                 "file must be produced by running the pipeline first.")
    if g is not None:
        lines += [
            "",
            f"  Stage         : {g.stage}",
            f"  Generated by  : {g.generated_by}",
            f"  What it is    : {g.what}",
            f"  Valid example : {g.example}",
        ]
        if g.columns:
            lines.append(f"  Required cols : {', '.join(g.columns)}")
        if g.upstream:
            lines.append(f"  Needs first   : {g.upstream}")
    lines += ["", f"Full generated-file map + rebuild order: {DEBUG_DOC}"]
    return "\n".join(lines)


def require_file(path: str, key: str | None = None) -> str:
    """Assert a generated file exists and is non-empty; else raise a clear error."""
    g = _resolve(path, key)
    if not os.path.exists(path):
        raise MissingGeneratedFile(_message(path, g, "Missing generated file"))
    if os.path.isdir(path):
        raise MalformedGeneratedFile(_message(path, g, "Expected a file but found a directory"))
    if os.path.getsize(path) == 0:
        raise MalformedGeneratedFile(_message(path, g, "Empty generated file"))
    return path


def require_csv(path: str, key: str | None = None):
    """Existence + readability + required-column check; returns the loaded DataFrame."""
    require_file(path, key)
    import pandas as pd
    g = _resolve(path, key)
    try:
        df = pd.read_csv(path)
    except Exception as e:  # noqa: BLE001 - re-raise as an actionable error
        raise MalformedGeneratedFile(_message(path, g, f"Unreadable CSV ({type(e).__name__}: {e})")) from e
    if df.empty:
        raise MalformedGeneratedFile(_message(path, g, "CSV has no data rows"))
    if g is not None and g.columns:
        have = {c.lower() for c in df.columns}
        missing = [c for c in g.columns if c.lower() not in have]
        if missing:
            problem = (f"Malformed CSV - missing required column(s) {missing}; "
                       f"found {list(df.columns)}")
            raise MalformedGeneratedFile(_message(path, g, problem))
    return df


def render_markdown() -> str:
    """Render the human debug guide from MANIFEST (single source of truth)."""
    out = [
        "# Generated files - debug & rebuild map",
        "",
        "> **Auto-generated from `reliage/scoring/generated_manifest.py`"
        " (`python -m reliage.scoring.generated_manifest`). Do not edit by hand.**",
        "",
        "Nothing under `generated/` is committed - it is a local, regenerable build area "
        "(see [`../../data/DATASETS.md`](../../data/DATASETS.md)). On a fresh clone it is "
        "empty; you rebuild it from the external dataset source. If a step errors with "
        "*\"Missing/Malformed generated file\"*, find the file below: it tells you which "
        "step produces it, what it should look like, and what it needs first.",
        "",
        "The reader code enforces this via `reliage.scoring.generated_manifest.require_csv` "
        "/ `require_file`, so a missing or malformed file fails with an actionable message "
        "instead of a raw traceback.",
        "",
        "## Rebuild order (each step's outputs feed the next)",
        "",
        "```",
        "external source ($LONGEVITY_DATA_ROOT/GSE55763/raw/, + series matrix + PC ref)",
        "   │  Stage 2  tools/GSE55763/parse_metadata.py   → metadata/ (map, pheno, replicate_sample_ids)",
        "   │  Stage 3  tools/GSE55763/extract_betas.sh    → processed/betas.csv",
        "   │  Stage 4  reliage/scoring/score_methylCIPHER.R → processed/scores.csv (Versioned Score Table)",
        "   │  Stage 6  reliage.scoring.run_analysis        → out/ (leaderboard, contrasts, ...)",
        "   │  Stage 7  reliage.scoring.age_accel_icc       → out/leaderboard_ageaccel.csv",
        "   │  Stage 8  reliage.scoring.robustness          → out/robustness/",
        "   ▼  Stage 9  reliage.scoring.figures             → out/figures/",
        "```",
        "",
        "## Files",
        "",
    ]
    for g in MANIFEST:
        out += [
            f"### `{g.path}`",
            "",
            f"- **Stage:** {g.stage}",
            f"- **What it is:** {g.what}",
            f"- **Generated by:** `{g.generated_by}`",
            f"- **Valid example:** {g.example}",
        ]
        if g.columns:
            out.append(f"- **Required columns:** `{', '.join(g.columns)}`")
        if g.upstream:
            out.append(f"- **Needs first:** {g.upstream}")
        out += ["- **If missing/malformed:** re-run the *Generated by* command above after "
                "ensuring *Needs first* exists.", ""]
    return "\n".join(out) + "\n"


def main() -> None:
    md = render_markdown()
    # Write next to the other PIR03-C2 docs when run from the repo root.
    target = DEBUG_DOC
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"wrote {target} ({len(MANIFEST)} generated files documented)")
    except OSError:
        print(md)


if __name__ == "__main__":
    main()
