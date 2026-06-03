"""Cohere API client wrapper (fallback LLM provider)."""

from typing import Optional

from config import settings


try:
    import cohere
except ImportError as exc:
    raise ImportError(
        "Missing cohere dependency. Install with: pip install cohere"
    ) from exc


class CohereClient:
    """Wraps the Cohere chat API with the same interface as GeminiClient."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.COHERE_API_KEY
        self.model = model or settings.COHERE_MODEL
        if not self.api_key:
            raise RuntimeError(
                "COHERE_API_KEY is required for the Cohere fallback. "
                "Set it in .env or the environment."
            )
        self.client = cohere.Client(api_key=self.api_key)

    def generate(self, prompt: str, temperature: float = 0.3, max_output_tokens: int = 512) -> str:
        """Generate a response from Cohere, raising LLMRateLimitError on quota/rate-limit."""
        from llm_router import LLMRateLimitError  # local import to avoid circular dependency

        try:
            response = self.client.chat(
                model=self.model,
                message=prompt,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
            return response.text.strip()

        except cohere.errors.TooManyRequestsError as exc:
            raise LLMRateLimitError(f"Cohere rate limit exceeded: {exc}") from exc
        except Exception as exc:
            msg = str(exc).lower()
            if any(kw in msg for kw in ("rate limit", "quota", "429", "too many requests")):
                raise LLMRateLimitError(f"Cohere quota error: {exc}") from exc
            raise
