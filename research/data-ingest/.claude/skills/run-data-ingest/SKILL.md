---
name: run-data-ingest
description: "Validate the data-ingest skill — check data sources (USA/Canada/England), standard schemas, normalization rules, validation rules, and cross-references."
---

# Run: Data Ingestion Validator

Validates the data ingestion skill definition for data source coverage and schema completeness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/data-ingest/.claude/skills/run-data-ingest/driver.py
```

The driver outputs:
- Data source coverage by jurisdiction (USA, Canada, England)
- Standard schema completeness (crash record, vehicle record)
- Normalization rules correctness
- Validation rules coverage
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Data Ingestion Validation ===
Data sources: 12/12 ✓ (5 USA, 3 Canada, 4 England)
Crash record schema: ✓ (all required fields)
Vehicle record schema: ✓ (all required fields)
Normalization rules: ✓ (speed, jurisdiction, severity, conflict type)
Validation rules: ✓ (required, optional, location, vehicle, date, coord, speed, mass)
Quality metrics: ✓ (5 completeness thresholds)
Cross-references:
  scenario-taxonomy: ✓ (downstream)
  data-exploration: ✓ (downstream)
  bayesian-analysis: ✓ (downstream)
  risk-metrics: ✓ (downstream)
  statistical-validation: ✓ (sibling)
  standards-research: ✓ (sibling)
Issues found: 0
```

## Direct invocation

```python
from driver import DataIngestValidator
validator = DataIngestValidator()
report = validator.validate()
print(report.summary)
```
