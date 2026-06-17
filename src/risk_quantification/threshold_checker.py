"""Threshold compliance checker for risk quantification.

Checks scenario collision rates against jurisdictional safety
thresholds and produces compliance classifications.
"""

from __future__ import annotations

# safety_thresholds is a sibling package under src/ — use absolute import for standalone scripts
from src.safety_thresholds import BaselineEstimator, CollisionRateThresholds, THRESHOLDS, AVDeploymentCriteria


class ThresholdComplianceChecker:
    """Check collision rate compliance against safety thresholds."""

    def __init__(self, jurisdiction: str = "usa"):
        """Initialize checker for a specific jurisdiction.

        Args:
            jurisdiction: Jurisdiction code (usa, canada, england).

        Raises:
            ValueError: If jurisdiction is unknown.
        """
        if jurisdiction not in THRESHOLDS:
            raise ValueError(
                f"Unknown jurisdiction: {jurisdiction!r}. "
                f"Known: {list(THRESHOLDS.keys())}"
            )
        self.jurisdiction = jurisdiction
        self.thresholds = THRESHOLDS[jurisdiction]
        self.evaluator = AVDeploymentCriteria()

    @property
    def baseline_estimator(self) -> BaselineEstimator:
        """Return the baseline estimator for jurisdiction lookups."""
        return BaselineEstimator()

    def check_compliance(
        self,
        collision_rate: float,
        n_samples: int = 10000,
        confidence_interval: tuple[float, float] | None = None,
    ) -> dict:
        """Check compliance for a single scenario's collision rate.

        Args:
            collision_rate: Observed AV collision rate per 100M miles.
            n_samples: Number of Monte Carlo samples used.
            confidence_interval: Optional 95% CI for the collision rate.

        Returns:
            Dict with compliance_level, safety_margin_percent,
            required_improvement, and threshold details.
        """
        if collision_rate < 0:
            raise ValueError("collision_rate must be non-negative")

        threshold_val = self.thresholds.deployment_threshold
        safe_val = self.thresholds.safe_threshold
        baseline = self.thresholds.baseline_fatal_rate

        compliance_level = (
            "FULL" if collision_rate < safe_val
            else "CONDITIONAL" if collision_rate < threshold_val
            else "NON_COMPLIANT"
        )

        margin = (threshold_val - collision_rate) / threshold_val * 100
        required_improvement = max(0, (collision_rate - safe_val) / collision_rate * 100) if collision_rate > 0 else 0.0

        return {
            "jurisdiction": self.jurisdiction,
            "collision_rate": collision_rate,
            "n_samples": n_samples,
            "compliance_level": compliance_level,
            "meets_threshold": collision_rate < threshold_val,
            "safety_margin_percent": margin,
            "required_improvement_percent": required_improvement,
            "threshold_value": threshold_val,
            "safe_threshold": safe_val,
            "baseline_fatal_rate": baseline,
            "confidence_interval": confidence_interval,
        }

    def check_batch(
        self,
        results: list[dict],
    ) -> dict[str, dict]:
        """Check compliance for multiple scenario results.

        Args:
            results: List of dicts with 'scenario_id', 'collision_rate',
                'n_samples', and optionally 'confidence_interval'.

        Returns:
            Dict keyed by scenario_id with compliance results.
        """
        return {
            r.get("scenario_id", f"scenario_{i}"): self.check_compliance(
                r["collision_rate"],
                r.get("n_samples", 10000),
                r.get("confidence_interval"),
            )
            for i, r in enumerate(results)
        }

    def get_jurisdiction_info(self) -> dict:
        """Return jurisdiction threshold metadata."""
        return {
            "jurisdiction": self.jurisdiction,
            "baseline_fatal_rate": self.thresholds.baseline_fatal_rate,
            "safe_threshold": self.thresholds.safe_threshold,
            "deployment_threshold": self.thresholds.deployment_threshold,
            "required_reduction_percent": self.thresholds.required_reduction_percent,
            "confidence_interval": self.thresholds.confidence_interval,
        }
