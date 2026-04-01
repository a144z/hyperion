# selfplay.py

import random
import asyncio
from typing import List
from .lean_interface import LeanState, LeanInterface
from .search import HyperionProver
from .data_logger import log_success
from .config import config

class SelfPlayGenerator:
    """Mutate proven theorems to create new problems."""
    def __init__(self, lean_interface: LeanInterface):
        self.lean = lean_interface
        self.proven_theorems: List[str] = []  # In real, load from DB

    async def mutate(self, theorem: str) -> str:
        """Randomly alter constants, hypotheses, or conclusions."""
        # Simple mutations for demonstration
        # In reality, you'd use an LLM to generate meaningful variations.
        mutations = [
            lambda s: s.replace("ℕ", "ℤ"),
            lambda s: s.replace("+", "*"),
            lambda s: s.replace("a + b", "a * b"),
            lambda s: s.replace("∀", "∃"),
            lambda s: s + " ∧ true",
        ]
        mutation = random.choice(mutations)
        return mutation(theorem)

    async def generate_curriculum(self, num_problems: int = 10):
        """Generate new problems by mutating proven ones and attempt to prove them."""
        if not self.proven_theorems:
            print("No proven theorems yet; skipping self‑play.")
            return

        for _ in range(num_problems):
            parent = random.choice(self.proven_theorems)
            new_thm = await self.mutate(parent)
            print(f"Generated: {new_thm}")

            # Attempt to prove with Hyperion
            prover = HyperionProver(self.lean)
            proof = await prover.prove(new_thm)
            if proof:
                print(f"New theorem proved: {new_thm}")
                log_success(LeanState(goal=new_thm), proof)
                self.proven_theorems.append(new_thm)  # Add to proven set
            else:
                print(f"Failed to prove: {new_thm}")

    def add_proven(self, theorem: str):
        self.proven_theorems.append(theorem)