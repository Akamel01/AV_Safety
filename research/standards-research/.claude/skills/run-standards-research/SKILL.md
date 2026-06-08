---
name: run-standards-research
description: "Validate the standards-research skill — check standards framework (UL 4600, ISO 21448, ISO 26262, etc.), cross-referencing matrix, compliance mapping, and cross-references."
---

# Run: Standards Research Validator

Validates the standards research skill definition for standards coverage and cross-referencing.

## Prerequisites

```bash
# No Python dependencies needed for standards research validation
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/standards-research/.claude/skills/run-standards-research/driver.py
```

The driver outputs:
- Standards framework completeness (UL 4600, ISO 21448, ISO 26262, ISO 21002, NHTSA, TC, DfT)
- Cross-referencing matrix coverage
- Compliance mapping methodology
- Workflow step completeness
- Output format compliance
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Standards Research Validation ===
Standards covered: 7/7 ✓ (UL 4600, ISO 21448, ISO 26262, ISO 21002, NHTSA, TC, DfT)
Cross-ref matrix: ✓ (5 requirements × 5 standards)
Compliance mapping: ✓ (4-step process)
Workflow: 5/5 steps ✓ (identify, extract, cross-ref, document, update)
Output format: ✓ (standards-analysis.md with clauses, metrics, jurisdiction)
Cross-references:
  safety-thresholds: ✓ (sibling)
  risk-metrics: ✓ (sibling)
  data-ingest: ✓ (upstream)
  portfolio-deploy: ✓ (downstream)
Issues found: 0
```

## Direct invocation

```python
from driver import StandardsValidator
validator = StandardsValidator()
report = validator.validate()
print(report.summary)
```
