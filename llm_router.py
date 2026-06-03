"""LLM Router — tries providers in order, falling back on rate-limit / quota errors.

Provider order is controlled by the LLM_PROVIDER_ORDER env variable (default: gemini,cohere,cerebras).
Any provider whose API key is not configured is skipped silently.

Usage (drop-in replacement for GeminiClient):
    from llm_router import LLMRouter
    llm = LLMRouter()
    text = llm.generate("What is the best time to sell maize?")
"""

import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class LLMRateLimitError(Exception):
    """Raised by any LLM client wrapper when the provider returns a rate-limit or quota error."""


class LLMRouter:
    """Tries each configured LLM provider in order.

    Falls over to the next provider only on LLMRateLimitError.
    All other exceptions propagate immediately so bugs are visible.
    """

    def __init__(self):
        self._providers = self._build_provider_list()
        if not self._providers:
            raise RuntimeError(
                "LLMRouter: no providers could be initialised. "
                "Configure at least one of GEMINI_API_KEY, COHERE_API_KEY, CEREBRAS_API_KEY in .env."
            )

    # ------------------------------------------------------------------
    # Public interface — identical signature to GeminiClient.generate()
    # ------------------------------------------------------------------

    def generate(self, prompt: str, temperature: float = 0.3, max_output_tokens: int = 512) -> str:
        """Generate a completion, falling back through providers on rate-limit errors."""
        last_error: Optional[Exception] = None

        for name, client in self._providers:
            try:
                logger.info("LLMRouter: calling provider '%s'", name)
                result = client.generate(
                    prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
                if name != self._providers[0][0]:
                    logger.warning(
                        "LLMRouter: primary provider unavailable; response from '%s'.", name
                    )
                return result

            except LLMRateLimitError as exc:
                logger.warning(
                    "LLMRouter: provider '%s' hit rate-limit/quota (%s). Trying next provider.",
                    name,
                    exc,
                )
                last_error = exc
                continue  # try the next provider

        raise RuntimeError(
            f"LLMRouter: all providers exhausted. Last error: {last_error}"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_provider_list(self):
        """Instantiate providers in the configured order, skipping those without API keys."""
        order = [p.strip().lower() for p in settings.LLM_PROVIDER_ORDER.split(",") if p.strip()]
        providers = []

        builder_map = {
            "gemini": self._try_build_gemini,
            "cohere": self._try_build_cohere,
            "cerebras": self._try_build_cerebras,
        }

        for name in order:
            builder = builder_map.get(name)
            if builder is None:
                logger.warning("LLMRouter: unknown provider '%s' in LLM_PROVIDER_ORDER — skipping.", name)
                continue
            client = builder()
            if client is not None:
                providers.append((name, client))

        return providers

    @staticmethod
    def _try_build_gemini():
        if not settings.GEMINI_API_KEY:
            logger.info("LLMRouter: GEMINI_API_KEY not set — Gemini skipped.")
            return None
        try:
            from gemini_client import GeminiClient
            return GeminiClient()
        except Exception as exc:
            logger.warning("LLMRouter: failed to initialise Gemini client: %s", exc)
            return None

    @staticmethod
    def _try_build_cohere():
        if not settings.COHERE_API_KEY:
            logger.info("LLMRouter: COHERE_API_KEY not set — Cohere skipped.")
            return None
        try:
            from cohere_client import CohereClient
            return CohereClient()
        except Exception as exc:
            logger.warning("LLMRouter: failed to initialise Cohere client: %s", exc)
            return None

    @staticmethod
    def _try_build_cerebras():
        if not settings.CEREBRAS_API_KEY:
            logger.info("LLMRouter: CEREBRAS_API_KEY not set — Cerebras skipped.")
            return None
        try:
            from cerebras_client import CerebrasClient
            return CerebrasClient()
        except Exception as exc:
            logger.warning("LLMRouter: failed to initialise Cerebras client: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def active_providers(self) -> list[str]:
        """Returns the names of all successfully initialised providers in priority order."""
        return [name for name, _ in self._providers]

    def __repr__(self) -> str:
        return f"LLMRouter(providers={self.active_providers})"
