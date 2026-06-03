"""Hunt agent: synthesizes recommendations into a final action plan."""

from typing import Optional

from gemini_client import GeminiClient


class HuntAgent:
    def __init__(self, memory, gemini: Optional[GeminiClient] = None):
        self.memory = memory
        self.gemini = gemini or GeminiClient()

    def run(self, scout_result, guardian_result):
        prompt = (
            "You are a workflow manager for an agricultural support system. "
            "Review the scout market analysis and the guardian logistics plan, "
            "then create a short, practical action plan for the farmer. "
            f"Scout result: {scout_result['analysis']} "
            f"Guardian plan: {guardian_result['plan']}"
        )

        summary = self.gemini.generate(prompt)
        result = {
            "summary": summary,
        }

        self.memory.store_transient("hunt", result)
        return result
