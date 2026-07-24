# reliage — Mission & Vision

## North Star

> **reliage is the open, reproducible metrology layer for aging biomarkers** —
> measurement science for biomarkers, starting with epigenetic clocks.

Every mature discipline has a metrology layer: physics has measurement science,
chemistry has analytical validation, diagnostics has assay validation. Longevity
research does not yet have a mature, open, reproducible one. reliage aims to be it.
That is a larger and more durable contribution than "another benchmarking tool."

**Do not rename the project now** (v1 is scoped to epigenetic clocks and ships as
"reliability"). But keep every abstraction **biomarker-agnostic**: nothing in reliage
is methylation-specific anymore — it operates on `scores + measurement design`, which
works unchanged for proteomic, transcriptomic, and metabolomic clocks. Guard that.

## The one-sentence product philosophy

Every output must answer exactly one of three questions:

| Question | Layer | reliage term |
|---|---|---|
| **How noisy is this?** | Measurement | Measurement **Capability** (repeatability, agreement, noise floor, calibration) |
| **Can I measure my effect?** | Detectability | Experimental detectability |
| **What should I use?** | Recommendation | Clock recommendation |

Everything else is implementation detail. (Renamed from "Measurement Characteristics"
to **Measurement Capability** — scientists care about capability: repeatability,
agreement, noise floor, detectability, calibration.)

## Roadmap — user-facing capabilities (not internal architecture)

```
v1  MEASUREMENT     how noisy is this?        <- reliability core (in progress)
v2  DETECTABILITY   can I measure my effect?  <- detectability + trial-design assistant
v3  RECOMMENDATION  what should I use?        <- multi-clock recommendation
```

**v1 Measurement** (finish first, in order): variance ratio + paired bootstrap ✅ →
process GSE55763 → first end-to-end report → validate vs published stats → freeze v1.

**v2 Detectability** — the sleeper flagship. Today it answers "can I detect 2 years?".
It naturally grows into a **trial-design assistant**:
```
expected effect + variance + n + design  →  power  →  recommendation
```
(v0.3.0 ships the measurement-noise *screen* — clearly NOT a power calculation yet;
a real trial decision needs biological variance, design, n, power, attrition, and
multiple-testing policy.)

**v3 Recommendation** — scientists ultimately ask *"which clock should I use?"*, not
"can GrimAge do it?". Expose:
```
Goal: detect a 1-year intervention  →  Use: PCGrimAge  →  Why: lowest MDC95
```
`recommend_for_effect` is the seed of this (ranks clocks, names which clear the noise
floor, or "none sufficient"); the full "why"-carrying, design-aware engine is v3.

## The v2 design invariant that future-proofs everything

Make the **measurement design** a first-class object so metrics are *selected by the
design*, never hardcoded to "technical replicate":

```
Experiment → Measurement Design → Applicable Capabilities
             (technical | biological | longitudinal | intervention | multi-site | multi-platform)
```

This makes the tool refuse category errors (never analyze a longitudinal design as if
within-person change were pure error; never call acute responsiveness "unreliability").
**v1 stays clean**; the cheap forward-compatible move now is to *tag every result with
its measurement design*. The window to protect this boundary is now — nothing is
scored yet, so no dataset has hardened the interfaces.

## Scope discipline (what reliage must NOT absorb)

reliage answers exactly one question well: **can this biomarker be trusted for this
measurement task?** Aging mechanisms, causality, and intervention biology stay
*separate projects that consume reliage's outputs* — never folded in. Deepen
measurement-science rigor (provenance, reproducibility, validation frameworks,
benchmark infrastructure — the real moat); do not widen into biology.
