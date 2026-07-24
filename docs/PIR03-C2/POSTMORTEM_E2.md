# POSTMORTEM — Experiment E2 (Implementation Sensitivity)

Reflection written immediately after E2. Outcome: **implementation-robust** — pyaging
reproduces the M1 conclusion (scores r ≥ 0.9997, identical ICC/VR ordering, same verdict),
with one benign GrimAge calibration offset. A "no divergence" result — and per the protocol,
that is as valuable as a "yes." The goal was truth, not confirmation; the truth here is
robustness.

## What worked

1. **The Versioned Score Table as an interface — vindicated.** pyaging emitted the *identical*
   long-form schema, and the entire reliage pipeline (`run_analysis`, `age_accel_icc`,
   `robustness`) ran on it **unchanged** — one output-path parameter was the only edit. Swapping
   the scoring engine really was a drop-in. This is the concrete payoff of the M1 scorer-agnostic
   architecture; E2 is its first real exercise.
2. **Protocol locked before results.** Prespecified concordance thresholds meant the verdict was
   pre-registered, not chosen to fit the numbers.
3. **Introspecting the installed package (M1's top lesson) caught both bugs.** Reading pyaging's
   catalog and `forward()` source — not its clock *names* — is what surfaced the clinical-vs-DNAm
   PhenoAge trap and the GrimAge feature-input contract.
4. **A known-relationship smoke test caught the biggest bug.** GrimAge should track chronological
   age; `r_age = 0.29` was the tripwire that exposed the age/female mis-wiring.

## Which early assumptions turned out wrong

- **pyaging `phenoage` is the CLINICAL PhenoAge** (blood chemistry), not the DNAm clock. The
  methylation Levine clock is `dnamphenoage`. Clock *name* ≠ clock *definition*.
- **GrimAge age/sex are FEATURES, not obs.** pyaging reads Female/Age as the last two columns of
  the feature matrix (`x[:,-2:]`), not from `adata.obs`. My obs assignment silently gave a
  constant age.
- **The Python environment would "just work."** pyaging requires Python < 3.14; the box had 3.14.
  Solved with an isolated 3.13 env via `uv` (no admin).

## What nearly caused mistakes

- **Nearly reported a false GrimAge "implementation divergence."** The first (buggy) run showed
  GrimAge `r_age = 0.29`, SPR 0.51 — a dramatic-looking divergence. It was *my* scorer bug, not
  pyaging's algorithm. Following the M1 rule ("establish causal role before concluding") turned a
  false finding into a fixed bug.
- **Nearly compared two different clocks** (clinical vs DNAm PhenoAge) — the 100%-missing-feature
  error stopped it.

## Which validation step caught the most

**Sanity-checking a known biological relationship** (clock vs chronological age) — the single
cheapest, highest-yield check. It caught the GrimAge bug that all the reliability metrics
(ICC/VR, which are age-independent) were *blind* to. Runner-up: feature-set inspection (CpG
counts/names), which caught the PhenoAge definition mismatch.

## What we would do differently from day one

1. **Read a scorer's full input contract before scoring** — which features, and *where* covariates
   (age/sex) are expected — not after an anomaly.
2. **Match clocks by feature set (CpG identity/count), never by name.** Names lie across tools.
3. **Add an automatic scorer smoke test:** every new scorer's age clocks must correlate with
   chronological age above a floor before its scores are trusted.

## Honest caveat this experiment surfaced

**PC-clock "independence" is partial.** pyaging's PC clocks and methylCIPHER's `calcPCClocks`
almost certainly share the same published Higgins-Chen PC coefficients, so their r ≈ 1.0 partly
reflects a shared upstream, not two independent re-implementations. The strongest independent
evidence is the **original** clocks (separately coded from public coefficients), which also agree
to r ≈ 1.0.

## What should become standard for future Foundry experiments

- Implementation-sensitivity studies are **dominated by clock-definition matching**, not by the
  algorithms. Budget effort accordingly; the scoring math, once matched, agrees almost exactly.
- Always include a **known-relationship smoke test** as a scorer gate.
- State **partial-independence caveats** explicitly (shared upstream references).
- The Versioned Score Table interface makes multi-scorer experiments cheap — this is the pattern
  to reuse for every future "does the conclusion depend on X?" question.

---
*E2 answers its question: the M1 conclusion does not depend on the scoring implementation
(within GSE55763). Next candidates — Tier-3 formal reference comparison, an independent
third-party rerun — remain separate steps before any v1.0 discussion.*
