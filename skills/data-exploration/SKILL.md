# Skill: Data Exploration

**Purpose:** Perform exploratory data analysis (EDA) on collision risk datasets to identify patterns, distributions, and insights relevant to AV safety.

## 1. EDA Pipeline

### 1.1 Analysis Flow

```
Cleaned Data
    │
    ▼
┌──────────────┐
│  Summary Stats │  (descriptive statistics)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Distribution  │  (histograms, KDE, CDFs)
│  Analysis     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Correlation   │  (feature relationships)
│  Analysis     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Segmentation  │  (by conflict type, jurisdiction, severity)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Visualization │  (publication-quality plots)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Report        │  (markdown + notebooks)
└──────────────┘
```

### 1.2 File Structure

```
src/data_exploration/
├── __init__.py
├── eda_engine.py        — Main EDA orchestrator
├── summary_stats.py     — Descriptive statistics
├── distributions.py     — Distribution analysis (histograms, KDE, CDF)
├── correlations.py      — Feature correlation analysis
├── segmentation.py      — Data segmentation by conflict type, jurisdiction, severity
├── visualization.py     — Plotting functions
├── notebooks/           — Jupyter notebooks for exploratory analysis
│   ├── 01_overview.ipynb
│   ├── 02_conflict_analysis.ipynb
│   ├── 03_jurisdiction_comparison.ipynb
│   └── 04_severity_analysis.ipynb
└── reports/             — Generated EDA reports
    ├── summary.md
    └── figures/
```

## 2. Descriptive Statistics

### 2.1 Summary Statistics Module

```python
import numpy as np
import pandas as pd
from scipy import stats

class SummaryStatistics:
    def compute_overall_summary(self, df: pd.DataFrame, numeric_cols: List[str]) -> dict:
        """Compute overall descriptive statistics."""
        summary = {}
        for col in numeric_cols:
            vals = df[col].dropna()
            summary[col] = {
                "count": len(vals),
                "mean": vals.mean(),
                "median": vals.median(),
                "std": vals.std(),
                "min": vals.min(),
                "max": vals.max(),
                "q25": vals.quantile(0.25),
                "q75": vals.quantile(0.75),
                "skewness": stats.skew(vals),
                "kurtosis": stats.kurtosis(vals)
            }
        return summary
    
    def compute_by_conflict_type(self, df: pd.DataFrame, numeric_cols: List[str]) -> dict:
        """Compute summary statistics grouped by conflict type."""
        results = {}
        for ctype in df["conflict_type"].unique():
            subset = df[df["conflict_type"] == ctype]
            summary = {}
            for col in numeric_cols:
                vals = subset[col].dropna()
                summary[col] = {
                    "count": len(vals),
                    "mean": vals.mean(),
                    "median": vals.median(),
                    "std": vals.std(),
                    "q25": vals.quantile(0.25),
                    "q75": vals.quantile(0.75)
                }
            results[ctype] = summary
        return results
    
    def compute_by_jurisdiction(self, df: pd.DataFrame, numeric_cols: List[str]) -> dict:
        """Compute summary statistics grouped by jurisdiction."""
        results = {}
        for jur in df["jurisdiction"].unique():
            subset = df[df["jurisdiction"] == jur]
            summary = {}
            for col in numeric_cols:
                vals = subset[col].dropna()
                summary[col] = {
                    "count": len(vals),
                    "mean": vals.mean(),
                    "median": vals.median(),
                    "std": vals.std(),
                    "q25": vals.quantile(0.25),
                    "q75": vals.quantile(0.75)
                }
            results[jur] = summary
        return results
```

## 3. Distribution Analysis

### 3.1 Distribution Detection

