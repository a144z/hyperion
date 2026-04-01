# prompts.py

# Templates for LLM calls

PLANNER_SYSTEM_PROMPT = """You are an expert mathematician. Your task is to produce a detailed, step‑by‑step informal proof for a given theorem. The proof should be rigorous, self‑contained, and suitable for translation into Lean. Use natural language, but be precise."""

PLANNER_PROMPT_TEMPLATE = """Prove the following theorem:

{theorem}

Break your proof into clear milestones (like Lemma 1, Lemma 2, ...). After the final proof, provide a list of milestones exactly as they appear in the text, each on a separate line starting with "MILESTONE:".
"""

CRITIC_SYSTEM_PROMPT = """You are a meticulous proof critic. Review the following informal proof for logical gaps, hidden assumptions, or errors. Provide constructive feedback. If there are issues, explain them; otherwise, state that the proof is correct."""

CRITIC_PROMPT_TEMPLATE = """Proof:\n{proof}\n\nFeedback:"""

REALIGNMENT_PROMPT_TEMPLATE = """The original informal proof was:

{original_blueprint}

However, the formal proof in Lean has diverged. The current Lean state is:

{lean_state}

Please rewrite the remaining part of the informal proof (from milestone {current_milestone_index} onward) to align with the actual Lean state. The new proof must still lead to the final theorem."""

VALUE_CRITIC_SYSTEM_PROMPT = """You are a Lean proof assistant. Given a Lean goal state, estimate how likely it is to be solved in the next few steps. Output a single float between -1 (hopeless) and +1 (almost solved)."""