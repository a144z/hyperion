# planner.py

import asyncio
from typing import List, Dict, Optional
import logging
from . import config
from .prompts import *

logger = logging.getLogger(__name__)

class LLMClient:
    """Mock LLM client; replace with real API calls."""
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # In real code: call Claude/DeepSeek/OpenAI
        # For now, return dummy
        if "MILESTONE:" in user_prompt:
            return "Here is the proof...\n\nMILESTONE: Lemma 1: Base case\nMILESTONE: Lemma 2: Inductive step\nMILESTONE: Conclusion"
        elif "Feedback" in user_prompt:
            return "The proof looks correct. No gaps found."
        else:
            return "Revised proof: ..."

class InformalPlanner:
    def __init__(self):
        self.llm = LLMClient()  # Replace with actual model
        self.milestones: List[str] = []

    async def generate_blueprint(self, theorem_statement: str) -> str:
        """Generate informal proof and milestones."""
        user_prompt = PLANNER_PROMPT_TEMPLATE.format(theorem=theorem_statement)
        response = await self.llm.generate(PLANNER_SYSTEM_PROMPT, user_prompt)

        # Parse milestones
        self.milestones = []
        for line in response.split("\n"):
            if line.startswith("MILESTONE:"):
                self.milestones.append(line[len("MILESTONE:"):].strip())
        # If no explicit milestones, use a default
        if not self.milestones:
            self.milestones = ["Main proof"]
        return response

    async def critique_and_revise(self, blueprint: str) -> str:
        """Multi‑agent critique: review and possibly revise."""
        if not config.use_multi_agent_critique:
            return blueprint

        user_prompt = CRITIC_PROMPT_TEMPLATE.format(proof=blueprint)
        feedback = await self.llm.generate(CRITIC_SYSTEM_PROMPT, user_prompt)

        if "correct" in feedback.lower() or "no gaps" in feedback.lower():
            return blueprint

        # Revise: ask the planner to incorporate feedback
        revise_prompt = f"Original proof:\n{blueprint}\n\nCritic feedback:\n{feedback}\n\nPlease produce a revised proof."
        revised = await self.llm.generate(PLANNER_SYSTEM_PROMPT, revise_prompt)
        return revised

    def get_milestones(self) -> List[str]:
        return self.milestones