from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, Optional


class LLMService:
    """Provider fallback + caching. Uses Redis if REDIS_URL is set, else in-memory.
    Providers (in order): Groq → Gemini → OpenAI.
    """

    def __init__(self) -> None:
        self._cache = None
        self._redis = None

        # Optional Redis cache
        try:
            import redis  # type: ignore

            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self._redis = redis.from_url(redis_url)
        except Exception:
            self._redis = None

        # Prepare providers based on available API keys
        self._providers: Dict[str, Any] = {}
        
        def is_placeholder(key: str | None) -> bool:
            if not key: return True
            placeholders = ["sk_your_", "your_", "key_here", "insert_", "ENTER_YOUR"]
            return any(p.lower() in key.lower() for p in placeholders)

        groq_key = os.getenv("GROQ_API_KEY")
        if not is_placeholder(groq_key):
            try:
                from groq import Groq  # type: ignore
                # Set max_retries=0 to fallback quickly to other providers instead of waiting
                self._providers["groq"] = Groq(api_key=groq_key, max_retries=0)
            except Exception:
                pass

        gemini_key = os.getenv("GEMINI_API_KEY")
        if not is_placeholder(gemini_key):
            try:
                import google.generativeai as genai  # type: ignore
                genai.configure(api_key=gemini_key)
                # Use models/ prefix as shown in list_models()
                self._providers["gemini"] = genai.GenerativeModel("models/gemini-2.0-flash")
            except Exception:
                pass

        openai_key = os.getenv("OPENAI_API_KEY")
        if not is_placeholder(openai_key):
            try:
                from openai import OpenAI  # type: ignore
                self._providers["openai"] = OpenAI(api_key=openai_key)
            except Exception:
                pass

        self._order = ["groq", "gemini", "openai"]

    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            if self._redis is not None:
                v = self._redis.get(key)
                return json.loads(v) if v else None
        except Exception:
            pass
        return None

    def _cache_set(self, key: str, value: Dict[str, Any], ttl: int = 86400) -> None:
        try:
            if self._redis is not None:
                self._redis.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    async def complete(self, prompt: str, max_tokens: int = 256) -> Dict[str, Any]:
        cache_key = f"llm:{hashlib.md5(prompt.encode()).hexdigest()}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        # Models to try for each provider
        # Updated to use currently valid Groq models (llama-3.1-8b-instant instead of 8192)
        groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        
        if not self._providers:
            import logging
            logging.getLogger(__name__).error("No providers loaded. Checking usage...")
            # Detailed debug for user
            if is_placeholder(groq_key):
                logging.getLogger(__name__).warning("Groq: SKIPPED (Key invalid or empty)")
            if is_placeholder(gemini_key):
                logging.getLogger(__name__).warning("Gemini: SKIPPED (Key invalid or empty)")
            if is_placeholder(openai_key):
                logging.getLogger(__name__).warning("OpenAI: SKIPPED (Key invalid or empty)")
                
            raise RuntimeError("No LLM providers initialized. Please check your .env file and ensure you have valid API keys for Groq, Gemini, or OpenAI.")
            
        last_err: Optional[Exception] = None
        
        # Log which providers are available
        # logger.info(f"Available providers: {list(self._providers.keys())}")

        for name in self._order:
            if name not in self._providers:
                # logger.debug(f"Skipping {name} (not configured)")
                continue
            
            try:
                # logger.info(f"Attempting generation with {name}...")
                
                if name == "groq":
                    client = self._providers[name]
                    # Try different models if one hits rate limit
                    for model in groq_models:
                        try:
                            resp = client.chat.completions.create(
                                model=model,
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=max_tokens,
                            )
                            result = {"provider": name, "model": model, "text": resp.choices[0].message.content}
                            self._cache_set(cache_key, result)
                            return result
                        except Exception as e:
                            import logging
                            logging.getLogger(__name__).warning(f"Groq ({model}) failed: {e}")
                            err_str = str(e).lower()
                            # Handle Rate Limits (429) AND Bad Requests (400 - e.g. decommissioned models)
                            if "rate_limit" in err_str or "429" in err_str or "400" in err_str or "decommissioned" in err_str:
                                last_err = e
                                continue # try next model
                            raise e

                elif name == "gemini":
                    # Try a few common model names in sequence if the primary one fails
                    # Favoring 2.0 or generic 'flash-latest' with models/ prefix
                    gemini_models = [
                        "gemini-1.5-flash-latest",
                        "gemini-1.5-flash",
                        "models/gemini-1.5-flash-latest", 
                        "models/gemini-1.5-flash", 
                        "gemini-2.0-flash-exp",
                        "models/gemini-2.0-flash-exp"
                    ]
                    
                    inner_err = None
                    for model_name in gemini_models:
                        try:
                            import google.generativeai as genai
                            m = genai.GenerativeModel(model_name)
                            resp = m.generate_content(prompt)
                            result = {"provider": name, "model": model_name, "text": getattr(resp, "text", "")}
                            self._cache_set(cache_key, result)
                            return result
                        except Exception as e:
                            inner_err = e
                            continue
                    
                    import logging
                    logging.getLogger(__name__).warning(f"Gemini failed all models: {inner_err}")
                    raise inner_err or Exception("All Gemini models failed")
                
                elif name == "openai":
                    client = self._providers[name]
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                    )
                    result = {"provider": name, "text": resp.choices[0].message.content}
                    self._cache_set(cache_key, result)
                    return result
                
                else:
                    continue

            except Exception as e:  # try next provider
                last_err = e
                continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_err}. Check your API keys and quotas.")


