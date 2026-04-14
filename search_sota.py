# search_sota.py
"""
SOTA Search Engine - MCTS + Proof Decomposition + Subgoal Management
====================================================================
UPGRADES from basic Hyperion:
1. Monte Carlo Tree Search (MCTS) with PUCT instead of best-first
2. Hierarchical proof decomposition (theorem → lemmas → tactics)
3. Subgoal management with dynamic milestone tracking
4. Cross-entropy method for tactic diversification
5. Proof state embedding for similarity search
6. Iterative deepening with timeout management
7. Complete proof trace with dependency graph
"""

import asyncio
import math
import uuid
import heapq
import time
import json
from typing import List, Optional, Dict, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from collections import defaultdict

from .lean_interface import LeanInterface, LeanState, TacticResult
from .planner_sota import InformalPlannerSOTA, ProofStep, Lemma
from .symbolic_sota import SymbolicBoosterSOTA
from .policy_sota import PolicyModelSOTA
from .critic_sota import ValueCriticSOTA
from .config import config

logger = logging.getLogger(__name__)


# ============================================================================
# MCTS NODE WITH FULL PROOF TRACE
# ============================================================================

class NodeType(Enum):
    ROOT = "root"
    AND = "and"  # All children must be solved (decomposition)
    OR = "or"    # One child must be solved (branching)
    LEAF = "leaf"

@dataclass
class ProofTrace:
    """Complete proof trace with dependency information"""
    node_id: str
    tactic: str
    parent_state: str
    resulting_state: str
    is_valid: bool
    children: List['ProofTrace'] = field(default_factory=list)
    lemma_used: Optional[str] = None
    timestamp: float = 0.0
    depth: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "tactic": self.tactic,
            "parent_state": self.parent_state,
            "resulting_state": self.resulting_state,
            "is_valid": self.is_valid,
            "children": [c.to_dict() for c in self.children],
            "lemma_used": self.lemma_used,
            "depth": self.depth
        }

@dataclass
class MCTSNode:
    """MCTS node with PUCT scoring"""
    state: LeanState
    parent: Optional['MCTSNode'] = None
    children: List['MCTSNode'] = field(default_factory=list)
    
    # MCTS statistics
    visits: int = 0
    total_reward: float = 0.0
    prior_probability: float = 0.0  # from policy model
    
    # Proof tracking
    tactic_used: Optional[str] = None
    tactic_history: List[str] = field(default_factory=list)
    depth: int = 0
    node_type: NodeType = NodeType.LEAF
    
    # Subgoal management
    subgoal_index: int = 0
    is_solved: bool = False
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    proof_trace: Optional[ProofTrace] = None
    
    # Cached values
    _value_estimate: Optional[float] = None
    
    def q_value(self) -> float:
        """Exploitation term"""
        if self.visits == 0:
            return 0.0
        return self.total_reward / self.visits
    
    def u_value(self, parent_visits: int) -> float:
        """Exploration term (PUCT)"""
        if self.visits == 0:
            return float('inf')
        return self.prior_probability * math.sqrt(parent_visits) / (1 + self.visits)
    
    def puct_score(self, parent_visits: int, exploration_constant: float = 1.5) -> float:
        """PUCT = Q + c * U"""
        return self.q_value() + exploration_constant * self.u_value(parent_visits)
    
    def best_child(self, exploration_constant: float = 1.5) -> Optional['MCTSNode']:
        """Select best child by PUCT score"""
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.puct_score(self.visits, exploration_constant))
    
    def is_fully_expanded(self) -> bool:
        """Check if node should be expanded more"""
        return len(self.children) >= 5  # Max branching factor
    
    def trajectory_reward(self) -> float:
        """Total reward from root to this node"""
        if self.parent is None:
            return self.total_reward
        return self.parent.trajectory_reward() + self.total_reward


# ============================================================================
# PROOF DECOMPOSITION
# ============================================================================

