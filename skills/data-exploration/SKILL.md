---
name: data-exploration
description: "Perform exploratory data analysis on collision risk datasets to identify patterns, distributions, and insights relevant to AV safety."
---

# Data Exploration

Perform exploratory data analysis (EDA) on collision risk datasets to identify patterns, distributions, and insights relevant to AV safety.

## EDA Pipeline

```
Cleaned Data
  ↓ Summary Stats (descriptive statistics)
  ↓ Distribution Analysis (histograms, KDE, CDFs)
  ↓ Correlation Analysis (feature relationships)
  ↓ Segmentation (by conflict type, jurisdiction, severity)
  ↓ Visualization (publication-quality plots)
  ↓ Report (markdown + notebooks)
```

## Analysis Categories

### Summary Statistics
- Per-column: count, mean, median, std, min, max, q25, q75, skewness, kurtosis
- Grouped by conflict type
- Grouped by jurisdiction
- Grouped by severity level

### Distribution Analysis
- Candidate distributions: norm, lognorm, gamma, weibull_min
- Fit via MLE, compare via KS test + AIC
- **Critical: GPD fitting for extreme TTC values (< 3.0s)**
- Speed distributions across jurisdictions × vehicle types
- TTC distribution with GPD tail fit

### Correlation Analysis
- Pearson and Spearman correlation matrices
- Strong correlations identified (|r| ≥ 0.5)
- Conflict-specific correlations with collision occurrence
- Feature importance ranking

### Segmentation
- By conflict type: count, collision rate, severity distribution, speed/gap stats
- By jurisdiction: conflict type distribution, collision rate, speed/gap stats
- By severity: count, percentage, conflict type/jurisdiction distribution

### Visualization
- Conflict type bar chart
- Speed histograms (with KDE, faceted by jurisdiction/conflict type)
- TTC histogram with GPD fit
- Jurisdiction comparison bar chart
- Correlation heatmap (triangular mask)
- Multi-panel figures for EDA report

## Cross-Skill Dependencies

- **data-ingest** (upstream) — outputs cleaned dataset that data-exploration ingests
- **bayesian-analysis** (downstream) — EDA informs prior elicitation and model design
- **risk-metrics** (downstream) — EDA findings drive metric selection and validation
- **scenario-taxonomy** — conflict type segmentation uses taxonomy definitions
- **stochastic-simulation** — EDA distributions drive Monte Carlo sampling parameters
1. Dominant conflict types and their relative frequencies
2. Speed distributions by jurisdiction and vehicle type
3. TTC distribution characteristics (mean, median, tail behavior)
4. Strong feature correlations with collision likelihood
5. Jurisdictional differences in conflict patterns
6. Severity distributions and their drivers

## Validation Requirements

### Completeness
- All conflict types analyzed individually
- All jurisdictions compared
- All severity levels documented
- All numeric features summarized

### Reproducibility
- All random operations use fixed seed (42)
- All packages and versions documented
- Original data preserved, transformations logged

### Quality
- No missing data in critical fields (crash_id, date, jurisdiction)
- Outliers identified and documented
- Inconsistencies flagged and addressed
- Statistical tests reported (p-values, confidence intervals)

## Reuse Trigger

Use when:
- Starting analysis of any collision risk dataset
- Validating data quality before modeling
- Identifying patterns for feature engineering
- Generating EDA reports for portfolio

## Expected Data Schema (input from data-ingest)

Required columns in input DataFrame:
- `crash_id`, `date`, `jurisdiction` — always required (no missing values)
- `conflict_type` — from scenario-taxonomy taxonomy (one of 8 types)
- `severity_level` — benign/moderate/extreme
- `speed_ms`, `gap_distance_m`, `TTC_s` — numeric features
- `collision` — binary indicator (0/1)

## Data Availability

Data directories are currently empty (not yet populated):
- `data/raw/` — raw crash datasets (FARS, CISS, CMFwiki, etc.)
- `data/processed/` — cleaned/normalized datasets for EDA

EDA pipelines execute against whatever data is available in `data/processed/`.
