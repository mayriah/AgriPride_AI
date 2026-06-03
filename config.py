"""Configuration and environment helpers."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    ENV: str = os.getenv("ENV", "development")
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))

    # --- Primary LLM: Gemini ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- Fallback LLM 1: Cohere ---
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "command-a-03-2025")

    # --- Fallback LLM 2: Cerebras ---
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    CEREBRAS_MODEL: str = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")

    # --- Router: comma-separated order of providers to try ---
    LLM_PROVIDER_ORDER: str = os.getenv("LLM_PROVIDER_ORDER", "gemini,cohere,cerebras")


settings = Settings()


def validate_settings():
    """Warn (don't crash) if primary LLM key is missing; router handles fallbacks."""
    configured = []
    if settings.GEMINI_API_KEY:
        configured.append("gemini")
    if settings.COHERE_API_KEY:
        configured.append("cohere")
    if settings.CEREBRAS_API_KEY:
        configured.append("cerebras")

    if not configured:
        raise RuntimeError(
            "No LLM API keys configured. Set at least one of: "
            "GEMINI_API_KEY, COHERE_API_KEY, CEREBRAS_API_KEY in .env."
        )
