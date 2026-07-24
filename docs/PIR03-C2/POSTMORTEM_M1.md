# POSTMORTEM — Milestone 001

A reflection written immediately after the first robustness-qualified GSE55763 result
(tag `v0.3.1-scientific-baseline`), while the details are fresh. Not a technical
document — a record of judgment: what worked, what was wrong, what nearly went wrong,
and what should become standard. Intended to be reused as a template for future
Foundry contribution candidates.

---

## What architectural decisions proved most valuable

1. **Scorer-agnostic design with the Versioned Score Table as the interface.** Because
   reliage consumes only a score table + replicate map — never betas or clock formulas —
   the scoring engine (methylCIPHER) and the measurement engine (reliage) stayed cleanly
   separable. This is what makes the *next* experiment (pyaging) a drop-in second producer
   rather than a rewrite. The single most load-bearing decision.
2. **Provenance as a gate, not an afterthought.** Mandatory commit-pinning + per-run
   coverage forced us to confront the GrimAge V1-vs-V2 question instead of silently
   inheriting the script's default. Provenance discipline caught a *scientific* error, not
   just a bookkeeping one.
3. **Reporting ICC *with* absolute error (SEM, MDC95).** This looked like pedantry until
   the age-acceleration analysis: ICC dropped sharply while SEM and the variance ratio were
   invariant. Without the absolute-error columns we'd have misread a spread artifact as a
   change in reliability. The protocol rule paid for itself in one step.
4. **Explicit evidence / claim gates.** "No real-data result yet" stayed literally true
   through weeks of software work. The gates made it psychologically impossible to drift
   into believing we had a result before we did.
5. **Robustness designed as attempted refutation.** The compression audit, LOSO, outlier
   audit, and Bland–Altman were framed as "here is every way this could be an artifact,"
   not "here is more support." The claim was strengthened only after they failed to break it.

## Which early assumptions turned out wrong

- **The scorer was *not* ready.** `score_methylCIPHER.R` was written against an older
  methylCIPHER API — wrong argument names, `calcGrimAgeV2` instead of the manifest-locked
  V1, lowercase pheno columns. It would have errored on first contact. Assumption "the code
  is done" was false; the *installed package* was the ground truth, not the script.
- **The fast-path data source was dead.** The Yale Box example file
  (`Example_PCClock_Data.RData`) had been removed. We assumed a linked external artifact
  would persist; it did not. Pivoted to the canonical GEO route (which was the real target
  anyway).
- **The PC reference did not require the Box download.** We assumed the 2 GB
  `CalcAllPCClocks.RData` from Box was mandatory; methylCIPHER actually ships a no-auth
  Zenodo download path. Reading the package's own source changed the plan.
- **The betas were not perfectly complete.** 4 CpGs were NA across all samples, which
  `calcGrimAgeV1`'s `check_DNAm` rejects outright. Assumption "normalized betas are clean"
  needed a preprocessing step (drop all-NA → impute) that we hadn't planned.

## What nearly caused mistakes

- **Reviewing the wide convenience table as if it were the standard.** The canonical
  `scores.csv` was already long-form with per-row provenance and demographics separated; the
  wide view was a display convenience. A design critique nearly landed on the wrong artifact.
  Lesson: label derived views as derived, loudly.
- **A silently-truncating extractor.** The first extractor used `zcat 2>/dev/null`, which
  would have passed a *partial* 9.7 GB download through as if it were complete data. Hardened
  to `gzip -t` + row/column assertions before it ever ran on the real file. A quiet failure
  mode is worse than a loud one.
- **A point-estimate headline.** "87–96% reduction" are point estimates; the CI-bounded
  worst case is ~67% (Hannum). Caught in the review pass and qualified. Nearly published a
  number stronger than the interval supports.
- **Calling `cg00017157` an "outlier" prematurely.** It was flagged from a raw-matrix display,
  then established to be in *none* of the clock CpG sets — zero scoring impact. We nearly
  described a non-issue as a data-quality concern. Establish causal role before naming.
- **Git nearly committed the wrong things.** `git add -A` staged the embedded PC-Clocks
  clone and a stray empty tarball; and `.gitignore` would have *excluded* the milestone's own
  result artifacts. Both caught at commit time — but "decide the artifact-commit policy before
  the milestone" would have been cleaner than deciding it at `git add`.

## Which validation step caught the most issues

**Introspecting the installed package instead of trusting the script.** Reading
methylCIPHER's actual function signatures and source caught, in one sitting: the three API
mismatches, the correct GrimAge variant path, the Zenodo reference download, and the fact
that the bundled `exampleBetas` had no replicates (so it could smoke-test scoring but not
reliability). Runner-up: **provenance/manifest discipline** (GrimAge V1). The scientifically
decisive step was different from the correctness-decisive one — the **compression audit** is
what turned "more repeatable" into "selective denoising," the actual contribution.

## What we would do differently from day one

1. **Verify the scorer against the installed package API before assuming it runs.** Treat the
   dependency, not the committed script, as ground truth.
2. **Check external data-source liveness early.** Linked artifacts rot; confirm before building
   a plan around them.
3. **Resolve every "PIN X vs Y" TODO before the first run.** The V1/V2 ambiguity sat open far
   too long.
4. **Ship extractors with integrity assertions in v1**, never a `2>/dev/null` streaming path.
5. **Fix the canonical-vs-derived artifact distinction up front**, so reviews target the right
   object.
6. **Write the git artifact policy** (what results are committed, what stays regenerable) before
   the milestone commit, not during it.

## What should become standard for every future Foundry project

The workflow itself — this is the reusable asset, more than any single script:

```
Question
  → Protocol locked BEFORE results
  → Locked, commit-pinned implementation
  → Versioned intermediate artifact (the interface between engines)
  → Primary analysis (prespecified endpoint)
  → Robustness analyses designed as attempted REFUTATIONS
  → Technical report with calibrated claims + explicit limits
  → Immutable milestone freeze (tag; editorial fixes go on top, never into it)
  → Follow-up experiments as NEW questions, not checkboxes
```

Plus the habits that made it trustworthy:
- **Evidence layers** kept distinct: software (engine verified) · statistical (robustness) ·
  scientific (dataset). A claim is only as strong as its weakest layer.
- **Believe the result only after trying to disprove it.** The robustness section is a list
  of failed refutations; the claim is what survived.
- **Calibrated language with a Remaining-Uncertainties table** — state what was *not* achieved.
- **Two independent engines** joined by a versioned, provenance-carrying artifact.

## How M1 reframed the project

The question evolved without our noticing:
`Can we reproduce Higgins-Chen?` → `Can we build an open benchmark?` →
**`Can we independently evaluate measurement reliability for any biomarker?`**
The Higgins-Chen comparison became *Calibration Experiment #1*, not the project. The durable
contribution is the reproducible workflow, not the 87–96% number. If another lab can run this
same apparatus on a different biomarker or scorer and get a reviewable measurement assessment,
reliage has done something more lasting than reproducing one finding.

---
*Next chapter: Experiment E2 — Implementation Sensitivity (methylCIPHER vs pyaging), a new
scientific question with its own protocol and report.*
