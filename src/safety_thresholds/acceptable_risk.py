"""Acceptable risk reduction definer.

Computes the required risk reduction percentage that AVs must achieve
below human driver baselines to be considered "safe enough" for deployment.
"""

from __future__ import annotations


class AcceptableRiskDefiner:
    """Define acceptable risk thresholds for AV deployment."""

    DEFAULT_ACCEPTABLE_INCREASE_FATALITIES = 1  # One extra fatality over baseline
    DEFAULT_CONFIDENCE_LEVEL = 0.95

    def define_acceptable_reduction(
        self,
        baseline_fatal_rate: float,
        acceptable_increase_in_fatalities: int = 1,
        confidence_level: float = 0.95,
    ) -> dict:
        """Compute acceptable threshold and required reduction percentage.

        Args:
            baseline_fatal_rate: Human driver fatal rate per 100M miles.
            acceptable_increase_in_fatalities: How many additional fatalities
                are deemed acceptable above baseline.
            confidence_level: Statistical confidence level (default 95%).

        Returns:
            Dict with baseline_fatal_rate, acceptable_threshold,
            required_reduction_percent, and confidence_level.
        """
        if baseline_fatal_rate <= 0:
            raise ValueError("baseline_fatal_rate must be positive")
        if acceptable_increase_in_fatalities < 0:
            raise ValueError("acceptable_increase_in_fatalities must be non-negative")
        if not (0 < confidence_level <= 1):
            raise ValueError("confidence_level must be in (0, 1]")

        acceptable_threshold = baseline_fatal_rate - (acceptable_increase_in_fatalities / 1e8)
        # Guard: if acceptable_threshold goes negative, set to zero
        if acceptable_threshold <= 0:
            acceptable_threshold = baseline_fatal_rate * 0.01  # 1% of baseline

        required_reduction = (
            (baseline_fatal_rate - acceptable_threshold) / baseline_fatal_rate * 100
        )

        return {
            "baseline_fatal_rate": baseline_fatal_rate,
            "acceptable_increase_in_fatalities": acceptable_increase_in_fatalities,
            "acceptable_threshold": acceptable_threshold,
            "required_reduction_percent": required_reduction,
            "confidence_level": confidence_level,
        }

    def compute_required_reduction(
        self,
        baseline_fatal_rate: float,
        target_fatal_rate: float,
    ) -> float:
        """Compute the required percentage reduction to go from baseline to target.

        Args:
            baseline_fatal_rate: Human baseline rate.
            target_fatal_rate: Target AV rate.

        Returns:
            Required reduction as a percentage (e.g. 24.7 means 24.7%).
        """
        if baseline_fatal_rate <= 0 or target_fatal_rate < 0:
            raise ValueError("Invalid rate values")
        if target_fatal_rate > baseline_fatal_rate:
            return 0.0  # No reduction needed
        return (baseline_fatal_rate - target_fatal_rate) / baseline_fatal_rate * 100
