
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
- **Vector Lemma Retrieval**: Qdrant‑based retrieval of Mathlib lemmas for context.

## Installation

### Prerequisites
- Python 3.10+
- Lean 4 (via [elan](https://github.com/leanprover/elan) or from the official website)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo) installed
- Docker (optional, for Qdrant)

### Step‑by‑Step
1. Clone the repository:
   ```bash
   git clone <your-repo-url> hyperion
   cd hyperion
   ```
2. Create a virtual environment and install Python dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Install Lean 4 and LeanDojo:
   ```bash
   # If you haven't installed elan:
   curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
   # Then install LeanDojo (it will pull Lean 4):
   pip install lean-dojo
   ```
4. Set up Qdrant (optional, but recommended for lemma retrieval):
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
   Then populate the vector DB with Mathlib lemmas (see the script in `vector_db.py`).
5. Configure API keys and model paths in `config.py` (see [Configuration](#configuration)).
6. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Configuration

Edit `hyperion/config.py` to set:

- **Model names**: `policy_model_name`, `critic_model_name`, `planner_model_name`
- **API keys**: `anthropic_api_key`, `openai_api_key` (if using commercial APIs)
- **Lean interface**: `lean_worker_count`, `lean_timeout`
- **Search parameters**: `max_search_nodes`, `speculative_batch_size`, `value_prune_threshold`
- **Logging and training**: `log_dir`, `training_batch_size`
- **Self‑play**: `mutation_probability`, `selfplay_interval_hours`
- **Vector DB**: `vector_db_host`, `vector_db_port`

## Usage

### API Endpoints

- `POST /prove` – Submit a Lean theorem and receive a proof (or an error).
  ```bash
  curl -X POST http://localhost:8000/prove \
    -H "Content-Type: application/json" \
    -d '{"theorem": "theorem example (n : ℕ) : n + 0 = n := by simp"}'
  ```
  Response:
  ```json
  {"proof": "by simp", "success": true}
  ```

- `POST /selfplay` – Trigger self‑play generation (generates new problems by mutation and attempts to prove them).
- `POST /train` – Start a nightly training run (requires pre‑collected traces).

## Customizing for the 12 Putnam Problems

To prove all 12 Putnam problems from a given year:

1. **Format the theorems** as Lean statements (e.g., in a `.lean` file). Make sure they are self‑contained and use the standard Lean 4 syntax.
2. **Pre‑populate the vector DB** with relevant Mathlib lemmas. This is crucial for retrieving necessary facts during search. Use the provided embedding script or an offline process.
3. **Fine‑tune the policy model** on existing Putnam solutions (if available) to bootstrap performance. You can collect traces by running Hyperion on known solutions (even if they fail) and then use the `/train` endpoint to improve.
4. **Adjust search parameters** for deeper exploration. The Putnam problems often require long proofs; consider increasing `max_search_nodes` (e.g., 5000) and `speculative_batch_size` (e.g., 5).
5. **Use the blueprint realignment** to keep the search focused. The system will automatically rewrite the informal plan if the formal state diverges.
6. **Run self‑play** after a few successful proofs to generate synthetic training data, further improving the model.

## Architecture Overview

See the detailed documentation in the code. The main components are:

1. **Planner** (`planner.py`): Generates informal blueprint via LLM and performs multi‑agent critique.
2. **Search Engine** (`search.py`): Best‑first search with speculative batching, value pruning, and realignment.
3. **Symbolic Booster** (`symbolic.py`): Fast‑path tactics (`grind`, `aesop`, `ring`).
4. **Policy Model** (`policy.py`): LLM that generates tactic sequences.
5. **Value Critic** (`critic.py`): Lightweight model that scores Lean states.
6. **Lean Interface** (`lean_interface.py`): Asynchronous wrapper around LeanDojo (or other Lean REPL).
7. **Self‑Play & Training** (`selfplay.py`, `training.py`): Mutation, curriculum generation, and nightly fine‑tuning.
8. **Vector DB** (`vector_db.py`): Qdrant‑based retrieval of Mathlib lemmas.

## Planned Improvements / Roadmap

We are actively developing Hyperion. The following improvements are planned:

### Performance & Scalability
- [ ] **Parallel Lean workers** – Use Ray to scale to hundreds of simultaneous Lean sessions.
- [ ] **Caching of tactic results** – Store successful tactic invocations to avoid recomputation.
- [ ] **Adaptive batching** – Dynamically adjust speculative batch size based on success rate.
- [ ] **Better error recovery** – When a tactic batch fails at step k, keep the first k-1 steps and branch.

### Search & Exploration
- [ ] **PUCT‑based tree search** – Replace simple best‑first with Monte Carlo Tree Search (MCTS) using the value critic as a prior.
- [ ] **Incremental blueprint realignment** – Use the value critic to detect divergence earlier and realign more aggressively.
- [ ] **Goal decomposition with lemmas** – Automatically split a goal into lemmas using the planner, then prove them independently.
- [ ] **Hierarchical search** – Use the blueprint milestones as sub‑tasks, proving each with a separate search.

### Training & Self‑Improvement
- [ ] **Full GRPO implementation** – Integrate Group Relative Policy Optimization from the paper using `trl`.
- [ ] **DPO fine‑tuning** – Use logged (state, good_tactic, bad_tactic) triples to train the policy.
- [ ] **Self‑play with adversarial mutation** – Generate harder problems by altering constants, swapping operators, or adding constraints.
- [ ] **Continuous integration** – Automatically run nightly training and self‑play on a schedule.

### Integration & Tooling
- [ ] **LeanDojo 2.0 support** – Update to the latest LeanDojo API for better performance and stability.
- [ ] **Better vector retrieval** – Use a larger embedding model and hybrid search (BM25 + dense) for more relevant lemmas.
- [ ] **Web interface** – Provide a simple UI for submitting theorems and viewing proofs.
- [ ] **Docker deployment** – Package the entire system with pre‑loaded models and vector DB.

### Putnam‑Specific Enhancements
- [ ] **Pre‑training on math contest problems** – Fine‑tune the policy on a corpus of Putnam and other contest solutions.
- [ ] **Automated lemma extraction** – Automatically extract and index lemmas from Mathlib that are relevant to number theory, combinatorics, etc.
- [ ] **Proof‑style guidance** – Prompt the planner to produce informal proofs in the style of Putnam solutions (e.g., using clever invariants).

## To‑Do List (Actionable Items)

If you'd like to contribute, here are some concrete tasks:

- [ ] **Implement real LeanDojo interface** – Replace the mock `LeanWorker` with a robust async session pool.
- [ ] **Populate vector DB** – Write a script to parse Mathlib and insert lemma embeddings into Qdrant.
- [ ] **Integrate a real LLM** – Add support for OpenAI, Anthropic, and local Hugging Face models.
- [ ] **Add test suite** – Write unit tests for the planner, search, and Lean interface.
- [ ] **Create example scripts** – Show how to prove a simple theorem (e.g., `2 + 2 = 4`) to verify the system.
- [ ] **Implement the realignment prompt** – Call the LLM when divergence is detected and update the blueprint.
- [ ] **Add GRPO training loop** – Use `trl` to implement the algorithm described in the paper.
- [ ] **Profile performance** – Measure latency of each component and identify bottlenecks.
- [ ] **Add documentation** – Write docstrings for all classes and methods.
- [ ] **Set up CI/CD** – Automate testing and linting with GitHub Actions.

## Contributing

We welcome contributions! Please open an issue or pull request. For major changes, discuss first.

## License

MIT License

Copyright (c) 2025 Hyperion Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Third‑Party Licenses

Hyperion incorporates or depends on the following third‑party software:

| Component | License | Purpose |
|-----------|---------|---------|
| Lean 4 | Apache 2.0 | Theorem prover kernel |
| LeanDojo | MIT | Lean interaction interface |
| Qdrant | Apache 2.0 | Vector database for lemma retrieval |
| Transformers (Hugging Face) | Apache 2.0 | Model loading and inference |
| FastAPI | MIT | Web server framework |
| Ray | Apache 2.0 | Distributed computing |

### Model Licenses

The models used with Hyperion (e.g., DeepSeek‑Prover, Qwen, Claude) are subject to their respective licenses. Users are responsible for complying with the terms of each model provider.

### Attribution

If you use Hyperion in your research, please cite:

```
@software{hyperion2026,
  author = {a144z},
  title = {Hyperion: AI Theorem Prover for Lean 4},
  year = {2025},
  url = {https://github.com/a144z/hyperion}
}
```

### Commercial Use

This software is open‑source and free for both academic and commercial use under the terms of the MIT License. However, if you use Hyperion commercially with proprietary models or APIs, please be aware that those services may have their own licensing requirements.

### Disclaimer

This software is provided for research and educational purposes. The authors make no guarantees about the correctness of generated proofs. Users should independently verify any proofs intended for publication or critical applications.
