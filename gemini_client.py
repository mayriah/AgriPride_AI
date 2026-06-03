"""Gemini API client wrapper."""
import os

from typing import Optional

from config import settings

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted, TooManyRequests
except ImportError as exc:
    raise ImportError(
        "Missing google-generativeai dependency. Install with: pip install google-generativeai"
    ) from exc


# Imported here to avoid circular import; llm_router imports clients, not the other way around.
def _get_rate_limit_error():
    from llm_router import LLMRateLimitError  # noqa: PLC0415
    return LLMRateLimitError


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required. Set it in .env or the environment."
            )

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name=self.model)

    def generate(self, prompt: str, temperature: float = 0.3, max_output_tokens: int = 512) -> str:
        LLMRateLimitError = _get_rate_limit_error()
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        try:
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config,
            )
        except (ResourceExhausted, TooManyRequests) as exc:
            raise LLMRateLimitError(f"Gemini rate limit / quota exceeded: {exc}") from exc
        except Exception as exc:
            # Surface quota errors that arrive as generic exceptions (e.g. 429 wrapped in grpc)
            msg = str(exc).lower()
            if any(kw in msg for kw in ("quota", "rate limit", "resource exhausted", "429")):
                raise LLMRateLimitError(f"Gemini quota error: {exc}") from exc
            raise

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content"):
                content = candidate.content
                if isinstance(content, list) and content:
                    part = content[0]
                    if hasattr(part, "text") and part.text:
                        return part.text.strip()
                elif hasattr(content, "text") and content.text:
                    return content.text.strip()

        return str(response).strip()

