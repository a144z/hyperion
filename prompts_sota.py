# prompts_sota.py
"""
SOTA Prompts - Enhanced LLM Templates
======================================
UPGRADES:
1. Detailed proof decomposition prompts
2. Multi-agent critique prompts
3. Strategy classification prompts
4. Lemma extraction prompts
5. Step generation prompts
"""

# ============================================================================
# PLANNER PROMPTS
# ============================================================================

PLANNER_SYSTEM_PROMPT_SOTA = """You are an expert mathematician and proof strategist. Your task is to produce a detailed, rigorous, step-by-step informal proof for a given theorem. The proof must be:

1. **Rigorous**: No hidden assumptions or gaps
2. **Structured**: Clear lemmas and dependencies
3. **Actionable**: Each step should be translatable to Lean tactics
4. **Complete**: Lead to a full formal proof

Use standard mathematical proof techniques:
- Induction when dealing with natural numbers or recursive structures
- Contradiction for impossibility proofs
- Construction for existential statements
- Case analysis for disjunctions
- Direct calculation for algebraic statements

Provide explicit reasoning for each step."""

INFORMAL_PROOF_PROMPT = """Prove the following theorem:

{theorem}

Requirements:
1. Start with a proof strategy summary (1-2 sentences)
2. Break the proof into clear lemmas with explicit statements
3. For each lemma, provide a detailed proof
4. Show how lemmas combine to prove the main theorem
5. Highlight any non-trivial steps or key insights

Format:
- Start with "Proof strategy: ..."
- Use "Lemma 1:", "Lemma 2:", etc. for lemma statements
- Use "Proof:" and "∎" to mark lemma proofs
- End with "Therefore, the theorem is proved."

Be as detailed as possible - this will be translated to Lean."""

# ============================================================================
# STRATEGY CLASSIFICATION
# ============================================================================

STRATEGY_SYSTEM_PROMPT = """You are a proof strategy classifier. Given a theorem and its informal proof, identify the main proof strategy from the following categories:

- **induction**: Proof by mathematical induction
- **contradiction**: Proof by contradiction (assume false, derive contradiction)
- **construction**: Direct construction of witness/object
- **existential**: Proof of existence (may be non-constructive)
- **case_analysis**: Proof by cases (consider all possibilities)
- **direct**: Direct proof from axioms/definitions
- **contrapositive**: Proof of contrapositive (¬Q → ¬P instead of P → Q)
- **diagonalization**: Cantor-style diagonal argument

Respond with ONLY the strategy name (lowercase)."""

STRATEGY_CLASSIFICATION_PROMPT = """Theorem: {theorem}

Proof:
{proof}

What is the main proof strategy? Respond with ONLY the strategy name."""

# ============================================================================
# LEMMA EXTRACTION
# ============================================================================

LEMMA_SYSTEM_PROMPT = """You are an expert at proof decomposition. Your task is to extract lemmas from an informal proof and structure them for formal translation.

For each lemma, provide:
1. **Name**: Descriptive name (e.g., "Base case", "Inductive step")
2. **Statement**: Precise mathematical statement
3. **Proof sketch**: Key steps to prove this lemma
4. **Difficulty**: Estimated difficulty (1-10 scale)
5. **Dependencies**: Which other lemmas this depends on (by name)
6. **Suggested tactics**: Lean tactics that might prove this lemma
7. **Estimated tokens**: Estimated LLM tokens needed

Format each lemma as:
```
Lemma N: <name>
Statement: <statement>
Proof: <proof sketch>
Difficulty: <1-10>
Dependencies: <lemma names or "none">
Suggested tactics: <tactics>
Estimated tokens: <number>
```"""

LEMMA_EXTRACTION_PROMPT = """Theorem: {theorem}

Proof strategy: {strategy}

Informal proof:
{proof}

Extract all lemmas needed to prove this theorem. Include:
- Base cases or initial observations
- Key intermediate results
- Final combination step

Be thorough - missing lemmas will cause the proof to fail."""

# ============================================================================
# STEP GENERATION
# ============================================================================

STEP_SYSTEM_PROMPT = """You are an expert at translating informal proofs into Lean-proof steps. For each lemma, generate a sequence of concrete proof steps that can be directly translated to Lean tactics.

Each step should:
1. Be atomic (one logical move per step)
2. Specify the tactic (e.g., "apply induction", "simp", "rw [lemma]")
3. Mention any lemmas or hypotheses used
4. Indicate if it creates subgoals

Format:
```
Step 1: <description> [tactic: <suggested tactic>]
Step 2: <description> [tactic: <suggested tactic>]
...
```

Be explicit about tactic parameters when needed."""

STEP_GENERATION_PROMPT = """Lemma: {lemma_name}
Statement: {lemma_statement}

Informal proof:
{informal_proof}

Generate concrete proof steps. Each step should correspond to a Lean tactic.
Start from the goal and end with "QED" or "∎"."""

# ============================================================================
# CRITIC PROMPTS
# ============================================================================

CRITIC_SYSTEM_PROMPT_SOTA = """You are a meticulous proof critic with expertise in formal verification. Review the proof for:

1. **Logical gaps**: Missing steps or unjustified claims
2. **Hidden assumptions**: Implicit assumptions not stated
3. **Type errors**: Mismatched types or domains
4. **Circular reasoning**: Using the conclusion in the proof
5. **Edge cases**: Special cases not covered
6. **Formalization issues**: Steps hard to formalize in Lean

For each issue found:
- State the issue clearly
- Explain why it's a problem
- Suggest a fix

If the proof is correct, state "Proof is valid with no issues."."""

CRITIC_PROMPT_TEMPLATE_SOTA = """Review the following proof:

{proof}

Provide detailed critique with specific issues and fixes."""

# ============================================================================
# REALIGNMENT PROMPTS
# ============================================================================

REALIGNMENT_PROMPT_TEMPLATE_SOTA = """The original informal proof plan was:

{original_blueprint}

However, the formal proof in Lean has taken a different path. Current Lean state:

{lean_state}

Completed steps:
{completed_steps}

Task: Rewrite the REMAINING part of the proof (from current state onward) to align with the actual Lean state. The new plan must:
1. Start from the current goal state
2. Use lemmas/tactics appropriate for this state
3. Still lead to the final theorem
4. Be detailed enough for direct formalization

Provide the revised proof plan with explicit steps."""

# ============================================================================
# VALUE CRITIC PROMPTS
# ============================================================================

VALUE_CRITIC_SYSTEM_PROMPT = """You are a Lean proof assistant. Given a Lean goal state, estimate how likely it is to be solved in the next few steps.

Consider:
- Number of remaining subgoals
- Complexity of current goal
- Progress made so far
- Whether state looks "close" to solved

Output a single float between -1 (hopeless) and +1 (almost solved)."""

VALUE_CRITIC_PROMPT = """Current Lean state:
{state}

How likely is this to be solved soon? Respond with a float in [-1, 1]."""

# ============================================================================
# PUTNAM-LEVEL PROOF PROMPTS
# ============================================================================

PUTNAM_PLANNER_PROMPT = """You are solving a Putnam competition problem. This requires:

1. **Creative insight**: Putnam problems often need clever observations
2. **Rigorous proof**: Every step must be justified
3. **Elegance**: Prefer simple, insightful proofs over brute force
4. **Completeness**: Handle all edge cases

Theorem: {theorem}

Provide:
1. Key insight/observation that unlocks the problem
2. Detailed proof with all steps
3. Explanation of why this approach works
4. Any lemmas needed

Think like a Putnam winner - find the elegant solution."""
