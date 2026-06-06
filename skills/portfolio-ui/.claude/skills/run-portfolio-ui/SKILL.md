---
name: run-portfolio-ui
description: "Validate the portfolio-ui skill — check architecture (landing page, scenario selector, 3D/2D, indicators), state management, APIs, performance targets, and cross-references."
---

# Run: Portfolio UI Validator

Validates the portfolio UI skill definition for completeness and architecture correctness.

## Prerequisites

```bash
# Portfolio UI is HTML/JS/CSS — no Python dependencies needed
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/portfolio-ui/.claude/skills/run-portfolio-ui/driver.py
```

The driver outputs:
- Architecture completeness (landing page, scenario selector, visualization, indicators)
- State management correctness
- API coverage (risk computation, visualization, indicators)
- 8 conflict types coverage
- Performance targets assessment
- Optimization strategies completeness
- Testing checklist coverage
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Portfolio UI Validation ===
Architecture: ✓ (landing, scenario, visualization, indicators, risk, responsive)
State management: ✓ (portfolioState with all fields)
APIs: 3/3 ✓ (riskComputation, visualization, indicators)
Conflict types: 8/8 ✓
Performance targets: ✓ (5 targets: load, switch, MC, render, resize)
Optimizations: 6/6 ✓ (lazy load, pre-compute, progressive, workers, debounce, pagination)
Testing checklist: 11/11 items ✓
Cross-references:
  bayesian-evt: ✓ (depends on)
  3d-animation: ✓ (depends on)
  indicator-computation: ✓ (depends on)
  stochastic-simulation: ✓ (depends on)
  portfolio-deploy: ✓ (downstream)
  scenario-taxonomy: ✓ (data source)
Issues found: 0
```

## Direct invocation

```python
from driver import PortfolioUIValidator
validator = PortfolioUIValidator()
report = validator.validate()
print(report.summary)
```
