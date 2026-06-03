"""Guard agent: reviews analysis for bias, risk, and safety."""

import re
from typing import Optional

from gemini_client import GeminiClient


class GuardAgent:
    def __init__(self, memory, gemini: Optional[GeminiClient] = None):
        self.memory = memory
        self.gemini = gemini or GeminiClient()

    def validate(self, scout_result):
        prompt = (
            "You are an ethics reviewer for agricultural advice. "
            "Review the following recommendation and identify any unsafe, biased, "
            "or financially risky guidance. "
            "If the recommendation is acceptable, reply with only 'APPROVED'. "
            "If it is not acceptable, reply with only 'REJECTED' and then briefly explain why. "
            f"Scout analysis: {scout_result['analysis']}\n"
            f"Market data: {scout_result.get('prices')}\n"
            f"Weather data: {scout_result.get('weather')}"
        )

        review = self.gemini.generate(prompt)
        normalized = review.strip()
        lower = normalized.lower()

        match = re.match(r"(?i)^(approved|rejected)\b", normalized)
        if match:
            status = match.group(1).lower()
        elif "reject" in lower or "unsafe" in lower:
            status = "rejected"
        elif "approve" in lower:
            status = "approved"
        else:
            status = "rejected"

        result = {
            "status": status,
            "review": review,
        }

        self.memory.store_transient("guard", result)
        return result
