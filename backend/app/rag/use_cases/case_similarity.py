from ..vector_store import similarity_search
from ...models.risk_score import RiskScore
from sqlalchemy import desc

def find_similar_cases(personnel_id: int) -> dict:
    score = RiskScore.query.filter_by(personnel_id=personnel_id).order_by(desc(RiskScore.score_date)).first()
    if not score:
        return {"cases": [], "message": "No risk score available"}
    factors = score.risk_factors or {}
    top = factors.get("top_factors", [])
    query = f"Cases with {score.overall_risk} stress risk, factors: {', '.join([f['factor'] for f in top[:3]])}"
    results = similarity_search(query, n_results=5)
    return {
        "query": query,
        "cases": [{"content": r["content"][:500], "source": r["metadata"].get("source"),
                   "relevance": round(r["score"], 3)} for r in results],
        "message": f"Found {len(results)} similar cases from knowledge base"
    }
