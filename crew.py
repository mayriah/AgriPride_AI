"""Crew orchestration for AgriPride AI."""

from llm_router import LLMRouter
from memory.trail_memory import TrailMemory
from agents.scout_agent import ScoutAgent
from agents.guardian_agent import GuardianAgent
from agents.hunt_agent import HuntAgent
from agents.guard_agent import GuardAgent
from workflows.rank_rules import RankEngine
from workflows.escalation import escalate


class Crew:
    def __init__(self, input_data, llm=None):
        self.input_data = input_data
        self.memory = TrailMemory()
        # Accept LLMRouter or a legacy GeminiClient (e.g. injected in tests)
        self.gemini = llm or LLMRouter()
        self.scout = ScoutAgent(self.memory, self.gemini)
        self.guardian = GuardianAgent(self.memory, self.gemini)
        self.guard = GuardAgent(self.memory, self.gemini)
        self.hunt = HuntAgent(self.memory, self.gemini)
        self.rank_engine = RankEngine()

    def kickoff(self):
        scout_result = self.scout.run(self.input_data)
        validation = self.guard.validate(scout_result)

        if validation["status"] != "approved":
            return {
                "status": "rejected",
                "guard_review": validation,
                "escalation": escalate(validation),
            }

        rank_action = self.rank_engine.validate_scout_output(scout_result["prices"])
        if rank_action != "ALLOW":
            return {
                "status": "escalated",
                "reason": rank_action,
                "scout": scout_result,
                "escalation": escalate({"reason": rank_action}),
            }

        guardian_result = self.guardian.run(self.input_data, scout_result)
        final_result = self.hunt.run(scout_result, guardian_result)

        self.memory.store_archival("final_result", final_result)

        return {
            "status": "completed",
            "scout": scout_result,
            "guardian": guardian_result,
            "guard_review": validation,
            "final": final_result,
        }


def build_crew(input_data):
    return Crew(input_data)
