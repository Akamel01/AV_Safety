---
name: run-statistical-validation
description: "Validate the statistical-validation skill — check validation framework (5 categories), goodness-of-fit tests, hypothesis tests, benchmarks, sensitivity analysis, and cross-references."
---

# Run: Statistical Validation Validator

Validates the statistical validation skill definition for test coverage and methodology correctness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/statistical-validation/.claude/skills/run-statistical-validation/driver.py
```

The driver outputs:
- Validation framework coverage (5 categories)
- Goodness-of-fit test completeness (KS, Shapiro-Wilk, chi-square)
- Hypothesis test coverage (z-test, chi-square, homogeneity)
- Benchmark database correctness
- Sensitivity analysis methods (OAT, Sobol)
- Validation report structure completeness
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Statistical Validation Validation ===
Validation categories: 5/5 ✓
Goodness-of-fit tests: 4/4 ✓ (KS, Shapiro-Wilk, Anderson-Darling, chi-square)
Hypothesis tests: 3/3 ✓ (z-test, chi-square severity, homogeneity)
Benchmarks: 10/10 ✓ (NHTSA, UK, Canada, TTC, braking, friction, etc.)
Sensitivity methods: 2/2 ✓ (OAT, Sobol)
Validation report: 6/6 sections ✓
Quality standards: ✓ (5 thresholds: alpha, sample, normality, variance, GOF)
Cross-references:
  bayesian-evt: ✓ (upstream)
  risk-quantification: ✓ (upstream)
  safety-thresholds: ✓ (upstream)
  data-ingest: ✓ (upstream)
  risk-metrics: ✓ (sibling)
  collision-modeling: ✓ (sibling)
Issues found: 0
```

## Direct invocation

```python
from driver import StatsValidator
validator = StatsValidator()
report = validator.validate()
print(report.summary)
```
