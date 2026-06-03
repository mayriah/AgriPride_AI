"""Cerebras Cloud API client wrapper (fallback LLM provider)."""

from typing import Optional

from config import settings


try:
    from cerebras.cloud.sdk import Cerebras
    from cerebras.cloud.sdk import RateLimitError as CerebrasRateLimitError
except ImportError as exc:
    raise ImportError(
        "Missing cerebras-cloud-sdk dependency. Install with: pip install cerebras-cloud-sdk"
    ) from exc


class CerebrasClient:
    """Wraps the Cerebras Cloud chat-completions API with the same interface as GeminiClient."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.CEREBRAS_API_KEY
        self.model = model or settings.CEREBRAS_MODEL
        if not self.api_key:
            raise RuntimeError(
                "CEREBRAS_API_KEY is required for the Cerebras fallback. "
                "Set it in .env or the environment."
            )
        self.client = Cerebras(api_key=self.api_key)

    def generate(self, prompt: str, temperature: float = 0.3, max_output_tokens: int = 512) -> str:
        """Generate a response from Cerebras, raising LLMRateLimitError on quota/rate-limit."""
        from llm_router import LLMRateLimitError  # local import to avoid circular dependency

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=max_output_tokens,
            )
            return response.choices[0].message.content.strip()

        except CerebrasRateLimitError as exc:
            raise LLMRateLimitError(f"Cerebras rate limit exceeded: {exc}") from exc
        except Exception as exc:
            msg = str(exc).lower()
            if any(kw in msg for kw in ("rate limit", "quota", "429", "too many requests")):
                raise LLMRateLimitError(f"Cerebras quota error: {exc}") from exc
            raise
