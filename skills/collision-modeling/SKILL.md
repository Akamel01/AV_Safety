# Skill: Collision Modeling

**Purpose:** Build collision risk prediction models using machine learning and statistical methods, integrated with Bayesian EVT and kinematic simulation outputs.

## 1. Model Architecture

### 1.1 Model Types

| Model Type | Purpose | Input | Output |
|---|-|-|-|
| **Logistic Regression** | Binary collision prediction | Kinematic features | P(collision) |
| **Random Forest** | Multi-class risk classification | Features + conflicts | Risk level |
| **XGBoost** | Gradient-boosted risk score | Features + metadata | Risk score |
| **Neural Network** | Complex risk surface | All features | Risk probability |
| **Bayesian Model** | Uncertainty-aware prediction | Features + priors | P(collision|features) |

### 1.2 File Structure

```
src/risk_models/
├── __init__.py
├── collision_model.py     — Base collision model class
├── logistic_regression.py — Logistic regression model
├── random_forest.py       — Random forest model
├── xgboost_model.py       — XGBoost model
├── neural_network.py      — Neural network model
├── bayesian_model.py      — Bayesian predictive model
├── ensemble.py            — Ensemble model combining multiple models
├── validation.py          — Model validation metrics
└── benchmarking.py        — Compare models against benchmarks
```

## 2. Feature Engineering

### 2.1 Feature Set for Collision Prediction

```python
class FeatureEngine:
    @staticmethod
    def extract_features(trajectory: dict, indicators: dict, scenario: dict) -> dict:
        """Extract all features for collision risk prediction."""
        features = {}
        
        # Kinematic features
        features["speed_lead"] = scenario.get("speed_lead", 0)
        features["speed_follow"] = scenario.get("speed_follow", 0)
        features["speed_diff"] = abs(scenario.get("speed_lead", 0) - scenario.get("speed_follow", 0))
        features["relative_accel"] = indicators.get("relative_accel", 0)
        features["closing_speed"] = indicators.get("closing_speed", 0)
        features["delta_v"] = indicators.get("delta_v", 0)
        
        # Distance features
        features["ttc"] = indicators.get("ttc", np.inf)
        features["mttc"] = indicators.get("mttc", np.inf)
        features["pet"] = indicators.get("pet", np.inf)
        features["dtc"] = indicators.get("dtc", 0)
        features["min_gap"] = indicators.get("min_spatial_gap", np.inf)
        features["clearance"] = indicators.get("clearance_distance", np.inf)
        features["psd"] = indicators.get("psd", np.inf)
        
        # Deceleration features
        features["drac"] = indicators.get("drac", 0)
        features["rla"] = indicators.get("rla", 0)
        features["madr"] = indicators.get("madr", 0)
        features["max_decel"] = indicators.get("max_decel", 0)
        features["cpi"] = indicators.get("cpi", 0)
        
        # Severity features
        features["delta_v_impact"] = indicators.get("delta_v_impact", 0)
        features["kinetic_energy"] = indicators.get("kinetic_energy", 0)
        features["pce"] = indicators.get("pce", 0)
        features["csi"] = indicators.get("csi", 0)
        
        # Probability features
        features["collision_probability"] = indicators.get("cp", 0)
        features["crash_potential"] = indicators.get("cpi", 0)
        features["risk_force"] = indicators.get("risk_force", 0)
        
        # Scenario metadata
        features["conflict_type"] = scenario.get("conflict_type", "unknown")
        features["road_type"] = scenario.get("road_type", "unknown")
        features["road_friction"] = scenario.get("road_friction", 0.8)
        features["weather"] = scenario.get("weather", "clear")
        features["lighting"] = scenario.get("lighting", "day")
        features["number_of_lanes"] = scenario.get("number_of_lanes", 1)
        
        # Derived features
        features["speed_ratio"] = features["speed_follow"] / features["speed_lead"] if features["speed_lead"] > 0 else 0
        features["ttc_normalized"] = features["ttc"] / 5.0  # normalize to 0-1 range
        features["gap_normalized"] = features["min_gap"] / 50.0  # normalize to 0-1 range
        features["acceleration_ratio"] = features["relative_accel"] / features["madr"] if features["madr"] > 0 else 0
        
        return features
```

### 2.2 Feature Selection

```python
class FeatureSelection:
    def select_features(self, X: np.ndarray, y: np.ndarray, 
                       feature_names: List[str], 
                       method: str = "random_forest_importance") -> List[str]:
        """Select features based on importance."""
        
        if method == "random_forest_importance":
            rf = RandomForestClassifier(n_estimators=100)
            rf.fit(X, y)
            importances = rf.feature_importances_
            selected = [name for name, imp in zip(feature_names, importances) if imp > np.mean(importances)]
            
        elif method == "mutual_information":
            from sklearn.feature_selection import mutual_info_classif
            mi = mutual_info_classif(X, y)
            selected = [name for name, mi_val in zip(feature_names, mi) if mi_val > np.mean(mi)]
            
        elif method == "recursive_elimination":
            from sklearn.feature_selection import RFE
            from sklearn.ensemble import RandomForestClassifier
            rfe = RFE(RandomForestClassifier(n_estimators=100), n_features_to_select=5)
            rfe.fit(X, y)
            selected = [name for name, sel in zip(feature_names, rfe.support_) if sel]
            
        return selected
```

## 3. Model Implementations

