# search.py

import asyncio
import uuid
import heapq
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
import logging

from .lean_interface import LeanInterface, LeanState, TacticResult
from .planner import InformalPlanner
from .symbolic import SymbolicBooster
from .policy import PolicyModel
from .critic import ValueCritic
from .config import config

logger = logging.getLogger(__name__)

@dataclass
class SearchNode:
    state: LeanState
    parent: Optional['SearchNode'] = None
    tactic_history: List[str] = field(default_factory=list)
    value_score: float = 0.0
    visits: int = 0
    total_reward: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __lt__(self, other):
        # For priority queue: higher value first
        return self.value_score > other.value_score

class HyperionProver:
    def __init__(self, lean_interface: LeanInterface):
        self.lean = lean_interface
        self.planner = InformalPlanner()
        self.booster = SymbolicBooster()
        self.policy = PolicyModel(config.policy_model_name)
        self.critic = ValueCritic(config.critic_model_name)
        self.milestones: List[str] = []
        self.current_milestone_index: int = 0
        self.original_blueprint: str = ""

    async def prove(self, theorem_statement: str) -> Optional[List[str]]:
        """Main entry point."""
        logger.info(f"Starting proof for: {theorem_statement[:80]}...")

        # Phase 1: Blueprint generation & critique
        blueprint = await self.planner.generate_blueprint(theorem_statement)
        self.original_blueprint = await self.planner.critique_and_revise(blueprint)
        self.milestones = self.planner.get_milestones()
        logger.info(f"Generated {len(self.milestones)} milestones")

        # Phase 2: Initialize search with root node
        root_state = LeanState(goal=theorem_statement)
        root = SearchNode(state=root_state)

        # Priority queue for best‑first search (max value)
        queue = [root]
        best_node = root
        visited = set()

        # Phase 3: Search loop
        for iteration in range(config.max_search_nodes):
            if not queue:
                break
            queue.sort(key=lambda x: x.value_score, reverse=True)
            current = queue.pop(0)

            if current.state.is_solved:
                logger.info(f"Solved! Node {current.id}")
                return current.tactic_history

            if current.id in visited:
                continue
            visited.add(current.id)

            # Try symbolic fast‑path
            fast_tac = await self.booster.try_solve(current.state)
            if fast_tac:
                logger.debug(f"Fast‑path hit: {fast_tac}")
                # Execute the tactic
                result = await self.lean.execute(current.state, [fast_tac])
                if result.success and result.new_state:
                    child = SearchNode(
                        state=result.new_state,
                        parent=current,
                        tactic_history=current.tactic_history + [fast_tac],
                        value_score=await self.critic.evaluate(result.new_state)
                    )
                    queue.append(child)
                    if child.state.is_solved:
                        return child.tactic_history
                continue

            # Speculative tactic generation
            batches = await self.policy.generate_batch(current.state, n=config.speculative_batch_size)

            for seq in batches:
                result = await self.lean.execute(current.state, seq)
                if result.success:
                    # Successfully executed entire sequence
                    new_state = result.new_state
                    # Compute value
                    score = await self.critic.evaluate(new_state)
                    # Realignment check
                    await self._maybe_realign(new_state)
                    child = SearchNode(
                        state=new_state,
                        parent=current,
                        tactic_history=current.tactic_history + seq,
                        value_score=score
                    )
                    queue.append(child)
                    if new_state.is_solved:
                        return child.tactic_history
                else:
                    # Partial success? The Lean interface might return an error at a step.
                    # We could keep the state before error, but our mock doesn't support that.
                    # For now, we just log.
                    logger.debug(f"Tactic sequence failed: {result.error_message}")
                    # Record negative example for RL
                    self._log_trace(current.state, seq, result)

            # Value pruning: if current node's value is too low, we skip expanding further
            if current.value_score < config.value_prune_threshold:
                logger.debug(f"Pruning low‑value node {current.id} with score {current.value_score}")

        logger.warning("Search exhausted without solution.")
        return None

    async def _maybe_realign(self, state: LeanState):
        """If state diverges from current milestone, rewrite remaining blueprint."""
        # In practice, we'd check if the current state matches the expected milestone.
        # For simplicity, we always trigger realignment if the milestone index is behind.
        if self.current_milestone_index >= len(self.milestones):
            return
        # Simulate divergence detection (e.g., state goal doesn't contain expected lemma)
        # For mock, just always realign every 5 steps.
        if len(state.goal) > 50 and self.current_milestone_index < len(self.milestones):
            # Use LLM to rewrite the remaining blueprint
            from .prompts import REALIGNMENT_PROMPT_TEMPLATE
            # In real, you'd call the planner's LLM with the state and old blueprint
            logger.info("Triggering blueprint realignment...")
            # For now, do nothing (mock)
            # self.original_blueprint = ...
            # self.milestones = ...

    def _log_trace(self, state: LeanState, tactics: List[str], result: TacticResult):
        """Log for nightly training."""
        # In real, write to JSONL
        from .data_logger import log_failure
        log_failure(state, tactics, result)

    def extract_proof(self, node: SearchNode) -> str:
        """Convert tactic history to a Lean proof."""
        return "by " + "\n  ".join(node.tactic_history)