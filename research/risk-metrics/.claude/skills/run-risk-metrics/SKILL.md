---
name: run-risk-metrics
description: "Validate the risk-metrics skill — check metric formulas, citations, standard alignment, workflow steps, and cross-references."
---

# Run: Risk Metrics Validator

Validates the risk metrics skill definition for formula correctness and standard alignment.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/risk-metrics/.claude/skills/run-risk-metrics/driver.py
```

The driver outputs:
- Metric formula completeness (collision rate, SWR, TTC, critical event, per-scenario)
- Citation coverage for each metric
- Standard alignment (UL 4600, ISO 21448, ISO 26262)
- Workflow step completeness (5 steps)
- Output format compliance
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Risk Metrics Validation ===
Metrics: 5/5 ✓ (collision rate, SWR, TTC dist, critical event, per-scenario)
Metric citations: ✓ (NHTSA, ES-28, BANSYSE)
Standard alignment: ✓ (UL 4600, ISO 21448, ISO 26262)
Workflow steps: 5/5 ✓ (define, implement, test, validate, document)
Output format: ✓ (formula, inputs/outputs, citation, test coverage)
Rules: ✓ (citations, justifications, multi-source, limitations)
Cross-references:
  data-ingest: ✓ (upstream)
  indicator-computation: ✓ (upstream)
  bayesian-evt: ✓ (upstream)
  collision-modeling: ✓ (sibling)
  safety-thresholds: ✓ (sibling)
  risk-quantification: ✓ (downstream)
  standards-research: ✓ (upstream)
Issues found: 0
```

## Direct invocation

```python
from driver import RiskMetricsValidator
validator = RiskMetricsValidator()
report = validator.validate()
print(report.summary)
```
