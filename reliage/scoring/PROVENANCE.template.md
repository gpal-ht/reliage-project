# Score provenance (fill at run time — mandatory)

Copy per scoring run into the dataset's `metadata/`. No score is valid without this.

- dataset: ______________ (e.g. GSE55763 GEO rebuild | pcclocks_example)
- scorer: methylCIPHER (PRIMARY) | pyaging (SENSITIVITY)
- repository owner + URL: HigginsChenLab / https://github.com/HigginsChenLab/methylCIPHER
- **exact commit hash:** ______________ (`git rev-parse HEAD`)
- R version: ______________
- package versions: methylCIPHER ______  + key deps ______
- clocks + functions: Horvath1(calcHorvath1), Hannum(calcHannum), PhenoAge(calcPhenoAge),
  GrimAge(calcGrimAgeV2 — PIN V1/V2), PC via calcPCClocks (PC reference object: ______)
- preprocessing / normalization: ______________
- imputation policy: ______________ (methylCIPHER default: none)
- required CpG coverage + **% present for this dataset** (per clock): ______________
- transformation + output unit: ______________ (years; DunedinPACE = years/year; DNAmTL = kb)
- GrimAge phenotype inputs used (age, sex): ______________
- notes / known issues encountered: ______________
