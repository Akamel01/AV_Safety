"""Pre-computed collision rate thresholds for all jurisdictions.

Derived from BaselineEstimator + AcceptableRiskDefiner + SafeThresholdQuantifier
with standard parameters (1 acceptable fatality increase, 15% margin).

Thresholds are in units of collision events per 100 million vehicle-miles.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CollisionRateThresholds:
    """Immutable collision rate thresholds for a jurisdiction.

    Attributes:
        jurisdiction: Jurisdiction code (usa, canada, england).
        safe_threshold: Safe threshold (per 100M miles) -- below this is
            considered "safe enough" for deployment.
        deployment_threshold: Deployment threshold -- AVs meeting this may
            deploy with conditions.
        baseline_fatal_rate: Human baseline fatal rate (per 100M miles).
        required_reduction_percent: Required risk reduction vs. baseline (%).
        confidence_interval: 95% CI for the human baseline rate.
    """
    jurisdiction: str
    safe_threshold: float
    deployment_threshold: float
    baseline_fatal_rate: float
    required_reduction_percent: float
    confidence_interval: tuple[float, float]

    def meets_threshold(self, av_rate: float) -> bool:
        """Check if AV rate is below deployment threshold.

        Args:
            av_rate: Observed AV collision rate per 100M miles.

        Returns:
            True if AV rate is safely below deployment threshold.
        """
        return av_rate < self.deployment_threshold

    def safety_margin(self, av_rate: float) -> float:
        """Compute safety margin percentage for given AV rate.

        The margin is how far below the deployment threshold the AV rate is,
        expressed as a percentage of the threshold.

        Args:
            av_rate: Observed AV collision rate per 100M miles.

        Returns:
            Safety margin as percentage (0-100).
        """
        if self.deployment_threshold <= 0:
            return 0.0
        return (self.deployment_threshold - av_rate) / self.deployment_threshold * 100

    def risk_level(self, av_rate: float) -> str:
        """Classify risk level for given AV rate.

        Args:
            av_rate: Observed AV collision rate per 100M miles.

        Returns:
            'SAFE' if below safe_threshold,
            'CONDITIONAL' if below deployment_threshold,
            'DANGEROUS' if at or above deployment_threshold.
        """
        if av_rate < self.safe_threshold:
            return "SAFE"
        elif av_rate < self.deployment_threshold:
            return "CONDITIONAL"
        else:
            return "DANGEROUS"


# Pre-computed thresholds using standard parameters
# Derived from: baseline + 1 acceptable fatality + 15% margin
#
# Source data:
#   USA:   NHTSA FARS 2020 -> 1.12 fatal/100Mm
#   Canada: Transport Canada -> 0.89 fatal/100Mm
#   England: DfT GB / JACArP -> 0.72 fatal/100Mm
THRESHOLDS: dict[str, CollisionRateThresholds] = {
    "usa": CollisionRateThresholds(
        jurisdiction="usa",
        safe_threshold=0.85,
        deployment_threshold=0.97,
        baseline_fatal_rate=1.12,
        required_reduction_percent=24.1,
        confidence_interval=(1.05, 1.19),
    ),
    "canada": CollisionRateThresholds(
        jurisdiction="canada",
        safe_threshold=0.67,
        deployment_threshold=0.77,
        baseline_fatal_rate=0.89,
        required_reduction_percent=24.7,
        confidence_interval=(0.82, 0.96),
    ),
    "england": CollisionRateThresholds(
        jurisdiction="england",
        safe_threshold=0.54,
        deployment_threshold=0.62,
        baseline_fatal_rate=0.72,
        required_reduction_percent=25.0,
        confidence_interval=(0.65, 0.79),
    ),
}
