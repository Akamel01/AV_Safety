"""Safe and deployment threshold computation.

Computes safe deployment thresholds by applying required reduction
percentages to jurisdictional baselines with configurable safety margins.
"""

from __future__ import annotations


class SafeThresholdQuantifier:
    """Compute safe and deployment thresholds for AV collision rates."""

    DEFAULT_MARGIN = 0.15  # 15% safety margin above safe threshold

    def compute_safe_threshold(
        self,
        baseline_fatal_rate: float,
        required_reduction_percent: float,
        margin: float | None = None,
        confidence_level: float = 0.95,
    ) -> dict:
        """Compute safe and deployment thresholds.

        Args:
            baseline_fatal_rate: Human driver fatal rate per 100M miles.
            required_reduction_percent: Required risk reduction (%) to be safe.
            margin: Safety margin above safe threshold (default 15%).
            confidence_level: Statistical confidence level.

        Returns:
            Dict with safe_threshold, deployment_threshold, margin_percent,
            confidence_level, baseline_fatal_rate, required_reduction_percent.
        """
        if baseline_fatal_rate <= 0:
            raise ValueError("baseline_fatal_rate must be positive")
        if not (0 <= required_reduction_percent < 100):
            raise ValueError("required_reduction_percent must be in [0, 100)")
        if margin is None:
            margin = self.DEFAULT_MARGIN

        safe_threshold = baseline_fatal_rate * (1 - required_reduction_percent / 100)
        deployment_threshold = safe_threshold * (1 + margin)

        return {
            "safe_threshold": safe_threshold,
            "deployment_threshold": deployment_threshold,
            "margin_percent": margin * 100,
            "confidence_level": confidence_level,
            "baseline_fatal_rate": baseline_fatal_rate,
            "required_reduction_percent": required_reduction_percent,
        }

    def compute_all_jurisdictions(self) -> dict[str, dict]:
        """Compute thresholds for all jurisdictions using standard parameters.

        Returns:
            Dict keyed by jurisdiction with threshold dicts.
        """
        from .baseline_estimator import BaselineEstimator
        from .acceptable_risk import AcceptableRiskDefiner

        estimator = BaselineEstimator()
        definer = AcceptableRiskDefiner()
        quantifier = SafeThresholdQuantifier()

        results = {}
        for jur in estimator.available_jurisdictions:
            baseline = estimator.get_baseline(jur)
            reduction = definer.define_acceptable_reduction(baseline.fatal_rate_per_100m_miles)
            thresholds = quantifier.compute_safe_threshold(
                baseline.fatal_rate_per_100m_miles,
                reduction["required_reduction_percent"],
            )
            results[jur] = {
                **thresholds,
                "baseline_source": baseline.source,
                "injury_rate_per_100m_miles": baseline.injury_rate_per_100m_miles,
                "property_damage_rate_per_100m_miles": baseline.property_damage_rate_per_100m_miles,
                "confidence_interval": baseline.confidence_interval,
            }

        return results