```python
class DistributionAnalysis:
    def fit_distributions(self, data: np.ndarray, candidate_distributions: List[str]) -> dict:
        """Fit multiple distributions and select best fit."""
        results = {}
        for dist_name in candidate_distributions:
            try:
                dist = getattr(stats, dist_name)
                params = dist.fit(data)
                
                # KS test for goodness of fit
                ks_stat, ks_p = stats.kstest(data, dist_name, args=params)
                
                # AIC for model comparison
                log_likelihood = np.sum(dist.logpdf(data, *params))
                n_params = len(params)
                aic = 2 * n_params - 2 * log_likelihood
                
                results[dist_name] = {
                    "params": params,
                    "ks_stat": ks_stat,
                    "ks_pvalue": ks_p,
                    "aic": aic,
                    "llf": log_likelihood
                }
            except Exception as e:
                results[dist_name] = {"error": str(e)}
        
        # Select best fit by AIC
        valid = {k: v for k, v in results.items() if "error" not in v}
        if valid:
            best = min(valid.items(), key=lambda x: x[1]["aic"])
            results["best_fit"] = best
            results["best_dist"] = best[0]
        
        return results
    
    def analyze_speed_distributions(self, df: pd.DataFrame) -> dict:
        """Analyze speed distributions across jurisdictions and vehicle types."""
        results = {}
        
        for jur in df["jurisdiction"].unique():
            for vtype in df["vehicle_type"].unique():
                subset = df[(df["jurisdiction"] == jur) & (df["vehicle_type"] == vtype)]
                speeds = subset["speed_ms"].dropna().values
                
                if len(speeds) > 10:  # minimum sample size
                    fitted = self.fit_distributions(
                        speeds,
                        ["norm", "lognorm", "gamma", "weibull_min"]
                    )
                    key = f"{jur}_{vtype}"
                    results[key] = fitted
        
        return results
```

### 3.2 Critical Distribution Analysis for Collision Risk

```python
def analyze_ttc_distributions(df: pd.DataFrame) -> dict:
    """Analyze TTC distributions from simulated or real data."""
    results = {}
    
    for ctype in df["conflict_type"].unique():
        subset = df[df["conflict_type"] == ctype]
        ttc_vals = subset["TTC"].dropna().values
        
        if len(ttc_vals) > 50:
            # Fit GPD to extreme values (TTC < 3.0s)
            extreme_ttc = ttc_vals[ttc_vals < 3.0]
            if len(extreme_ttc) > 20:
                excesses = 3.0 - extreme_ttc  # positive excesses
                
                # Fit GPD
                from scipy.stats import gpd
                gpd_params = gpd.fit(excesses)
                
                results[ctype] = {
                    "n_extremes": len(extreme_ttc),
                    "gpd_params": {
                        "xi": gpd_params[0],
                        "mu": gpd_params[1],
                        "sigma": gpd_params[2]
                    },
                    "mean_TTC": np.mean(ttc_vals),
                    "median_TTC": np.median(ttc_vals),
                    "p5_TTC": np.percentile(ttc_vals, 5)
                }
    
    return results
```

## 4. Correlation Analysis

### 4.1 Feature Correlation Matrix

```python
def compute_correlation_matrix(df: pd.DataFrame, numeric_cols: List[str]) -> dict:
    """Compute Pearson and Spearman correlations."""
    subset = df[numeric_cols].dropna()
    
    pearson_corr = subset.corr(method="pearson")
    spearman_corr = subset.corr(method="spearman")
    
    return {
        "pearson": pearson_corr,
        "spearman": spearman_corr
    }

def identify_key_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.5) -> List[tuple]:
    """Identify strong correlations above threshold."""
    strong = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            r = corr_matrix.iloc[i, j]
            if abs(r) >= threshold:
                strong.append((col1, col2, r))
    strong.sort(key=lambda x: abs(x[2]), reverse=True)
    return strong
```

### 4.2 Conflict-Specific Correlations

```python
def analyze_conflict_correlations(df: pd.DataFrame) -> dict:
    """Analyze correlations between features and collision likelihood by conflict type."""
    results = {}
    
    for ctype in df["conflict_type"].unique():
        subset = df[df["conflict_type"] == ctype]
        
        # Features to correlate with collision occurrence
        features = ["speed_lead", "speed_follow", "gap_distance", "reaction_time",
                     "road_friction", "speed_limit", "number_of_lanes"]
        
        if "collision" in subset.columns:
            corr_matrix = subset[features + ["collision"]].corr(method="pearson")
            collision_corr = corr_matrix["collision"].drop("collision").sort_values()
            results[ctype] = {
                "top_positive_correlations": collision_corr.tail(5).to_dict(),
                "top_negative_correlations": collision_corr.head(5).to_dict()
            }
    
    return results
```

