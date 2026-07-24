"""End-to-end reliage analysis runner (Milestone 3/4 scaffold).

Consumes a versioned score table + replicate map and produces the first
benchmark report: reliability leaderboard, paired PC-vs-original variance-ratio
contrasts (primary endpoint), and an experimental-detectability screen — plus a
comparison of the variance-ratio verdicts to the prespecified hypotheses.

Runs on ANY score table (methylCIPHER primary, or pyaging for the sensitivity
path) — reliage never needs the betas. Usable now on synthetic scores; on real
scores once scoring has run.

    python -m reliage.scoring.run_analysis scores.csv map.csv --out out/

score CSV: long form (sample_id, clock_id, variant, score[, unit,...]) or wide
           (sample_id + one column per clock label).
map CSV:   subject, sample_id.
"""

from __future__ import annotations

import argparse
import json
import os

import pandas as pd

from ..benchmark import run_reliability_benchmark
from ..contrast import run_paired_contrasts
from ..detectability import recommend_for_effect

# Protocol-locked pairs; wide-column labels use "<clock>" and "PC<clock>".
DEFAULT_PAIRS = [("Horvath1", "PCHorvath1"), ("Hannum", "PCHannum"),
                 ("PhenoAge", "PCPhenoAge"), ("GrimAge", "PCGrimAge")]


def load_scores_wide(scores_csv: str) -> pd.DataFrame:
    """Return a wide scores frame (index=sample_id, columns=clock labels)."""
    df = pd.read_csv(scores_csv)
    cols = {c.lower(): c for c in df.columns}
    if "clock_id" in cols and "score" in cols:      # long form -> pivot
        variant = cols.get("variant")
        label = (df[cols["clock_id"]] if variant is None
                 else [("PC" + c if v == "PC" else c)
                       for c, v in zip(df[cols["clock_id"]], df[variant])])
        df = df.assign(_label=label)
        wide = df.pivot_table(index=cols["sample_id"], columns="_label",
                              values=cols["score"], aggfunc="first")
        wide.index.name = "sample_id"
        return wide
    return df.set_index(cols.get("sample_id", df.columns[0]))


def load_map(map_csv: str) -> dict:
    m = pd.read_csv(map_csv)
    c = {x.lower(): x for x in m.columns}
    groups: dict[str, list[str]] = {}
    for subj, sid in zip(m[c["subject"]], m[c["sample_id"]]):
        groups.setdefault(str(subj), []).append(str(sid))
    return groups


def run(scores_csv: str, map_csv: str, out_dir: str,
        pairs=DEFAULT_PAIRS, effect_sizes=(1.0, 2.0, 5.0), n_boot: int = 2000):
    os.makedirs(out_dir, exist_ok=True)
    scores = load_scores_wide(scores_csv)
    groups = load_map(map_csv)

    # 1. Reliability leaderboard (all clocks present).
    clocks = [c for c in scores.columns]
    board = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
    board.frame.to_csv(os.path.join(out_dir, "leaderboard.csv"), index=False)

    # 2. Primary endpoint: paired PC-vs-original variance-ratio contrasts.
    usable_pairs = [(o, t) for (o, t) in pairs if o in scores.columns and t in scores.columns]
    contrasts = (run_paired_contrasts(scores, groups, usable_pairs, n_boot=n_boot)
                 if usable_pairs else pd.DataFrame())
    if not contrasts.empty:
        contrasts.to_csv(os.path.join(out_dir, "contrasts.csv"), index=False)

    # 3. Detectability screen (individual) using each clock's within-subject SD.
    sems = {r["clock"]: r["sem"] for _, r in board.frame.iterrows() if pd.notna(r["sem"])}
    detect = {}
    for e in effect_sizes:
        tbl, summary = recommend_for_effect(sems, e, mode="individual")
        detect[str(e)] = {"summary": summary, "table": tbl.to_dict(orient="records")}

    # 4. Verdict roll-up (primary endpoint).
    verdicts = contrasts["verdict"].value_counts().to_dict() if not contrasts.empty else {}
    n_improve = int((contrasts["variance_ratio"] < 1).sum()) if not contrasts.empty else 0
    joint = ("supported" if usable_pairs and n_improve == len(usable_pairs)
             else "partially_supported" if n_improve else "not_supported"
             if usable_pairs else "inconclusive")

    report = {
        "n_clocks": len(clocks),
        "n_pairs_evaluated": len(usable_pairs),
        "pairs_improving_direction": n_improve,
        "joint_primary_verdict": joint,
        "per_pair_verdicts": verdicts,
        "detectability": detect,
        "note": "Detectability is an individual measurement-noise screen, not a power calculation.",
    }
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(report, f, indent=2)

    md = [f"# reliage benchmark report",
          f"- clocks: {len(clocks)} | pairs evaluated: {len(usable_pairs)}",
          f"- joint primary verdict (PC reduces technical error): **{joint}** "
          f"({n_improve}/{len(usable_pairs)} pairs improve)", "",
          "## Reliability leaderboard", board.to_markdown(), "",
          "## Primary endpoint — variance ratio (PC/original), paired bootstrap CI"]
    if not contrasts.empty:
        md.append(contrasts.to_string(index=False))
    for e, d in detect.items():
        md.append(f"\n## Detectability screen — effect {e}\n{d['summary']}")
    with open(os.path.join(out_dir, "RESULTS.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser(description="reliage end-to-end analysis")
    ap.add_argument("scores_csv")
    ap.add_argument("map_csv")
    ap.add_argument("--out", default="reliage_out")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    rep = run(a.scores_csv, a.map_csv, a.out, n_boot=a.n_boot)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
