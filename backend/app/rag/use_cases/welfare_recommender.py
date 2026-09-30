from ..rag_chain import run_rag_query
from ...models.risk_score import RiskScore
from sqlalchemy import desc

def get_welfare_recommendation(personnel_id: int) -> dict:
    score = RiskScore.query.filter_by(personnel_id=personnel_id).order_by(desc(RiskScore.score_date)).first()
    if not score:
        return {"answer": "No risk score found for this personnel. Conduct a manual assessment.", "sources": []}
    factors = score.risk_factors or {}
    top_factors = factors.get("top_factors", [])
    factor_text = "\n".join([f"- {f['factor']}: {f['value']} (contribution: {f['contribution']})" for f in top_factors[:4]])
    extra = f"""
Anonymized Risk Profile:
- Overall Risk Level: {score.overall_risk}
- Stress Score: {score.stress_score:.1f}/100
- Burnout Score: {score.burnout_score:.1f}/100
- Key Risk Factors:
{factor_text}
"""
    query = f"What welfare interventions are recommended for a {score.overall_risk} risk personnel with the above profile?"
    return run_rag_query(query, use_case="RECOMMENDATION", extra_context=extra)
