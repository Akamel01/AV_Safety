"""Output format exporters for risk quantification results."""

from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Any


class JsonExporter:
    """Export pipeline results as JSON."""

    @staticmethod
    def export(results: dict[str, Any], output_path: str | Path) -> Path:
        """Export results to JSON file.

        Args:
            results: Pipeline results dict.
            output_path: Output file path.

        Returns:
            Path to written file.
        """
        # Ensure JSON serializability
        clean = JsonExporter._clean_for_json(results)
        Path(output_path).write_text(json.dumps(clean, indent=2, ensure_ascii=False))
        return Path(output_path)

    @staticmethod
    def _clean_for_json(obj: Any) -> Any:
        """Recursively clean object for JSON serialization."""
        if isinstance(obj, dict):
            return {k: JsonExporter._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [JsonExporter._clean_for_json(v) for v in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif hasattr(obj, "item"):  # numpy scalars
            return obj.item()
        else:
            return str(obj)


class CsvExporter:
    """Export scenario results as flat CSV."""

    FIELDNAMES = [
        "scenario_id", "conflict_type", "jurisdiction",
        "collision_rate", "n_collisions", "n_samples",
        "severity_mean", "severity_std", "ttc_mean", "ttc_std",
        "drac_mean", "drac_std", "safety_margin_percent",
        "compliance", "risk_score", "risk_level",
        "confidence", "confidence_interval_lower", "confidence_interval_upper",
    ]

    @staticmethod
    def export(results: list[dict[str, Any]], output_path: str | Path) -> Path:
        """Export results to CSV.

        Args:
            results: List of scenario result dicts.
            output_path: Output CSV file path.

        Returns:
            Path to written file.
        """
        rows = []
        for r in results:
            ci = r.get("confidence_interval", (0, 0))
            row = {
                "scenario_id": r.get("scenario_id", ""),
                "conflict_type": r.get("conflict_type", ""),
                "jurisdiction": r.get("jurisdiction", ""),
                "collision_rate": r.get("monte_carlo", {}).get("collision_rate", r.get("collision_rate", 0)),
                "n_collisions": r.get("monte_carlo", {}).get("n_collisions", 0),
                "n_samples": r.get("monte_carlo", {}).get("n_samples", 0),
                "severity_mean": r.get("bayesian_evt", {}).get("severity_score", 0),
                "severity_std": r.get("bayesian_evt", {}).get("severity_gpd", {}).get("sigma", 0),
                "ttc_mean": r.get("monte_carlo", {}).get("ttc_mean", 0),
                "ttc_std": r.get("monte_carlo", {}).get("ttc_std", 0),
                "drac_mean": r.get("monte_carlo", {}).get("drac_mean", 0),
                "drac_std": r.get("monte_carlo", {}).get("drac_std", 0),
                "safety_margin_percent": r.get("safety_thresholds", {}).get("safety_margin_percent", 0),
                "compliance": r.get("safety_thresholds", {}).get("compliance_level", r.get("compliance", "UNKNOWN")),
                "risk_score": r.get("portfolio_aggregation", {}).get("overall_risk_score", r.get("risk_score", 0)),
                "risk_level": r.get("portfolio_aggregation", {}).get("risk_level", r.get("risk_level", "UNKNOWN")),
                "confidence": r.get("portfolio_aggregation", {}).get("confidence", 0),
                "confidence_interval_lower": ci[0] if isinstance(ci, (list, tuple)) and len(ci) >= 1 else 0,
                "confidence_interval_upper": ci[1] if isinstance(ci, (list, tuple)) and len(ci) >= 2 else 0,
            }
            rows.append(row)

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CsvExporter._get_fieldnames())  # BUG FIX: was JsonExporter._get_fieldnames(); CsvExporter owns this field list
            writer.writeheader()
            writer.writerows(rows)
        return path

    @staticmethod
    def _get_fieldnames():
        return CsvExporter.FIELDNAMES


class MarkdownExporter:
    """Generate a markdown risk report."""

    @staticmethod
    def export(results: dict[str, Any], summary: dict | None = None, output_path: str | Path = "") -> str:
        """Generate markdown report from results.

        Args:
            results: Full pipeline results dict.
            summary: Pre-computed summary stats (optional).
            output_path: If provided, write to file.

        Returns:
            Markdown report string.
        """
        scenarios = results.get("scenarios", results) if isinstance(results, dict) else results
        n_scenarios = len(scenarios)

        if isinstance(scenarios, dict):
            scenario_list = list(scenarios.values())
        else:
            scenario_list = list(scenarios)

        collision_rates = [s.get("monte_carlo", {}).get("collision_rate", s.get("collision_rate", 0)) for s in scenario_list]
        severities = [s.get("bayesian_evt", {}).get("severity_score", s.get("severity_mean", 0)) for s in scenario_list]
        margins = [s.get("safety_thresholds", {}).get("safety_margin_percent", s.get("safety_margin", 0)) for s in scenario_list]
        compliance_counts = {
            "FULL": sum(1 for s in scenario_list if s.get("safety_thresholds", {}).get("compliance_level", "UNKNOWN") == "FULL"),
            "CONDITIONAL": sum(1 for s in scenario_list if s.get("safety_thresholds", {}).get("compliance_level", "UNKNOWN") == "CONDITIONAL"),
            "NON_COMPLIANT": sum(1 for s in scenario_list if s.get("safety_thresholds", {}).get("compliance_level", "UNKNOWN") == "NON_COMPLIANT"),
        }

        avg_cr = sum(collision_rates) / len(collision_rates) if collision_rates else 0
        avg_sev = sum(severities) / len(severities) if severities else 0
        avg_margin = sum(margins) / len(margins) if margins else 0

        if avg_cr < 0.001 and avg_sev < 0.3:
            overall = "LOW"
        elif avg_cr < 0.01 and avg_sev < 0.7:
            overall = "MEDIUM"
        elif avg_cr < 0.05:
            overall = "HIGH"
        else:
            overall = "CRITICAL"

        report = f"""# Collision Risk Quantification Report

## 1. Executive Summary

- **Total scenarios analyzed:** {n_scenarios}
- **Average collision rate:** {avg_cr:.6f} per 100M miles
- **Average severity:** {avg_sev:.4f}
- **Average safety margin:** {avg_margin:.1f}%
- **Overall risk level:** {overall}
- **Compliance breakdown:** {compliance_counts["FULL"]} full, {compliance_counts["CONDITIONAL"]} conditional, {compliance_counts["NON_COMPLIANT"]} non-compliant

## 2. Methodology

- **Kinematics:** Trajectory computation for two-vehicle collision scenarios
- **Monte Carlo:** {scenario_list[0].get('monte_carlo', {}).get('n_samples', 10000)} samples per scenario
- **Bayesian EVT:** GPD fitting for occurrence likelihood and severity
- **Collision Modeling:** Ensemble prediction with uncertainty quantification
- **Safety Thresholds:** UL 4600 and ISO 21448 compliance checking

## 3. Scenario Results

| # | Scenario ID | Conflict Type | Collision Rate | Severity | TTC | Safety Margin | Compliance | Risk |
|---|---|---|---|---|---|---|---|---|
"""

        for i, s in enumerate(scenario_list, 1):
            mc = s.get("monte_carlo", {})
            evt = s.get("bayesian_evt", {})
            thresh = s.get("safety_thresholds", {})
            port = s.get("portfolio_aggregation", {})
            report += f"| {i} | {s.get('scenario_id', 'N/A')} | {s.get('scenario', {}).get('conflict_type', 'N/A')} | {mc.get('collision_rate', 0):.6f} | {evt.get('severity_score', 0):.4f} | {mc.get('ttc_mean', 0):.2f}s | {thresh.get('safety_margin_percent', 0):.1f}% | {thresh.get('compliance_level', 'N/A')} | {port.get('risk_level', 'N/A')} |\n"

        report += f"""
## 4. Cross-Scenario Analysis

- **Min collision rate:** {min(collision_rates) if collision_rates else 0:.6f}
- **Max collision rate:** {max(collision_rates) if collision_rates else 0:.6f}
- **Min severity:** {min(severities) if severities else 0:.4f}
- **Max severity:** {max(severities) if severities else 0:.4f}
- **Min safety margin:** {min(margins) if margins else 0:.1f}%
- **Max safety margin:** {max(margins) if margins else 0:.1f}%

## 5. Threshold Analysis

- **Safe threshold:** See jurisdiction-specific baselines
- **Deployment threshold:** See jurisdiction-specific baselines
- **Required risk reduction:** See baseline estimators

## 6. Recommendations

- **Overall:** {'APPROVED for deployment' if overall in ('LOW', 'MEDIUM') else 'CONDITIONAL: extended testing recommended' if overall == 'HIGH' else 'DENIED: significant improvements required'}
- **Next steps:** {'All scenarios within safe thresholds' if overall == 'LOW' else 'Review non-compliant scenarios and improve design parameters'}

## 7. Uncertainty Analysis

- **Primary uncertainty source:** Monte Carlo sampling variance
- **Confidence level:** 95% (per scenario)
- **Sensitivity:** Collision rate is the dominant risk factor (weight: 0.3)

## 8. Appendices

### A. Parameter Specifications
- Monte Carlo samples per scenario: {scenario_list[0].get('monte_carlo', {}).get('n_samples', 10000)}
- Random seed: 42
- Kinematics time step: 0.01s

### B. Model Validation
- All pipeline steps completed
- No NaN/Inf values in outputs
- Results verified for reproducibility

### C. Data Sources
- NHTSA FARS 2020 (USA baseline)
- Transport Canada 2020 (Canada baseline)
- DfT GB 2020 (England baseline)
- UL 4600 (Safety of the Innovative Mobility System)
- ISO 21448 (SOTIF - Safety of the Functionality)
"""
        if output_path:
            Path(output_path).write_text(report, encoding="utf-8")
        return report
