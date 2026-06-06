"""Continuous monitoring and online threshold updates.

Implements Bayesian-style online learning for threshold estimation
with configurable learning rates.
"""

from __future__ import annotations

from .collision_rate_thresholds import THRESHOLDS


class ContinuousMonitoring:
    """Online threshold estimation with learning."""

    DEFAULT_LEARNING_RATE = 0.01

    def update_threshold(
        self,
        current_threshold: float,
        new_data: float,
        learning_rate: float | None = None,
    ) -> float:
        """Update threshold using exponential moving average.

        Args:
            current_threshold: Current threshold estimate.
            new_data: New observed collision rate.
            learning_rate: Weight for new data (default 0.01).

        Returns:
            Updated threshold estimate.
        """
        if learning_rate is None:
            learning_rate = self.DEFAULT_LEARNING_RATE
        if not (0 < learning_rate <= 1):
            raise ValueError("learning_rate must be in (0, 1]")

        updated = (1 - learning_rate) * current_threshold + learning_rate * new_data
        return updated

    def update_from_data(
        self,
        current_threshold: float,
        new_observations: list[float],
        learning_rate: float | None = None,
    ) -> float:
        """Update threshold from multiple observations.

        Args:
            current_threshold: Current threshold estimate.
            new_observations: List of new collision rate observations.
            learning_rate: Weight for new data.

        Returns:
            Updated threshold estimate.
        """
        if not new_observations:
            return current_threshold

        mean_observation = sum(new_observations) / len(new_observations)
        return self.update_threshold(current_threshold, mean_observation, learning_rate)

    def bayesian_update(
        self,
        prior_mean: float,
        prior_variance: float,
        likelihood_mean: float,
        likelihood_variance: float,
    ) -> tuple[float, float]:
        """Bayesian posterior update for threshold estimation.

        Uses conjugate normal-normal model.

        Args:
            prior_mean: Prior mean threshold.
            prior_variance: Prior variance.
            likelihood_mean: Observed mean from new data.
            likelihood_variance: Variance of the likelihood.

        Returns:
            (posterior_mean, posterior_variance) tuple.
        """
        if prior_variance <= 0 or likelihood_variance <= 0:
            raise ValueError("Variances must be positive")

        # Precision-weighted combination
        prior_precision = 1.0 / prior_variance
        likelihood_precision = 1.0 / likelihood_variance
        posterior_precision = prior_precision + likelihood_precision
        posterior_variance = 1.0 / posterior_precision
        posterior_mean = (
            prior_precision * prior_mean + likelihood_precision * likelihood_mean
        ) / posterior_precision

        return posterior_mean, posterior_variance

    def compute_jurisdiction_threshold_for_rate(
        self,
        av_collision_rate: float,
        jurisdiction: str,
    ) -> dict:
        """Compute what the threshold would need to be for a given AV rate.

        Args:
            av_collision_rate: Observed AV rate.
            jurisdiction: Jurisdiction code.

        Returns:
            Dict with computed thresholds and compliance status.
        """
        if jurisdiction not in THRESHOLDS:
            raise ValueError(f"Unknown jurisdiction: {jurisdiction}")

        thresh = THRESHOLDS[jurisdiction]
        margin = thresh.safety_margin(av_collision_rate)
        level = thresh.risk_level(av_collision_rate)

        return {
            "jurisdiction": jurisdiction,
            "av_rate": av_collision_rate,
            "safe_threshold": thresh.safe_threshold,
            "deployment_threshold": thresh.deployment_threshold,
            "safety_margin_percent": margin,
            "risk_level": level,
            "baseline_fatal_rate": thresh.baseline_fatal_rate,
        }
