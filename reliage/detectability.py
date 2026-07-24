"""Experimental detectability — "reliable enough for WHAT?".

A scientist's first question is not "what is the ICC?" but "can this clock detect
MY effect?". Given a clock's within-subject error and an expected effect size, this
module answers that as a decision, and recommends which clocks (if any) can detect
a given effect. It is the first concrete step of reliage's decision-support layer:

    clock -> measurement characteristics (SEM) -> experimental detectability -> recommendation

Units matter: ``sem`` and ``effect`` must be in the SAME unit (years for an age
clock; PACE units for DunedinPACE). Never compare across units.

Two modes:
  individual - can a change in ONE person be told apart from measurement noise?
               threshold = MDC95 = 1.96*sqrt(2)*SEM; marginal down to MDC68.
  trial      - MEASUREMENT-NOISE DETECTABILITY SCREEN for a paired study of n.
               threshold = (z_alpha/2 + z_power) * SEM * sqrt(2/n).

IMPORTANT: trial mode is a *measurement-noise screen*, NOT a full power calculation.
It accounts only for the clock's technical error. A real trial decision must also
include biological/between-person variance, paired-vs-unpaired design, the true
sample size, confidence level, power target, attrition, and multiple-testing policy.
A "detectable" screen result means "not ruled out by measurement noise," never
"the trial is powered."
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .icc import min_detectable_effect

_SQRT2 = np.sqrt(2.0)
_SYMBOL = {"detectable": "✅", "marginal": "⚠️", "not_detectable": "❌", "unknown": "—"}


def _individual_thresholds(sem: float, alpha: float = 0.05):
    """(marginal_floor = MDC68, detectable_threshold = MDC95) for one individual."""
    z95 = stats.norm.ppf(1 - alpha / 2)
    z68 = stats.norm.ppf(1 - 0.32 / 2)          # ~1.0 (two-sided 68%)
    return z68 * _SQRT2 * sem, z95 * _SQRT2 * sem


def effect_detectable(sem: float, effect: float, mode: str = "individual",
                      n: int | None = None, power: float = 0.80, alpha: float = 0.05) -> dict:
    """Classify one (clock, effect) as detectable / marginal / not_detectable.

    Returns a dict with ``verdict``, ``threshold`` (the value the effect must reach
    to be 'detectable'), and ``marginal_floor``.
    """
    if sem is None or (isinstance(sem, float) and np.isnan(sem)) or effect is None:
        return {"verdict": "unknown", "threshold": float("nan"), "marginal_floor": float("nan")}
    if mode == "individual":
        marg, thr = _individual_thresholds(sem, alpha)
    elif mode == "trial":
        if n is None or n < 2:
            raise ValueError("trial mode requires n >= 2")
        thr = min_detectable_effect(sem, n, power=power, alpha=alpha)
        marg = 0.8 * thr
    else:
        raise ValueError("mode must be 'individual' or 'trial'")
    if effect >= thr:
        verdict = "detectable"
    elif effect >= marg:
        verdict = "marginal"
    else:
        verdict = "not_detectable"
    return {"verdict": verdict, "threshold": float(thr), "marginal_floor": float(marg)}


def detectability_table(clock_sems: dict, effect_sizes, mode: str = "individual",
                        n: int | None = None, power: float = 0.80, alpha: float = 0.05) -> pd.DataFrame:
    """Clock x effect-size detectability grid (long form).

    ``clock_sems`` maps clock name -> within-subject SD (SEM) in the clock's unit.
    """
    rows = []
    for clock, sem in clock_sems.items():
        for e in effect_sizes:
            r = effect_detectable(sem, e, mode=mode, n=n, power=power, alpha=alpha)
            rows.append({"clock": clock, "effect_size": e, "verdict": r["verdict"],
                         "symbol": _SYMBOL[r["verdict"]], "threshold": r["threshold"]})
    return pd.DataFrame(rows)


def recommend_for_effect(clock_sems: dict, expected_effect: float, mode: str = "individual",
                         n: int | None = None, power: float = 0.80, alpha: float = 0.05):
    """The signature decision: given an expected effect, which clocks can detect it?

    Returns (table, summary): ``table`` is one row per clock ranked best-first (lowest
    SEM), ``summary`` is a one-line scientific recommendation.
    """
    rows = []
    for clock, sem in clock_sems.items():
        r = effect_detectable(sem, expected_effect, mode=mode, n=n, power=power, alpha=alpha)
        rows.append({"clock": clock, "sem": sem, "expected_effect": expected_effect,
                     "verdict": r["verdict"], "symbol": _SYMBOL[r["verdict"]],
                     "threshold": r["threshold"]})
    table = pd.DataFrame(rows).sort_values("sem", na_position="last").reset_index(drop=True)
    screen = " (measurement-noise screen only — not a power calculation)" if mode == "trial" else ""
    detectable = table.loc[table["verdict"] == "detectable", "clock"].tolist()
    if detectable:
        summary = f"Not ruled out by measurement noise for: {', '.join(detectable)} (effect {expected_effect}){screen}"
    elif (table["verdict"] == "marginal").any():
        marg = table.loc[table["verdict"] == "marginal", "clock"].tolist()
        summary = (f"Marginal only ({', '.join(marg)}) — no clock's noise floor clears "
                   f"{expected_effect}; consider a larger n, a paired design, or a different endpoint{screen}")
    else:
        summary = f"No current clock is sufficiently reliable to detect an effect of {expected_effect}{screen}"
    return table, summary