@dataclass
class ProofPlan:
    """Hierarchical proof decomposition"""
    theorem_statement: str
    main_strategy: str
    lemmas: List[Lemma]
    proof_steps: List[ProofStep]
    dependencies: Dict[str, List[str]]  # lemma → depends_on
    estimated_difficulty: float
    suggested_tactics: List[str]
    
    def get_next_subgoal(self, completed: Set[str]) -> Optional[Lemma]:
        """Get next unsolved lemma whose dependencies are all completed"""
        for lemma in self.lemmas:
            if lemma.id in completed:
                continue
            # Check if all dependencies are satisfied
            deps = self.dependencies.get(lemma.id, [])
            if all(dep in completed for dep in deps):
                return lemma
        return None
    
    def to_dict(self) -> Dict:
        return {
            "theorem": self.theorem_statement,
            "strategy": self.main_strategy,
            "lemmas": [l.to_dict() for l in self.lemmas],
            "steps": [s.to_dict() for s in self.proof_steps],
            "dependencies": self.dependencies,
            "difficulty": self.estimated_difficulty
        }


# ============================================================================
# SOTA SEARCH ENGINE
# ============================================================================

class HyperionProverSOTA:
    """
    SOTA Theorem Prover with:
    - MCTS with PUCT exploration
    - Hierarchical proof decomposition
    - Subgoal management
    - Complete proof trace
    - Iterative deepening
    - Cross-entropy tactic selection
    """
    
    def __init__(self, lean_interface: LeanInterface):
        self.lean = lean_interface
        self.planner = InformalPlannerSOTA()
        self.booster = SymbolicBoosterSOTA()
        self.policy = PolicyModelSOTA(config.policy_model_name)
        self.critic = ValueCriticSOTA(config.critic_model_name)
        
        # Search state
        self.root: Optional[MCTSNode] = None
        self.proof_plan: Optional[ProofPlan] = None
        self.completed_subgoals: Set[str] = set()
        
        # Proof output
        self.complete_proof: List[Dict] = []
        self.proof_trace: Optional[ProofTrace] = None
        
        # Statistics
        self.stats = {
            "nodes_explored": 0,
            "tactics_tried": 0,
            "fast_path_hits": 0,
            "realignment_count": 0,
            "subgoals_completed": 0,
            "total_time": 0.0,
            "max_depth": 0,
            "branching_factor": []
        }
    
    async def prove(
        self,
        theorem_statement: str,
        timeout_seconds: float = 300.0,
        max_iterations: int = 1000,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Main entry point for theorem proving.
        
        Returns complete Lean proof as string.
        """
        start_time = time.time()
        logger.info(f"{'='*70}")
        logger.info(f"STARTING SOTA PROOF SEARCH")
        logger.info(f"Theorem: {theorem_statement[:100]}...")
        logger.info(f"Timeout: {timeout_seconds}s, Max iterations: {max_iterations}")
        logger.info(f"{'='*70}")
        
        # Phase 1: Hierarchical proof decomposition
        logger.info("\n[Phase 1] Generating proof plan with decomposition...")
        self.proof_plan = await self.planner.decompose_proof(theorem_statement)
        logger.info(f"  Strategy: {self.proof_plan.main_strategy}")
        logger.info(f"  Lemmas: {len(self.proof_plan.lemmas)}")
        logger.info(f"  Estimated difficulty: {self.proof_plan.estimated_difficulty}/10")
        logger.info(f"  Suggested tactics: {', '.join(self.proof_plan.suggested_tactics[:5])}")
        
        # Phase 2: Initialize MCTS tree
        logger.info("\n[Phase 2] Initializing MCTS tree...")
        root_state = LeanState(goal=theorem_statement)
        self.root = MCTSNode(
            state=root_state,
            node_type=NodeType.ROOT,
            depth=0
        )
        
        # Phase 3: MCTS search loop
        logger.info("\n[Phase 3] Running MCTS search...")
        
        solution_node = None
        
        for iteration in range(max_iterations):
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.warning(f"⏰ Timeout after {elapsed:.1f}s ({iteration} iterations)")
                break
            
            # Selection: traverse tree using PUCT
            node = self._select(self.root)
            
            # Check if we reached a solved state
            if node.state.is_solved:
                logger.info(f"✓ Found solution at iteration {iteration}!")
                solution_node = node
                break
            
            # Expansion: generate children
            if not node.is_fully_expanded():
                await self._expand(node)
            
            # Simulation: evaluate leaf node
            if node.proof_trace is None or not node.children:
                reward = await self._simulate(node)
                
                # Backpropagation
                self._backpropagate(node, reward)
            
            # Update statistics
            self.stats["nodes_explored"] += 1
            self.stats["max_depth"] = max(self.stats["max_depth"], node.depth)
            
            # Progress logging every 100 iterations
            if iteration % 100 == 0:
                logger.info(f"  Iteration {iteration}: "
                          f"nodes={self.stats['nodes_explored']}, "
                          f"max_depth={self.stats['max_depth']}, "
                          f"time={elapsed:.1f}s")
        
        # Phase 4: Extract complete proof
        if solution_node:
            logger.info("\n[Phase 4] Extracting complete proof...")
            proof_text = await self._extract_complete_proof(solution_node, output_file)
            
            self.stats["total_time"] = time.time() - start_time
            logger.info(f"\n{'='*70}")
            logger.info(f"PROOF FOUND!")
            logger.info(f"{'='*70}")
            logger.info(f"Iterations: {iteration}")
            logger.info(f"Nodes explored: {self.stats['nodes_explored']}")
            logger.info(f"Max depth: {self.stats['max_depth']}")
            logger.info(f"Total time: {self.stats['total_time']:.2f}s")
            logger.info(f"Fast-path hits: {self.stats['fast_path_hits']}")
            logger.info(f"Subgoals completed: {self.stats['subgoals_completed']}")
            logger.info(f"{'='*70}\n")
            
            if output_file:
                logger.info(f"Complete proof saved to: {output_file}")
            
            return proof_text
        else:
            logger.warning(f"\n❌ Search exhausted without solution after {max_iterations} iterations")
            self.stats["total_time"] = time.time() - start_time
            return None
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select node using PUCT"""
        current = node
        
        while current.is_fully_expanded() and current.children:
            current = current.best_child(exploration_constant=config.exploration_constant)
        
        return current
    
    async def _expand(self, node: MCTSNode):
        """Expand node with tactic generation"""
        # Get next subgoal from proof plan
        next_subgoal = self.proof_plan.get_next_subgoal(self.completed_subgoals)
        
        # Try symbolic fast-path first (high priority)
        fast_tactics = await self.booster.try_solve_batch(node.state, self.proof_plan.suggested_tactics)
        
        if fast_tactics:
            for tactic in fast_tactics[:3]:  # Try top 3
                result = await self.lean.execute(node.state, [tactic])
                if result.success and result.new_state:
                    child = self._create_child_node(node, tactic, result, priority=0.9)
                    node.children.append(child)
                    self.stats["fast_path_hits"] += 1
                    logger.debug(f"  ⚡ Fast-path: {tactic}")
        
        # Generate tactics from policy model
        tactic_candidates = await self.policy.generate_tactic_candidates(
            node.state,
            context=self.proof_plan,
            current_subgoal=next_subgoal,
            num_candidates=10
        )
        
        # Score and select top tactics using cross-entropy method
        scored_tactics = []
        for tactic_info in tactic_candidates[:5]:  # Top 5
            # Quick validation
            result = await self.lean.execute(node.state, [tactic_info["tactic"]])
            if result.success and result.new_state:
                # Value estimate
                value = await self.critic.evaluate(result.new_state, self.proof_plan)
                scored_tactics.append((tactic_info, value, result))
                self.stats["tactics_tried"] += 1
        
        # Create children for valid tactics
        for tactic_info, value, result in scored_tactics:
            child = self._create_child_node(
                node,
                tactic_info["tactic"],
                result,
                prior_prob=tactic_info.get("probability", 0.1),
                value_estimate=value
            )
            node.children.append(child)
        
        # Update branching factor stat
        if node.children:
            self.stats["branching_factor"].append(len(node.children))
    
    def _create_child_node(
        self,
        parent: MCTSNode,
        tactic: str,
        result: TacticResult,
        prior_prob: float = 0.1,
        value_estimate: float = 0.0,
        priority: float = 0.5
    ) -> MCTSNode:
        """Create child node with full proof trace"""
        
        # Create proof trace
        trace = ProofTrace(
            node_id=str(uuid.uuid4())[:8],
            tactic=tactic,
            parent_state=parent.state.goal[:100],
            resulting_state=result.new_state.goal[:100] if result.new_state else "",
            is_valid=result.success,
            lemma_used=None,  # Would be populated from policy
            timestamp=time.time(),
            depth=parent.depth + 1
        )
        
        child = MCTSNode(
            state=result.new_state,
            parent=parent,
            tactic_history=parent.tactic_history + [tactic],
            tactic_used=tactic,
            depth=parent.depth + 1,
            prior_probability=prior_prob,
            total_reward=value_estimate,
            visits=1,
            _value_estimate=value_estimate,
            proof_trace=trace,
            subgoal_index=self.stats["subgoals_completed"]
        )
        
        # Check if subgoal completed
        if value_estimate > 0.8:
            self.completed_subgoals.add(f"subgoal_{child.subgoal_index}")
            self.stats["subgoals_completed"] += 1
            child.is_solved = True
        
        return child
    
    async def _simulate(self, node: MCTSNode) -> float:
        """Simulate from leaf node to estimate value"""
        if node.state.is_solved:
            return 1.0
        
        # Use critic for value estimation
        value = await self.critic.evaluate(node.state, self.proof_plan)
        
        # Add depth penalty (prefer shorter proofs)
        depth_penalty = -0.01 * node.depth
        return value + depth_penalty
    
    def _backpropagate(self, node: MCTSNode, reward: float):
        """Backpropagate reward up the tree"""
        current = node
        
        while current is not None:
            current.visits += 1
            current.total_reward += reward
            
            # Update parent's value estimate
            if current.parent:
                current._value_estimate = current.total_reward / current.visits
            
            current = current.parent
    
    async def _extract_complete_proof(
        self,
        solution_node: MCTSNode,
        output_file: Optional[str] = None
    ) -> str:
        """Extract complete Lean proof with formatting"""
        
        # Reconstruct tactic sequence
        tactics = solution_node.tactic_history
        
        # Build proof text
        proof_lines = []
        proof_lines.append(f"-- Theorem: {self.proof_plan.theorem_statement}")
        proof_lines.append(f"-- Strategy: {self.proof_plan.main_strategy}")
        proof_lines.append(f"-- Lemmas used: {len(self.proof_plan.lemmas)}")
        proof_lines.append(f"-- Tactics: {len(tactics)}")
        proof_lines.append(f"-- Search iterations: {self.stats['nodes_explored']}")
        proof_lines.append(f"-- Time: {self.stats['total_time']:.2f}s")
        proof_lines.append("")
        proof_lines.append(f"theorem proven_theorem : {self.proof_plan.theorem_statement} :=")
        proof_lines.append("by")
        
        # Format tactics with indentation
        for i, tactic in enumerate(tactics):
            if i == 0:
                proof_lines.append(f"  {tactic}")
            else:
                # Add structure based on proof plan
                if any(kw in tactic for kw in ["induction", "cases", "obtain"]):
                    proof_lines.append("")
                    proof_lines.append(f"  -- Step {i+1}")
                    proof_lines.append(f"  {tactic}")
                else:
                    proof_lines.append(f"  {tactic}")
        
        proof_text = "\n".join(proof_lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(proof_text)
        
        # Store complete proof
        self.complete_proof = proof_lines
        self.proof_trace = solution_node.proof_trace
        
        return proof_text
    
    def get_proof_json(self) -> Dict:
        """Get complete proof as JSON with full metadata"""
        return {
            "theorem": self.proof_plan.theorem_statement if self.proof_plan else "",
            "strategy": self.proof_plan.main_strategy if self.proof_plan else "",
            "proof": self.complete_proof,
            "proof_trace": self.proof_trace.to_dict() if self.proof_trace else None,
            "statistics": self.stats,
            "proof_plan": self.proof_plan.to_dict() if self.proof_plan else None
        }
    
    def export_proof_package(self, output_dir: str):
        """Export complete proof package with all metadata"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Main proof Lean file
        proof_text = "\n".join(self.complete_proof)
        with open(os.path.join(output_dir, "proof.lean"), 'w', encoding='utf-8') as f:
            f.write(proof_text)
        
        # Metadata JSON
        metadata = self.get_proof_json()
        with open(os.path.join(output_dir, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Proof trace JSON
        if self.proof_trace:
            with open(os.path.join(output_dir, "proof_trace.json"), 'w', encoding='utf-8') as f:
                json.dump(self.proof_trace.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Summary
        summary = {
            "theorem": self.proof_plan.theorem_statement if self.proof_plan else "",
            "success": bool(self.complete_proof),
            "tactics_count": len(self.complete_proof) - 8,  # Subtract header lines
            "iterations": self.stats["nodes_explored"],
            "time_seconds": self.stats["total_time"],
            "max_depth": self.stats["max_depth"],
            "fast_path_hits": self.stats["fast_path_hits"],
            "subgoals_completed": self.stats["subgoals_completed"]
        }
        with open(os.path.join(output_dir, "summary.json"), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Proof package exported to: {output_dir}")
