from ..rag_chain import run_rag_query
from ...models.risk_score import RiskScore
from sqlalchemy import desc

def explain_risk_in_natural_language(personnel_id: int) -> dict:
    score = RiskScore.query.filter_by(personnel_id=personnel_id).order_by(desc(RiskScore.score_date)).first()
    if not score:
        return {"answer": "No risk score available for this personnel.", "sources": []}
    factors = score.risk_factors or {}
    top_factors = factors.get("top_factors", [])
    factor_list = "\n".join([f"- {f['factor'].replace('_',' ').title()}: {f['value']} ({f['direction'].replace('_',' ')})" for f in top_factors[:4]])
    extra = f"""
AI Risk Score Summary (anonymized):
- Risk Level: {score.overall_risk}
- Stress Score: {score.stress_score:.1f}/100
- Key Contributing Factors:
{factor_list}
"""
    query = "Explain in plain language what these risk factors mean for a soldier's welfare and what can be done."
    return run_rag_query(query, use_case="EXPLANATION", extra_context=extra)
