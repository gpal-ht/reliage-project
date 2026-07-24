"""Intraclass correlation coefficient (ICC) engine.

This is the verified numerical core of ``reliage``. Test-retest reliability of an
epigenetic clock is quantified by the ICC of the clock's age estimate across
repeated measurements of the *same* biological sample. Higgins-Chen et al.
(Nature Aging, 2022) and the TranslAGE reliability work (bioRxiv, 2025) both
report clock reliability as ICCs following the reporting guidance of
Koo & Li (2016).

We implement the three single-measurement ICC forms of Shrout & Fleiss (1979),
computed from a two-way ANOVA decomposition (McGraw & Wong, 1996):

    ICC(1,1) : one-way random effects, absolute agreement, single measurement.
    ICC(2,1) : two-way random effects, absolute agreement, single measurement.
    ICC(3,1) : two-way mixed effects, consistency, single measurement.

For test-retest reliability of a clock the appropriate default is **ICC(2,1)**
(absolute agreement, two-way random): we care whether repeat measurements
*agree in value*, not merely correlate, and both the sample and the measurement
occasion are treated as random.

Correctness is pinned by ``tests/test_icc.py`` against the canonical worked
example in Shrout & Fleiss (1979), whose published values are
ICC(1,1)=0.17, ICC(2,1)=0.29, ICC(3,1)=0.71.

References
----------
Shrout PE, Fleiss JL. Intraclass correlations: uses in assessing rater
    reliability. Psychol Bull. 1979;86(2):420-428.
McGraw KO, Wong SP. Forming inferences about some intraclass correlation
    coefficients. Psychol Methods. 1996;1(1):30-46.
Koo TK, Li MY. A guideline of selecting and reporting intraclass correlation
    coefficients for reliability research. J Chiropr Med. 2016;15(2):155-163.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import stats

ICCForm = Literal["ICC1", "ICC2", "ICC3"]

# Qualitative reliability bands from Koo & Li (2016), used for reporting only.
_KOO_LI_BANDS = (
    (0.90, "excellent"),
    (0.75, "good"),
    (0.50, "moderate"),
    (0.00, "poor"),
)


def koo_li_band(icc: float) -> str:
    """Return the Koo & Li (2016) qualitative reliability label for an ICC."""
    if icc is None or np.isnan(icc):
        return "undefined"
    for threshold, label in _KOO_LI_BANDS:
        if icc >= threshold:
            return label
    return "poor"


@dataclass(frozen=True)
class ICCResult:
    """Result of an ICC computation.

    Attributes
    ----------
    form:
        Which ICC form was computed (``"ICC1"``, ``"ICC2"`` or ``"ICC3"``).
    icc:
        The point estimate.
    ci_low, ci_high:
        Bounds of the ``confidence``-level confidence interval (F-distribution
        based, McGraw & Wong 1996). ``nan`` if a CI is not available.
    confidence:
        Nominal coverage of the interval (e.g. 0.95).
    n_subjects:
        Number of subjects (rows) used.
    n_measurements:
        Number of repeated measurements per subject (columns / k).
    sem:
        Standard error of measurement = within-subject SD = sqrt(MSE), in the
        clock's own units (years for an age clock). This is the "within-subject
        error": measure one sample twice and the two readings differ by ~this
        much from noise alone.
    band:
        Koo & Li (2016) qualitative label for ``icc``.
    """

    form: ICCForm
    icc: float
    ci_low: float
    ci_high: float
    confidence: float
    n_subjects: int
    n_measurements: int
    sem: float = float("nan")

    @property
    def band(self) -> str:
        return koo_li_band(self.icc)

    @property
    def mdc95(self) -> float:
        """Smallest detectable change for one individual (95%), in clock units.

        A single person's clock value must change by more than this to be
        distinguishable from measurement noise: MDC95 = 1.96 * sqrt(2) * SEM.
        """
        return smallest_detectable_change(self.sem, confidence=0.95)


def smallest_detectable_change(sem: float, confidence: float = 0.95) -> float:
    """Individual-level smallest detectable change (a.k.a. MDC / SDC).

    For a single subject measured at two times, the change must exceed
    ``z * sqrt(2) * sem`` to exceed measurement noise at the given confidence.
    Assumption-light (no sample size needed); the headline "minimum detectable
    effect per clock" for the leaderboard.
    """
    if sem is None or np.isnan(sem):
        return float("nan")
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    return float(z * np.sqrt(2) * sem)


def min_detectable_effect(sem: float, n: int, power: float = 0.80,
                          alpha: float = 0.05, paired: bool = True) -> float:
    """Study-level minimum detectable effect on the MEAN change, in clock units.

    For a trial that measures each of ``n`` participants before and after, the
    smallest true mean change detectable with the given power:
    ``(z_{1-alpha/2} + z_{power}) * sem * sqrt(2/n)`` (paired). Reported on
    request; the leaderboard defaults to the assumption-light individual MDC.
    """
    if sem is None or np.isnan(sem) or n < 2:
        return float("nan")
    za = stats.norm.ppf(1 - alpha / 2)
    zb = stats.norm.ppf(power)
    factor = np.sqrt(2.0 / n) if paired else 2.0 / np.sqrt(n)
    return float((za + zb) * sem * factor)


def _anova_mean_squares(data: np.ndarray):
    """Two-way ANOVA mean squares for an n x k matrix (subjects x measurements).

    Returns (MSR, MSC, MSE, MSW) where
        MSR = between-subjects (rows) mean square,
        MSC = between-measurements (columns) mean square,
        MSE = residual mean square (two-way),
        MSW = within-subjects mean square (one-way residual).
    """
    n, k = data.shape
    grand_mean = data.mean()
    row_means = data.mean(axis=1)
    col_means = data.mean(axis=0)

    # Sums of squares.
    ss_total = ((data - grand_mean) ** 2).sum()
    ss_rows = k * ((row_means - grand_mean) ** 2).sum()
    ss_cols = n * ((col_means - grand_mean) ** 2).sum()
    ss_error = ss_total - ss_rows - ss_cols        # two-way residual
    ss_within = ss_total - ss_rows                  # one-way within-subject

    msr = ss_rows / (n - 1)
    msc = ss_cols / (k - 1)
    mse = ss_error / ((n - 1) * (k - 1))
    msw = ss_within / (n * (k - 1))
    return msr, msc, mse, msw


def compute_icc(
    data,
    form: ICCForm = "ICC2",
    confidence: float = 0.95,
) -> ICCResult:
    """Compute a single-measurement ICC from a subjects x measurements matrix.

    Parameters
    ----------
    data:
        Array-like of shape ``(n_subjects, n_measurements)``. Row ``i`` holds
        the repeated clock estimates for subject ``i``. Must be a complete
        (non-missing) rectangular matrix with ``n_subjects >= 2`` and
        ``n_measurements >= 2``. Rows containing NaN must be dropped by the
        caller (see :func:`reliage.benchmark.build_replicate_matrix`).
    form:
        ``"ICC2"`` (default, absolute agreement, two-way random),
        ``"ICC1"`` (one-way random) or ``"ICC3"`` (consistency, two-way mixed).
    confidence:
        Confidence level for the returned interval.

    Returns
    -------
    ICCResult
    """
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"data must be 2-D (subjects x measurements); got shape {arr.shape}")
    if np.isnan(arr).any():
        raise ValueError("data contains NaN; drop incomplete subjects before calling compute_icc")
    n, k = arr.shape
    if n < 2 or k < 2:
        raise ValueError(f"need >=2 subjects and >=2 measurements; got n={n}, k={k}")

    msr, msc, mse, msw = _anova_mean_squares(arr)

    if form == "ICC1":
        denom = msr + (k - 1) * msw
        icc = (msr - msw) / denom if denom != 0 else np.nan
    elif form == "ICC2":
        denom = msr + (k - 1) * mse + (k / n) * (msc - mse)
        icc = (msr - mse) / denom if denom != 0 else np.nan
    elif form == "ICC3":
        denom = msr + (k - 1) * mse
        icc = (msr - mse) / denom if denom != 0 else np.nan
    else:
        raise ValueError(f"unknown ICC form {form!r}; expected 'ICC1', 'ICC2' or 'ICC3'")

    ci_low, ci_high = _icc_confidence_interval(
        form, msr, msc, mse, msw, n, k, confidence
    )
    # Within-subject error (SEM): random within-subject residual SD. Use the
    # two-way residual MSE (excludes systematic between-occasion drift) for
    # ICC2/ICC3; the one-way within-subject MSW for ICC1.
    resid = msw if form == "ICC1" else mse
    sem = float(np.sqrt(resid)) if resid > 0 else 0.0
    return ICCResult(
        form=form,
        icc=float(icc),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        confidence=confidence,
        n_subjects=n,
        n_measurements=k,
        sem=sem,
    )


def _icc_confidence_interval(form, msr, msc, mse, msw, n, k, confidence):
    """F-distribution confidence interval per McGraw & Wong (1996), Table 7."""
    alpha = 1.0 - confidence
    try:
        if form == "ICC1":
            f_val = msr / msw if msw != 0 else np.inf
            df1, df2 = n - 1, n * (k - 1)
            f_l = f_val / stats.f.ppf(1 - alpha / 2, df1, df2)
            f_u = f_val * stats.f.ppf(1 - alpha / 2, df2, df1)
            low = (f_l - 1) / (f_l + (k - 1))
            high = (f_u - 1) / (f_u + (k - 1))
        elif form == "ICC3":
            f_val = msr / mse if mse != 0 else np.inf
            df1, df2 = n - 1, (n - 1) * (k - 1)
            f_l = f_val / stats.f.ppf(1 - alpha / 2, df1, df2)
            f_u = f_val * stats.f.ppf(1 - alpha / 2, df2, df1)
            low = (f_l - 1) / (f_l + (k - 1))
            high = (f_u - 1) / (f_u + (k - 1))
        else:  # ICC2 absolute agreement (McGraw & Wong 1996)
            icc = (msr - mse) / (msr + (k - 1) * mse + (k / n) * (msc - mse))
            fj = stats.f.ppf(1 - alpha / 2, n - 1, (n - 1) * (k - 1))
            v_num = (k - 1) * (n - 1) * ((k * icc * (msc - mse) + n * (mse - icc * (
                msr + (k - 1) * mse + (k / n) * (msc - mse)))) ** 2)
            # Guard the Satterthwaite-style df against degenerate zero terms.
            a = (k * icc) / (n * (1 - icc)) if icc < 1 else np.inf
            b = 1 + (k * icc * (n - 1)) / (n * (1 - icc)) if icc < 1 else np.inf
            v = ((a * msc + b * mse) ** 2) / (
                (a * msc) ** 2 / (k - 1) + (b * mse) ** 2 / ((n - 1) * (k - 1))
            )
            f_low = stats.f.ppf(1 - alpha / 2, n - 1, v)
            f_high = stats.f.ppf(1 - alpha / 2, v, n - 1)
            low = (n * (msr - f_low * mse)) / (
                f_low * (k * msc + (k * n - k - n) * mse) + n * msr
            )
            high = (n * (f_high * msr - mse)) / (
                k * msc + (k * n - k - n) * mse + n * f_high * msr
            )
        low = float(np.clip(low, -1.0, 1.0))
        high = float(np.clip(high, -1.0, 1.0))
        if low > high:
            low, high = high, low
        return low, high
    except Exception:
        return float("nan"), float("nan")
