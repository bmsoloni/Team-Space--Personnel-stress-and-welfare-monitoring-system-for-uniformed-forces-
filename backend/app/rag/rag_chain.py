from .vector_store import similarity_search
from .llm_client import call_llm

SYSTEM_PROMPTS = {
    "CHATBOT": """You are a welfare advisor for CRPF (Central Reserve Police Force).
Answer ONLY based on the provided context from official welfare guidelines and SOPs.
Do not speculate beyond the retrieved documents. If the answer is not in the context, say so clearly.
Always be empathetic, professional, and supportive.""",
    "COMPANION": """You are a supportive wellness companion for CRPF personnel.
Be empathetic, non-judgmental, and encouraging. Provide emotional support and practical coping strategies
based on the retrieved mental health resources. Never share personal data with anyone.
Always recommend professional help for serious concerns.""",
    "RECOMMENDATION": """You are a welfare intervention specialist for CRPF.
Based on the provided risk indicators and similar case outcomes, generate a clear, actionable
intervention recommendation grounded in official CRPF welfare protocols.""",
    "EXPLANATION": """You are a welfare officer explaining AI risk analysis results.
Translate the numerical risk factors into clear, compassionate, non-stigmatizing language
grounded in clinical and welfare literature. Focus on systemic factors, not personal blame.""",
}

def run_rag_query(query: str, use_case: str = "CHATBOT", extra_context: str = "") -> dict:
    retrieved = similarity_search(query, n_results=5)
    if not retrieved:
        context = "No specific documentation found. Please consult your welfare officer directly."
    else:
        context = "\n\n".join([
            f"[Source: {d['metadata'].get('source','Unknown')}, Page: {d['metadata'].get('page','?')}]\n{d['content']}"
            for d in retrieved
        ])
    system_prompt = SYSTEM_PROMPTS.get(use_case, SYSTEM_PROMPTS["CHATBOT"])
    prompt = f"""Context from official CRPF welfare documentation:
---
{context}
---
{extra_context}
Question: {query}
Answer (cite sources where possible):"""
    result = call_llm(prompt, system_prompt)
    result["sources"] = [{"document": d["metadata"].get("source"),
                          "page": d["metadata"].get("page"),
                          "relevance_score": round(d["score"], 3),
                          "chunk_preview": d["content"][:200] + "..."} for d in retrieved]
    return result
