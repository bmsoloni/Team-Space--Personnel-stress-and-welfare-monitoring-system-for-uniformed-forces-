from flask import current_app

def call_llm(prompt: str, system_prompt: str = "") -> dict:
    use_gemini = current_app.config.get("USE_GEMINI", False)
    if use_gemini:
        return _call_gemini(prompt, system_prompt)
    model_name = current_app.config.get("OLLAMA_MODEL", "llama3:8b")
    return _call_ollama(prompt, system_prompt, model_name)

def _call_ollama(prompt: str, system_prompt: str, model: str) -> dict:
    try:
        import ollama
        base_url = current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        client = ollama.Client(host=base_url)
        response = client.chat(model=model, messages=messages)
        return {"answer": response["message"]["content"], "model_used": model}
    except Exception as e:
        error_str = str(e)
        if "Connection refused" in error_str or "ConnectError" in error_str or "ConnectionError" in error_str:
            msg = (f"The AI model (Ollama / {model}) is not running. "
                   f"Please start Ollama and ensure the model '{model}' is pulled, "
                   f"or configure a Gemini API key in the backend .env file.")
        else:
            msg = f"AI model error: {error_str}. Ensure Ollama is running with model '{model}'."
        return {"answer": msg, "model_used": model}

# Ordered fallback list — primary model first, then alternatives
_GEMINI_FALLBACK_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash",
]

def _call_gemini(prompt: str, system_prompt: str) -> dict:
    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import ServerError

        api_key = current_app.config.get("GEMINI_API_KEY")
        if not api_key:
            return {
                "answer": "Gemini API key is not configured. Please set GEMINI_API_KEY in the backend .env file.",
                "model_used": "gemini-3.5-flash",
            }

        client = genai.Client(api_key=api_key)
        primary_model = current_app.config.get("GEMINI_MODEL", "gemini-3.5-flash")

        # Build fallback list: primary first, then the rest (deduped, preserving order)
        candidates = [primary_model] + [m for m in _GEMINI_FALLBACK_MODELS if m != primary_model]

        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None
        )

        last_error = None
        for model_name in candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                return {"answer": response.text, "model_used": model_name}
            except ServerError as e:
                # 503 overload — try next model
                last_error = e
                continue
            except Exception as e:
                # Non-503 error (auth, not found, etc.) — don't retry
                return {"answer": f"[Gemini Error: {str(e)}]", "model_used": model_name}

        # All models failed
        return {
            "answer": (
                "All Gemini models are currently experiencing high demand. "
                "This is a temporary Google server issue — please try again in a few minutes."
            ),
            "model_used": primary_model,
        }

    except Exception as e:
        return {"answer": f"[Gemini Error: {str(e)}]", "model_used": "gemini-3.5-flash"}