## 5. Segmentation Analysis

### 5.1 Conflict Type Segmentation

```python
def segment_by_conflict_type(df: pd.DataFrame) -> dict:
    """Segment data by conflict type and analyze each group."""
    results = {}
    
    for ctype in df["conflict_type"].unique():
        subset = df[df["conflict_type"] == ctype]
        
        results[ctype] = {
            "n_conflicts": len(subset),
            "n_collisions": subset["collision"].sum() if "collision" in subset.columns else 0,
            "collision_rate": subset["collision"].mean() if "collision" in subset.columns else 0,
            "severity_distribution": subset["severity_level"].value_counts().to_dict() if "severity_level" in subset.columns else {},
            "speed_stats": {
                "lead": {"mean": subset["speed_lead"].mean(), "std": subset["speed_lead"].std()},
                "follow": {"mean": subset["speed_follow"].mean(), "std": subset["speed_follow"].std()}
            } if "speed_lead" in subset.columns else {},
            "gap_stats": {
                "mean": subset["gap_distance"].mean(),
                "median": subset["gap_distance"].median(),
                "p5": subset["gap_distance"].quantile(0.05),
                "p95": subset["gap_distance"].quantile(0.95)
            } if "gap_distance" in subset.columns else {}
        }
    
    return results
```

### 5.2 Jurisdiction Comparison

```python
def compare_jurisdictions(df: pd.DataFrame) -> dict:
    """Compare conflict patterns across jurisdictions."""
    results = {}
    
    for jur in df["jurisdiction"].unique():
        subset = df[df["jurisdiction"] == jur]
        
        results[jur] = {
            "n_conflicts": len(subset),
            "n_jurisdictions": df[df["jurisdiction"] == jur]["crash_id"].nunique(),
            "conflict_type_distribution": subset["conflict_type"].value_counts().to_dict(),
            "severity_distribution": subset["severity_level"].value_counts().to_dict() if "severity_level" in subset.columns else {},
            "avg_speed_ms": subset["speed_ms"].mean() if "speed_ms" in subset.columns else 0,
            "avg_gap_m": subset["gap_distance"].mean() if "gap_distance" in subset.columns else 0,
            "collision_rate": subset["collision"].mean() if "collision" in subset.columns else 0
        }
    
    return results
```

### 5.3 Severity Segmentation

```python
def segment_by_severity(df: pd.DataFrame) -> dict:
    """Segment data by injury severity."""
    results = {}
    
    for severity in df["severity_level"].unique():
        subset = df[df["severity_level"] == severity]
        
        results[severity] = {
            "count": len(subset),
            "percentage": len(subset) / len(df) * 100,
            "conflict_type_distribution": subset["conflict_type"].value_counts().to_dict(),
            "jurisdiction_distribution": subset["jurisdiction"].value_counts().to_dict(),
            "avg_speed_ms": subset["speed_ms"].mean() if "speed_ms" in subset.columns else 0,
            "avg_gap_m": subset["gap_distance"].mean() if "gap_distance" in subset.columns else 0,
            "speed_distribution": {
                "mean": subset["speed_ms"].mean(),
                "std": subset["speed_ms"].std(),
                "median": subset["speed_ms"].median()
            } if "speed_ms" in subset.columns else {}
        }
    
    return results
```

## 6. Visualization

### 6.1 Plotting Functions

