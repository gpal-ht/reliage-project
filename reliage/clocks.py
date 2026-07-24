"""Clock-score adapters.

``reliage`` is deliberately agnostic about *how* clock scores are produced — its
verified core only needs a scores table. This module provides optional adapters
so you can compute scores from a methylation beta matrix when you don't already
have them.

The primary adapter targets **ComputAgeBench** (the open Python accuracy
benchmark), so a single pipeline can report an accuracy score (from
ComputAgeBench) and a reliability score (from reliage) for the same open clocks.
ComputAgeBench is an *optional* dependency — importing this module never
requires it; the adapter imports lazily and raises a clear message if it's
absent.
"""

from __future__ import annotations

from typing import Callable

import pandas as pd


def linear_clock(coefficients: pd.Series, intercept: float = 0.0) -> Callable[[pd.DataFrame], pd.Series]:
    """Build a simple linear epigenetic clock callable.

    Most first/second-generation clocks are linear in CpG beta values:
    ``age_hat = intercept + sum_j w_j * beta_j``. Given the published
    coefficients this returns a callable usable directly as a clock in
    :func:`reliage.benchmark.score_samples`.

    Parameters
    ----------
    coefficients:
        Series of CpG weight indexed by CpG id.
    intercept:
        Clock intercept.

    Returns
    -------
    callable(betas: DataFrame) -> Series of scores indexed by sample id.
    Missing CpGs are treated as 0 contribution (documented limitation).
    """
    cpgs = coefficients.index

    def _score(betas: pd.DataFrame) -> pd.Series:
        shared = [c for c in cpgs if c in betas.columns]
        w = coefficients.loc[shared]
        return betas[shared].mul(w, axis=1).sum(axis=1) + intercept

    return _score


def computage_clock(model_name: str) -> Callable[[pd.DataFrame], pd.Series]:
    """Adapter that scores samples using a ComputAgeBench in-library clock.

    Lazily imports ``computage``. Raises a clear ImportError with install
    guidance if ComputAgeBench is not installed.

    Parameters
    ----------
    model_name:
        Name of an in-library ComputAgeBench model.

    Returns
    -------
    callable(betas) -> Series of scores.

    Notes
    -----
    This keeps the two open tools composable: the same clock that ComputAgeBench
    scores for *accuracy* is scored by reliage for *reliability*. The exact
    call surface of ComputAgeBench's model registry may evolve; this adapter is
    intentionally thin and is covered by an integration test that is skipped when
    ``computage`` is absent.
    """
    try:
        import computage  # noqa: F401
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "ComputAgeBench is not installed. Install with "
            "`pip install computage` to use computage_clock(); or supply "
            "precomputed scores and skip clock computation entirely."
        ) from exc

    def _score(betas: pd.DataFrame) -> pd.Series:  # pragma: no cover - needs computage
        from computage.models_library.registry import ModelsRegistry  # type: ignore

        model = ModelsRegistry.get(model_name)
        preds = model.predict(betas)
        return pd.Series(preds, index=betas.index, name=model_name)

    return _score
