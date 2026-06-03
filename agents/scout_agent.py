"""Scout agent: analyzes market and weather for crop selling decisions."""

import re
from typing import Optional

from gemini_client import GeminiClient
from tools.market_tool import get_market_prices
from tools.weather_tool import get_weather


class ScoutAgent:
    def __init__(self, memory, gemini: Optional[GeminiClient] = None):
        self.memory = memory
        self.gemini = gemini or GeminiClient()

    def _has_required_sections(self, analysis: str) -> bool:
        required = ["SELL ADVICE", "RISK", "PLAN B"]
        return all(re.search(rf"(?m)^\s*{section}:?", analysis, re.IGNORECASE) for section in required)

    def _get_missing_sections(self, analysis: str):
        required = ["SELL ADVICE", "RISK", "PLAN B"]
        return [section for section in required if not re.search(rf"(?m)^\s*{section}:?", analysis, re.IGNORECASE)]

    def _contains_unrelated_terms(self, analysis: str) -> bool:
        unrelated = ["land", "property", "real estate", "asset-backed", "asset backed", "loan from friends", "bridging finance"]
        return any(re.search(rf"\b{re.escape(term)}\b", analysis, re.IGNORECASE) for term in unrelated)

    def run(self, input_data):
        crop = input_data["crop"]
        location = input_data["location"]
        quantity = input_data["quantity_kg"]
        days_to_cash = input_data["need_cash_in_days"]

        prices = get_market_prices(crop, location)
        weather = get_weather(location)

        prompt = (
            f"You are an agricultural market analyst. A farmer has {quantity} kg of {crop} "
            f"in {location} and needs cash in {days_to_cash} days. "
            "Use the market price data and weather signal to recommend whether the farmer "
            "should sell now, hold stock, or look for a different market. "
            "Explain risks, a fair price range, and the best next step. "
            "Answer exactly in three plain text sections with these headings: "
            "SELL ADVICE:, RISK:, and PLAN B:. "
            "Do not use markdown subheadings, bullet lists, or additional headings. "
            "Keep each section concise and specific to the crop, location, weather, and cash timing. "
            "Do not mention land, property, real estate, or unrelated assets. "
            "If the forecast indicates rain in the next five days, explain why selling now is safer than waiting. "
            f"Market data: {prices}. Weather data: {weather}."
        )

        analysis = self.gemini.generate(prompt, temperature=0.0, max_output_tokens=768)
        missing = self._get_missing_sections(analysis)
        invalid = self._contains_unrelated_terms(analysis)

        if missing or invalid:
            follow_up = (
                "The previous response is not acceptable because it is incomplete or contains unrelated content. "
                f"Provide the missing sections only: {', '.join(missing)}. " if missing else ""
                "Do not mention land, property, real estate, loans, or unrelated asset types. "
                "Keep the format exactly as headings followed by clear guidance for the crop. "
                f"Previous response:\n{analysis}"
            )
            additional = self.gemini.generate(follow_up, temperature=0.0, max_output_tokens=768)
            analysis = analysis.strip() + "\n\n" + additional.strip()
            missing = self._get_missing_sections(analysis)
            invalid = self._contains_unrelated_terms(analysis)

        if missing or invalid:
            follow_up = (
                "The response is still incorrect. Add any remaining missing sections and remove any unrelated references. "
                "The answer should focus only on the crop, market price, weather, and storage risks. "
                f"Current response:\n{analysis}"
            )
            additional = self.gemini.generate(follow_up, temperature=0.0, max_output_tokens=768)
            analysis = analysis.strip() + "\n\n" + additional.strip()

        result = {
            "prices": prices,
            "weather": weather,
            "analysis": analysis,
        }

        self.memory.store_transient("scout", result)
        return result