```python
import matplotlib.pyplot as plt
import seaborn as sns

class EDAVisualization:
    def create_conflict_type_distribution(self, df: pd.DataFrame) -> plt.Figure:
        """Plot distribution of conflict types."""
        fig, ax = plt.subplots(figsize=(10, 6))
        counts = df["conflict_type"].value_counts().sort_values(ascending=False)
        sns.barplot(x=counts.index, y=counts.values, ax=ax)
        ax.set_title("Conflict Type Distribution")
        ax.set_xlabel("Conflict Type")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    
    def create_speed_histogram(self, df: pd.DataFrame, hue_col: str = None) -> plt.Figure:
        """Plot speed histograms by jurisdiction or conflict type."""
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=df, x="speed_ms", hue=hue_col, ax=ax, kde=True, bins=50)
        ax.set_title("Speed Distribution")
        ax.set_xlabel("Speed (m/s)")
        ax.set_ylabel("Frequency")
        plt.tight_layout()
        return fig
    
    def create_ttc_histogram(self, df: pd.DataFrame) -> plt.Figure:
        """Plot TTC histogram with GPD fit."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ttc_vals = df["TTC"].dropna().values
        sns.histplot(ttc_vals, bins=100, ax=ax, kde=True, stat="density")
        
        # Add GPD fit (if available)
        if len(ttc_vals) > 50:
            gpd_fit = self._fit_gpd(ttc_vals)
            if gpd_fit:
                x = np.linspace(0, ttc_vals.max(), 1000)
                y = gpd_fit.pdf(x)
                ax.plot(x, y, "r--", label="GPD fit", linewidth=2)
                ax.legend()
        
        ax.set_title("TTC Distribution with GPD Fit")
        ax.set_xlabel("TTC (s)")
        ax.set_ylabel("Density")
        plt.tight_layout()
        return fig
    
    def create_jurisdiction_comparison(self, df: pd.DataFrame) -> plt.Figure:
        """Plot collision rate comparison across jurisdictions."""
        fig, ax = plt.subplots(figsize=(8, 6))
        rates = df.groupby("jurisdiction")["collision"].mean()
        rates.plot(kind="bar", ax=ax)
        ax.set_title("Collision Rate by Jurisdiction")
        ax.set_xlabel("Jurisdiction")
        ax.set_ylabel("Collision Rate")
        plt.tight_layout()
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame, numeric_cols: List[str]) -> plt.Figure:
        """Plot correlation heatmap."""
        fig, ax = plt.subplots(figsize=(12, 10))
        corr = df[numeric_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, ax=ax, annot=True, fmt=".2f", cmap="viridis")
        ax.set_title("Feature Correlation Matrix")
        plt.tight_layout()
        return fig
```

### 6.2 Publication-Quality Figures

```python
def create_publication_figure(plt_figure: plt.Figure, save_path: str, dpi: int = 300):
    """Save figure in publication-quality format."""
    plt_figure.savefig(save_path, dpi=dpi, bbox_inches="tight", format="pdf")
    plt_figure.savefig(save_path.replace(".pdf", ".png"), dpi=dpi, bbox_inches="tight")
    plt.close(plt_figure)

def create_multi_panel_figure(figures: dict, layout: tuple = (2, 2), figsize: tuple = (12, 10)):
    """Create multi-panel figure for EDA report."""
    fig, axes = plt.subplots(layout[0], layout[1], figsize=figsize)
    
    for i, (title, ax) in enumerate(zip(figures.keys(), axes.flat)):
        if title in figures:
            figures[title].add_ax(ax)
            ax.set_title(title)
        ax.axis("off")
    
    plt.tight_layout()
    return fig
```

## 7. EDA Report Generation

### 7.1 Markdown Report Template

```markdown
# Collision Risk Data Exploration Report

## 1. Dataset Overview
- Total conflicts: {n_conflicts}
- Jurisdictions: {jurisdictions}
- Conflict types: {conflict_types}
- Date range: {date_range}

## 2. Conflict Type Distribution
{conflict_type_distribution}

## 3. Speed Analysis
{speed_distributions}

## 4. TTC Analysis
{ttc_distributions}

## 5. Correlation Analysis
{key_correlations}

## 6. Jurisdiction Comparison
{jurisdiction_comparison}

## 7. Severity Analysis
{severity_distribution}

## 8. Key Findings
1. {finding_1}
2. {finding_2}
3. {finding_3}
```

## 8. Validation Requirements

### 8.1 Completeness
- **All conflict types** analyzed individually
- **All jurisdictions** compared
- **All severity levels** documented
- **All numeric features** summarized

### 8.2 Reproducibility
- **Seed:** All random operations use fixed seed (42)
- **Dependencies:** All packages and versions documented
- **Data:** Original data preserved, transformations logged

### 8.3 Quality
- **No missing data** in critical fields (crash_id, date, jurisdiction)
- **Outliers** identified and documented
- **Inconsistencies** flagged and addressed
- **Statistical tests** reported where appropriate (p-values, confidence intervals)
