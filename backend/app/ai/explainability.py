import numpy as np

def get_shap_explanation(features: dict, stress_score: float, burnout_score: float) -> dict:
    """Generate SHAP-like factor attribution. Uses real SHAP if model loaded, else rule-based."""
    try:
        import shap
        from .model_registry import get_model
        from .feature_engineering import get_feature_array
        model = get_model("stress")
        scaler = get_model("scaler")
        if model:
            X = get_feature_array(features)
            Xs = scaler.transform(X) if scaler else X
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(Xs)
            feature_names = list(features.keys())[2:]  # skip personnel_id, anon_id
            vals = shap_vals[0][0] if isinstance(shap_vals, list) else shap_vals[0]
            factors = [{"factor": n, "value": round(float(features.get(n,0)),2),
                        "contribution": round(float(v)*100, 2),
                        "direction": "increases_risk" if v > 0 else "decreases_risk"}
                       for n, v in zip(feature_names, vals)]
            factors.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            return {"top_factors": factors[:5], "method": "shap"}
    except Exception:
        pass
    return _rule_based_explanation(features, stress_score)

def _rule_based_explanation(features: dict, score: float) -> dict:
    factors = [
        {"factor": "deployment_duration_days",
         "value": features.get("deployment_duration_days", 0),
         "contribution": round(min(features.get("deployment_duration_days", 0) / 365 * 30, 30), 2),
         "direction": "increases_risk"},
        {"factor": "leave_denied_90d",
         "value": features.get("leave_denied_90d", 0),
         "contribution": round(features.get("leave_denied_90d", 0) * 5, 2),
         "direction": "increases_risk"},
        {"factor": "consecutive_duty_days",
         "value": features.get("consecutive_duty_days", 0),
         "contribution": round(features.get("consecutive_duty_days", 0) * 1.5, 2),
         "direction": "increases_risk"},
        {"factor": "wellness_score_avg",
         "value": features.get("wellness_score_avg", 50),
         "contribution": round((50 - features.get("wellness_score_avg", 50)) * 0.2, 2),
         "direction": "decreases_risk" if features.get("wellness_score_avg", 50) > 50 else "increases_risk"},
    ]
    factors.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    return {"top_factors": factors, "method": "rule_based"}
