# Skill: Safety Thresholds

**Purpose:** Quantify "safe enough" thresholds for autonomous vehicle deployment using statistical analysis, Bayesian modeling, and regulatory frameworks.

## 1. Core Framework

### 1.1 The "Safe Enough" Question

How safe is safe enough for autonomous vehicles?

This requires:
1. **Quantifying baseline risk** — human driver collision rates by jurisdiction
2. **Defining acceptable risk** — how much safer must AV be vs humans?
3. **Setting deployment thresholds** — minimum safety level for AV approval
4. **Validating thresholds** — testing against real-world data and standards

### 1.2 Key Definitions

| Term | Definition | Typical Value |
|---|-|-|
| **Baseline collision rate** | Human driver collision rate per mile/hour | 1-3 per 100M miles (fatal) |
| **Acceptable risk reduction** | How much safer AV must be vs humans | 10-30% reduction |
| **Safe threshold** | Maximum acceptable collision rate for AV | < 0.5 per 100M miles |
| **Safety margin** | Gap between AV performance and threshold | ≥ 50% above threshold |

## 2. Methodology

### 2.1 Step 1: Establish Baseline

```python
class BaselineEstimator:
    def estimate_human_baseline(self, jurisdiction: str) -> dict:
        """Estimate human driver collision baseline by jurisdiction."""
        # Data sources: NHTSA FARS (USA), Transport Canada (Canada), DfT GB (England)
        
        if jurisdiction == "USA":
            # NHTSA 2020 data
            return {
                "fatal_rate_per_100m_miles": 1.12,
                "injury_rate_per_100m_miles": 125.0,
                "property_damage_rate_per_100m_miles": 500.0,
                "source": "NHTSA FARS 2020",
                "confidence_interval": {"lower": 1.05, "upper": 1.19}
            }
        elif jurisdiction == "Canada":
            return {
                "fatal_rate_per_100m_miles": 0.89,
                "injury_rate_per_100m_miles": 98.0,
                "property_damage_rate_per_100m_miles": 410.0,
                "source": "Transport Canada 2020",
                "confidence_interval": {"lower": 0.82, "upper": 0.96}
            }
        elif jurisdiction == "England":
            return {
                "fatal_rate_per_100m_miles": 0.72,
                "injury_rate_per_100m_miles": 85.0,
                "property_damage_rate_per_100m_miles": 380.0,
                "source": "DfT GB 2020",
                "confidence_interval": {"lower": 0.65, "upper": 0.79}
            }
        
        raise ValueError(f"Unknown jurisdiction: {jurisdiction}")
```

### 2.2 Step 2: Define Acceptable Risk

```python
class AcceptableRiskDefiner:
    def define_acceptable_reduction(self, 
                                   baseline_fatal_rate: float,
                                   acceptable_increase_in_fatalities: int = 1,
                                   confidence_level: float = 0.95) -> dict:
        """
        Define acceptable risk based on how many additional fatalities are acceptable.
        
        For example: If baseline is 1.12 per 100M miles, and we accept
        at most 1 additional fatality per year (≈ 0.00001 per mile),
        then AV must be safer by at least that amount.
        """
        # Acceptable risk threshold
        acceptable_threshold = baseline_fatal_rate - (acceptable_increase_in_fatalities / 1e8)
        
        # Required reduction percentage
        required_reduction = (baseline_fatal_rate - acceptable_threshold) / baseline_fatal_rate * 100
        
        return {
            "baseline_fatal_rate": baseline_fatal_rate,
            "acceptable_increase_in_fatalities": acceptable_increase_in_fatalities,
            "acceptable_threshold": acceptable_threshold,
            "required_reduction_percent": required_reduction,
            "confidence_level": confidence_level
        }
```

### 2.3 Step 3: Quantify Safe Threshold

