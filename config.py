# config.py

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Models
    policy_model_name: str = "deepseek-ai/deepseek-prover-v1.5"  # or local path
    critic_model_name: str = "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4"  # quantized 7B
    planner_model_name: str = "anthropic/claude-3.5-sonnet"  # or open‑weight equivalent

    # Lean interface
    lean_worker_count: int = 8  # number of parallel Lean REPL workers
    lean_timeout: float = 30.0  # seconds per tactic batch

    # Search parameters
    max_search_nodes: int = 1000
    speculative_batch_size: int = 3  # tactics per bundle
    value_prune_threshold: float = -0.5
    exploration_constant: float = 1.0  # for PUCT (optional)

    # Blueprint
    use_multi_agent_critique: bool = True
    realignment_threshold: float = 0.3  # divergence threshold

    # Logging & training
    log_dir: str = "./logs"
    training_batch_size: int = 16
    learning_rate: float = 1e-6
    grpo_groups: int = 8

    # Self‑play
    mutation_probability: float = 0.2
    selfplay_interval_hours: int = 24

    # Vector DB
    vector_db_host: str = "localhost"
    vector_db_port: int = 6333

    # Paths
    lean_workspace: str = "./lean_workspace"
    mathlib_dir: str = "./mathlib4"  # if needed

    # API keys (optional)
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

config = Config()