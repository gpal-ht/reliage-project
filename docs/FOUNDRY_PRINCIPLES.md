# FOUNDRY_PRINCIPLES

The methodology that makes a Frontier Research Foundry contribution trustworthy — the
recurring lessons, extracted once so they need not be re-derived. These are cross-project.

**How to use this document.** Postmortems are no longer written from scratch for every
experiment. A new experiment records which principles it *reinforced*, *extended*, or (rarely)
*revised* — and any genuinely new lesson is added here as a numbered principle. The methodology
evolves; the lessons are not repeated.

---

## P1 — Lock the protocol before results
Freeze the question, hypothesis, primary endpoint, constants, and prespecified acceptance
criteria *before* producing any result. Prevents post-hoc rationalization; makes the verdict
pre-registered, not chosen to fit the numbers.
*Demonstrated:* M1 (PROTOCOL locked pre-results), E2 (comparison thresholds locked pre-scoring).

## P2 — Try to disprove a result before strengthening the claim
Treat robustness analyses as *attempted refutations*, not supporting evidence. Believe a result
only after it survives honest attempts to break it. When an anomaly appears, **establish its
causal role before concluding** — and sanity-check known relationships (e.g. an age clock must
track chronological age) as cheap tripwires.
*Demonstrated:* M1 (compression audit, LOSO, Bland–Altman, outliers — the claim is what survived).
E2 (the `r_age=0.29` tripwire exposed an integration bug that all age-independent metrics were
blind to; investigating instead of concluding turned a false "divergence" into a fixed bug).

## P3 — Match implementations by biological definition and required feature set, never by name
Across tools, a clock *name* is not a clock *definition*. Confirm the biological definition, the
exact input feature set, and where covariates are supplied — before comparing or scoring.
Implementation-sensitivity studies are dominated by *definition matching*, not by the algorithms;
once correctly matched, the math tends to agree almost exactly. Applies to methylation,
proteomic, transcriptomic, metabolomic, and imaging biomarkers alike.
*Demonstrated:* E2 (pyaging `phenoage` = clinical, not DNAm `dnamphenoage`; GrimAge reads
age/female as *features*, not `.obs`). Both would have created false replication failures.

## P4 — Separate software, statistical, and scientific evidence
A claim is only as strong as its weakest evidence layer. Keep them distinct: **software** (the
engine is correct — canonical validation), **statistical** (the effect survives refutation —
robustness), **scientific** (the effect exists in real data — the dataset result). Never let one
layer borrow another's confidence.
*Demonstrated:* M1 (evidence-layers table), and the CLAIMS ledger tracks them separately.

## P5 — Preserve immutable milestone snapshots
When a milestone is declared, freeze it at a tag. Editorial and follow-up work goes *on top of*
the tag, never into it. Future readers can always answer "what did we know when this milestone
was declared?" without ambiguity.
*Demonstrated:* M1 (`v0.3.1-scientific-baseline` frozen; review polish + postmortem + E2 all
committed after it, tag never moved).

## P6 — Record remaining uncertainties explicitly
State what a result does *not* establish as prominently as what it does. Bound every claim by its
scope (dataset, platform, design, entities). Maintain a living evidence ledger as the canonical
scientific state.
*Demonstrated:* M1 (Remaining-Uncertainties table), E2 (partial-independence caveat for PC
clocks), and `CLAIMS.md` (the project's scientific-state ledger).

---

*These principles emerged from PIR03-C2 (reliage), Milestone 001 and Experiment E2, but are
intended to govern every Foundry contribution. The scientific state of any project lives in its
`CLAIMS.md`; the methodology that produced it lives here.*
