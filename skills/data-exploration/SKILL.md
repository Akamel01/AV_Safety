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

## Key EDA Findings to Document
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

## File Structure
```
src/data_exploration/
├── eda_engine.py        Main EDA orchestrator
├── summary_stats.py     Descriptive statistics
├── distributions.py     Distribution analysis (histograms, KDE, CDF)
├── correlations.py      Feature correlation analysis
├── segmentation.py      Data segmentation by type/jurisdiction/severity
├── visualization.py     Plotting functions
├── notebooks/           Jupyter notebooks for exploratory analysis
│   ├── 01_overview.ipynb
│   ├── 02_conflict_analysis.ipynb
│   ├── 03_jurisdiction_comparison.ipynb
│   └── 04_severity_analysis.ipynb
└── reports/             Generated EDA reports
    ├── summary.md
    └── figures/
```