```python
class SafeThresholdQuantifier:
    def compute_safe_threshold(self, 
                               baseline: dict,
                               acceptable_reduction: dict,
                               confidence_level: float = 0.95) -> dict:
        """Compute safe threshold for AV deployment."""
        
        # Safe threshold = baseline × (1 - required_reduction)
        safe_threshold = baseline["fatal_rate_per_100m_miles"] * (1 - acceptable_reduction["required_reduction_percent"]/100)
        
        # Apply margin of safety (10-20% above threshold)
        margin = 0.15  # 15% margin
        deployment_threshold = safe_threshold * (1 + margin)
        
        return {
            "safe_threshold": safe_threshold,
            "deployment_threshold": deployment_threshold,
            "margin_percent": margin * 100,
            "confidence_level": confidence_level,
            "baseline_fatal_rate": baseline["fatal_rate_per_100m_miles"],
            "required_reduction_percent": acceptable_reduction["required_reduction_percent"]
        }
```

## 3. Threshold Computation by Metric

### 3.1 Collision Rate Thresholds

```python
@dataclass
class CollisionRateThresholds:
    jurisdiction: str
    safe_threshold: float  # collisions per 100M miles
    deployment_threshold: float  # with margin
    baseline_fatal_rate: float
    required_reduction_percent: float
    confidence_interval: tuple  # (lower, upper)
    
    def meets_threshold(self, av_rate: float) -> bool:
        return av_rate < self.deployment_threshold
    
    def safety_margin(self, av_rate: float) -> float:
        return (self.deployment_threshold - av_rate) / self.deployment_threshold * 100

# Example thresholds
THRESHOLDS = {
    "USA": CollisionRateThresholds(
        jurisdiction="USA",
        safe_threshold=0.85,
        deployment_threshold=0.97,
        baseline_fatal_rate=1.12,
        required_reduction_percent=24.1,
        confidence_interval=(0.80, 1.05)
    ),
    "Canada": CollisionRateThresholds(
        jurisdiction="Canada",
        safe_threshold=0.67,
        deployment_threshold=0.77,
        baseline_fatal_rate=0.89,
        required_reduction_percent=24.7,
        confidence_interval=(0.62, 0.82)
    ),
    "England": CollisionRateThresholds(
        jurisdiction="England",
        safe_threshold=0.54,
        deployment_threshold=0.62,
        baseline_fatal_rate=0.72,
        required_reduction_percent=25.0,
        confidence_interval=(0.50, 0.65)
    )
}
```

### 3.2 TTC Thresholds

```python
TTC_THRESHOLDS = {
    "critical": {
        "threshold": 1.0,  # seconds
        "description": "Immediate collision likely",
        "action": "emergency_brake"
    },
    "dangerous": {
        "threshold": 2.0,  # seconds
        "description": "High collision risk",
        "action": "hard_brake"
    },
    "warning": {
        "threshold": 3.0,  # seconds
        "description": "Moderate collision risk",
        "action": "alert_driver"
    },
    "safe": {
        "threshold": 5.0,  # seconds
        "description": "Low collision risk",
        "action": "monitor"
    }
}
```

### 3.3 DRAC Thresholds

```python
DRAC_THRESHOLDS = {
    "emergency": {
        "threshold": 8.0,  # m/s²
        "description": "Maximum emergency braking",
        "action": "full_brake"
    },
    "hard_brake": {
        "threshold": 5.0,  # m/s²
        "description": "Hard braking required",
        "action": "hard_brake"
    },
    "moderate_brake": {
        "threshold": 3.0,  # m/s²
        "description": "Moderate braking",
        "action": "alert_driver"
    },
    "light_brake": {
        "threshold": 1.5,  # m/s²
        "description": "Light braking",
        "action": "monitor"
    }
}
```

## 4. Bayesian Threshold Estimation

### 4.1 Hierarchical Model

