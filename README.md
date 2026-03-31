# Hyperion – AI Theorem Prover for Lean 4

Hyperion is a state‑of‑the‑art automated theorem prover that combines informal reasoning, speculative tactic execution, and self‑play to prove complex theorems. It is designed to handle all 12 Putnam problems from a given year (or any set of Lean theorems).

## Features

- **Informal Blueprint Generation**: Uses large LLMs (Claude/DeepSeek) to produce step‑by‑step informal proofs.
- **Multi‑Agent Critique**: A critic model reviews and revises the blueprint for logical gaps.
- **Speculative Tactic Batching**: Generates 3–5 tactics at once, reducing Lean REPL round‑trips.
- **Symbolic Fast‑Path**: Tries deterministic tactics (`grind`, `aesop`, `ring`) before invoking the policy.
- **Value‑Guided Search**: A lightweight critic prunes low‑promise branches.
- **Blueprint Realignment**: When Lean diverges, the informal plan is rewritten to match the actual state.
- **Self‑Play Curriculum**: Mutates proven theorems to generate new training data.
- **Nightly Training**: Uses DPO/GRPO to improve the policy from search traces.

## Installation

1. Clone the repository.
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set up Lean 4 and LeanDojo (or your preferred Lean interface). Modify `lean_interface.py` accordingly.
4. Configure models in `config.py`. You'll need API keys for commercial LLMs or paths to local open‑weights models.
5. (Optional) Start Qdrant for lemma retrieval.

## Usage

Start the server:
```bash
uvicorn main:app --reload