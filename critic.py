# critic.py

import asyncio
from typing import List
from .lean_interface import LeanState
from .prompts import VALUE_CRITIC_SYSTEM_PROMPT

class ValueCritic:
    """Lightweight model to score Lean states."""
    def __init__(self, model_name: str):
        self.model_name = model_name
        # Load quantized model (mock)
        self.model = None

    async def evaluate(self, state: LeanState) -> float:
        """Return a score between -1 and 1."""
        # In real: format state into a prompt, call model, extract score
        # Mock: heuristic based on goal length and keywords
        goal = state.goal.lower()
        if "solved" in goal or "no goals" in goal:
            return 1.0
        if "error" in goal:
            return -1.0
        # Longer goals might be harder
        score = 1.0 - min(1.0, len(goal) / 1000)
        # If it's the final goal, give bonus
        if "qed" in goal:
            score += 0.2
        return max(-1.0, min(1.0, score))