```python
import pymc as pm
import numpy as np

def estimate_threshold_bayesian(collision_data: dict, jurisdictions: list) -> dict:
    """Estimate safe threshold using Bayesian hierarchical model."""
    
    # Data format: {jurisdiction: [(collisions, miles_traveled), ...]}
    
    with pm.Model() as model:
        # Global parameters
        mu_alpha = pm.Normal("mu_alpha", mu=0, sigma=1)
        sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=1)
        
        # Jurisdiction-specific parameters
        alpha = pm.Normal("alpha", mu=mu_alpha, sigma=sigma_alpha, 
                         shape=len(jurisdictions))
        
        # Likelihood: Poisson process
        for jur, (collisions, miles) in collision_data.items():
            idx = jurisdictions.index(jur)
            rate = pm.Deterministic(f"rate_{jur}", pm.math.exp(alpha[idx]))
            observed = pm.Poisson("observed", mu=rate * miles, observed=collisions)
        
        # Sample posterior
        trace = pm.sample(2000, tune=1000, chains=4)
    
    # Extract safe threshold
    safe_thresholds = {}
    for jur in jurisdictions:
        rate_trace = trace[f"rate_{jur}"]
        safe_thresholds[jur] = {
            "mean_rate": np.mean(rate_trace),
            "median_rate": np.median(rate_trace),
            "ci95": np.percentile(rate_trace, [2.5, 97.5]),
            "p_safe": np.mean(rate_trace < 0.5)  # P(rate < 0.5 per 100M miles)
        }
    
    return safe_thresholds
```

## 5. Standards-Based Thresholds

### 5.1 UL 4600 Compliance

```python
# UL 4600 collision risk thresholds
UL4600_THRESHOLDS = {
    "collision_avoidance": {
        "minimum_safe_distance": "2.0 seconds TTC",
        "maximum_acceptable_collision_rate": "10^-6 per flight hour",
        "safety_margin": "≥ 50% above threshold"
    },
    "risk_management": {
        "individual_risk_acceptable": "10^-5 per flight hour",
        "societal_risk_acceptable": "10^-7 per flight hour",
        "risk_reduction_required": "≥ 90% below baseline"
    }
}
```

### 5.2 ISO 21448 (SOTIF) Alignment

```python
ISO21448_THRESHOLDS = {
    "performance": {
        "minimum_safe_operation": "TTC ≥ 2.5s",
        "degradation_tolerance": "≤ 10% degradation acceptable",
        "fallback_distance": "≥ 50m at legal speed"
    },
    "hazard_analysis": {
        "unintended_functionality": "zero tolerance",
        "perception_limit": "TTC ≥ 1.0s at perception limit",
        "actuation_limit": "TTC ≥ 2.0s at actuation limit"
    }
}
```

## 6. Threshold Application

### 6.1 Deployment Criteria

```python
class AVDeploymentCriteria:
    def evaluate_deployment(self, av_collision_rate: float, 
                          jurisdiction: str,
                          confidence_interval: tuple) -> dict:
        """Evaluate if AV meets deployment criteria."""
        
        thresholds = THRESHOLDS[jurisdiction]
        
        return {
            "meets_threshold": av_collision_rate < thresholds.deployment_threshold,
            "safety_margin_percent": thresholds.safety_margin(av_collision_rate),
            "confidence_interval": confidence_interval,
            "threshold_value": thresholds.deployment_threshold,
            "recommendation": "APPROVED" if av_collision_rate < thresholds.safe_threshold else 
                            "CONDITIONAL" if av_collision_rate < thresholds.deployment_threshold else "DENIED",
            "additional_requirements": [] if av_collision_rate < thresholds.safe_threshold else ["extended_testing"]
        }
```

### 6.2 Continuous Monitoring

```python
class ContinuousMonitoring:
    def update_threshold(self, new_data: dict, current_threshold: float, 
                        learning_rate: float = 0.01) -> float:
        """Update threshold based on new data (online learning)."""
        
        # Bayesian update
        prior_mean = current_threshold
        likelihood_mean = np.mean(new_data["collision_rates"])
        
        # Weighted average
        updated_threshold = (1 - learning_rate) * prior_mean + learning_rate * likelihood_mean
        
        return updated_threshold
```

## 7. Validation Requirements

### 7.1 Threshold Validation

| Criterion | Test | Pass Condition |
|---|-|-|
| **Statistical significance** | Compare AV vs baseline | p < 0.05 |
| **Practical significance** | Reduction ≥ 10% | True |
| **Standards alignment** | UL 4600 / ISO 21448 | Compliant |
| **Jurisdiction alignment** | Meets local requirements | True |
| **Margin adequacy** | ≥ 15% margin | True |

### 7.2 Documentation Requirements

- Every threshold: source, methodology, assumptions, confidence level
- Comparison to published benchmarks with citation
- Sensitivity analysis for key parameters
- Review by independent safety experts (if available)
