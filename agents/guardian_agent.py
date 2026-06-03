"""Guardian agent: plans transportation and delivery for crops."""

from typing import Optional

from gemini_client import GeminiClient
from tools.logistics_tool import plan_route


class GuardianAgent:
    def __init__(self, memory, gemini: Optional[GeminiClient] = None):
        self.memory = memory
        self.gemini = gemini or GeminiClient()

    def run(self, input_data, scout_result):
        crop = input_data["crop"]
        location = input_data["location"]
        quantity = input_data["quantity_kg"]

        route = plan_route(location, quantity)
        prompt = (
            f"You are a logistics planner for agricultural goods. "
            f"Prepare a safe transport plan for {quantity} kg of {crop} from {location}. "
            "Use the scout analysis to determine risk points and timing. "
            f"Scout summary: {scout_result['analysis']}. "
            f"Route data: {route}."
        )

        plan = self.gemini.generate(prompt)
        result = {
            "route": route,
            "plan": plan,
        }

        self.memory.store_transient("guardian", result)
        return result