### 3.1 Logistic Regression Model

```python
class LogisticCollisionModel:
    def __init__(self):
        self.model = LogisticRegression()
        self.coefficients = None
        self.intercept = None
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray, feature_names: List[str]):
        """Fit logistic regression to training data."""
        self.model.fit(X_train, y_train)
        self.coefficients = self.model.coef_[0]
        self.intercept = self.model.intercept_[0]
        
        # Compute feature importance (odds ratios)
        self.feature_importance = {
            name: float(np.exp(coeff)) 
            for name, coeff in zip(feature_names, self.coefficients)
        }
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict collision probability."""
        return self.model.predict_proba(X)[:, 1]
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Evaluate model performance."""
        y_pred = self.predict(X_test)
        y_pred_class = (y_pred > 0.5).astype(int)
        
        from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                                     f1_score, roc_auc_score, confusion_matrix)
        
        return {
            "accuracy": accuracy_score(y_test, y_pred_class),
            "precision": precision_score(y_test, y_pred_class),
            "recall": recall_score(y_test, y_pred_class),
            "f1": f1_score(y_test, y_pred_class),
            "auc_roc": roc_auc_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred_class)
        }
```

### 3.2 Random Forest Model

```python
class RandomForestCollisionModel:
    def __init__(self, n_estimators=200, max_depth=10, min_samples_leaf=10):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=42
        )
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        self.model.fit(X_train, y_train)
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        y_pred = self.predict(X_test)
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        return {
            "accuracy": accuracy_score(y_test, (y_pred > 0.5)),
            "precision": precision_score(y_test, (y_pred > 0.5)),
            "recall": recall_score(y_test, (y_pred > 0.5)),
            "f1": f1_score(y_test, (y_pred > 0.5)),
            "auc_roc": roc_auc_score(y_test, y_pred)
        }
    
    def feature_importance(self) -> dict:
        return dict(zip(self.model.feature_names_in_, self.model.feature_importances_))
```

### 3.3 Bayesian Predictive Model

```python
class BayesianCollisionModel:
    """Bayesian model for collision prediction with uncertainty."""
    
    def __init__(self, n_draws=1000):
        self.n_draws = n_draws
        self.trace = None
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """Fit Bayesian logistic regression model."""
        import pymc as pm
        
        n_features = X_train.shape[1]
        
        with pm.Model() as model:
            # Priors
            beta = pm.Normal("beta", mu=0, sigma=1, shape=n_features)
            intercept = pm.Normal("intercept", mu=0, sigma=1)
            
            # Likelihood
            logit_p = pm.math.dot(X_train, beta) + intercept
            p = pm.math.sigmoid(logit_p)
            
            likelihood = pm.Bernoulli("likelihood", p=p, observed=y_train)
        
        self.model = model
        self.trace = pm.sample(draws=self.n_draws, tune=500, chains=4)
        
        return self
    
    def predict(self, X_test: np.ndarray) -> tuple:
        """Predict collision probability with uncertainty."""
        posterior_predictive = pm.sample_posterior_predictive(
            self.trace, 
            vars=["likelihood"],
            predictions=True
        )
        
        # Get mean and CI for each prediction
        y_pred = np.mean(posterior_predictive["likelihood"].mean(dim=["chain", "sample"]).values, axis=1)
        lower = np.percentile(posterior_predictive["likelihood"].values, 2.5, axis=(0,1))
        upper = np.percentile(posterior_predictive["likelihood"].values, 97.5, axis=(0,1))
        
        return y_pred, lower, upper
```

## 4. Model Comparison and Selection

### 4.1 Comparison Metrics

```python
class ModelComparison:
    @staticmethod
    def compare_models(models: dict, X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
        """Compare multiple models on test data."""
        results = {}
        
        for name, model in models.items():
            y_pred = model.predict(X_test)
            y_pred_class = (y_pred > 0.5).astype(int)
            
            results[name] = {
                "accuracy": accuracy_score(y_test, y_pred_class),
                "precision": precision_score(y_test, y_pred_class, zero_division=0),
                "recall": recall_score(y_test, y_pred_class, zero_division=0),
                "f1": f1_score(y_test, y_pred_class, zero_division=0),
                "auc_roc": roc_auc_score(y_test, y_pred)
            }
        
        return pd.DataFrame(results).T
```

### 4.2 Best Model Selection

```python
def select_best_model(comparison_results: pd.DataFrame, primary_metric: str = "auc_roc") -> str:
    """Select best model based on primary metric."""
    return comparison_results[primary_metric].idxmax()
```

## 5. Validation Requirements

### 5.1 Model Performance Thresholds

| Metric | Minimum Threshold | Target Threshold |
|---|-|-|
| Accuracy | ≥ 0.80 | ≥ 0.90 |
| Precision | ≥ 0.75 | ≥ 0.85 |
| Recall | ≥ 0.70 | ≥ 0.85 |
| F1 Score | ≥ 0.75 | ≥ 0.85 |
| AUC-ROC | ≥ 0.80 | ≥ 0.90 |

### 5.2 Statistical Significance

- Compare model performance using paired t-test or McNemar's test
- Report p-values for all comparisons
- Require statistical significance (p < 0.05) for claiming improvement

### 5.3 Cross-Validation

- Use 5-fold cross-validation for model selection
- Use leave-one-jurisdiction-out validation for generalization
- Report mean and std of metrics across folds
