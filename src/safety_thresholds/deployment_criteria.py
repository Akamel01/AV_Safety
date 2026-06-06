"""AV deployment criteria evaluation.

Evaluates AV collision rates against jurisdictional thresholds
and produces deployment recommendations.
"""

from __future__ import annotations

from .collision_rate_thresholds import THRESHOLDS


class AVDeploymentCriteria:
    """Evaluate AV deployment readiness against safety thresholds."""

    def evaluate_deployment(
        self,
        av_collision_rate: float,
        jurisdiction: str,
        confidence_interval: tuple[float, float] | None = None,
    ) -> dict:
        """Evaluate deployment eligibility for a given AV collision rate.

        Args:
            av_collision_rate: Observed AV collision rate per 100M miles.
            jurisdiction: Jurisdiction code (usa, canada, england).
            confidence_interval: Optional 95% CI for the AV rate estimate.

        Returns:
            Dict with meets_threshold, safety_margin_percent, recommendation,
            threshold_value, and additional_requirements.

        Raises:
            ValueError: If jurisdiction is unknown or rate is invalid.
        """
        if av_collision_rate < 0:
            raise ValueError("av_collision_rate must be non-negative")
        if jurisdiction not in THRESHOLDS:
            raise ValueError(
                f"Unknown jurisdiction: {jurisdiction!r}. "
                f"Known: {list(THRESHOLDS.keys())}"
            )

        thresholds = THRESHOLDS[jurisdiction]
        meets = av_collision_rate < thresholds.deployment_threshold
        margin = thresholds.safety_margin(av_collision_rate)

        if av_collision_rate < thresholds.safe_threshold:
            recommendation = "APPROVED"
            additional_requirements = []
        elif av_collision_rate < thresholds.deployment_threshold:
            recommendation = "CONDITIONAL"
            additional_requirements = ["extended_testing", "monitoring_program"]
        else:
            recommendation = "DENIED"
            additional_requirements = [
                "extended_testing",
                "monitoring_program",
                "design_modification_required",
            ]

        return {
            "jurisdiction": jurisdiction,
            "av_collision_rate": av_collision_rate,
            "meets_threshold": meets,
            "safety_margin_percent": margin,
            "threshold_value": thresholds.deployment_threshold,
            "safe_threshold": thresholds.safe_threshold,
            "recommendation": recommendation,
            "additional_requirements": additional_requirements,
            "confidence_interval": confidence_interval,
        }

    def evaluate_all_jurisdictions(
        self,
        av_collision_rate: float,
        confidence_interval: tuple[float, float] | None = None,
    ) -> dict[str, dict]:
        """Evaluate against all jurisdictions.

        Args:
            av_collision_rate: Observed AV collision rate.
            confidence_interval: Optional 95% CI.

        Returns:
            Dict keyed by jurisdiction with evaluation results.
        """
        return {
            jur: self.evaluate_deployment(av_collision_rate, jur, confidence_interval)
            for jur in THRESHOLDS
        }
