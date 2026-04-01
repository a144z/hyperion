# policy.py

import asyncio
import random
from typing import List
from .lean_interface import LeanState

class PolicyModel:
    """Generates sequences of tactics (macro‑tactics)."""
    def __init__(self, model_name: str):
        self.model_name = model_name
        # Load model (mock for now)
        self.model = None

    async def generate_batch(self, state: LeanState, n: int = 3) -> List[List[str]]:
        """Generate n tactic sequences, each of length 3‑5."""
        # In real: call the LLM with the goal as context
        # For mock: return some dummy tactics
        # We'll simulate that sometimes the batch contains a "fail" to cause errors.
        batches = []
        for _ in range(n):
            length = random.randint(3, 5)
            seq = [f"tactic_{i}" for i in range(length)]
            # Occasionally insert a failing tactic for testing
            if random.random() < 0.2:
                seq[1] = "fail"
            batches.append(seq)
        return batches

    async def evaluate_state_value(self, state: LeanState) -> float:
        """Used by value critic. For now, just a heuristic."""
        # In real: call the value model
        if "solved" in state.goal.lower():
            return 1.0
        if "error" in state.goal.lower():
            return -1.0
        return 0.0