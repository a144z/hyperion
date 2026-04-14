-- Real Mathematical Proofs for Hyperion Benchmark
-- These are actual provable theorems in Lean 4

/-
  Theorem: Addition Commutativity
  Description: For all natural numbers a and b, a + b = b + a
  Difficulty: 1/6
  Expected AxiomMaths Tokens: 150
  Key Lemmas: Nat.add_zero, Nat.add_succ, induction
-/
theorem add_comm_proof (a b : Nat) : a + b = b + a := by
  induction a with
  | zero => simp
  | succ a' ih =>
    rw [Nat.add_succ, ih, Nat.add_succ]

/-
  Theorem: Distributivity of Multiplication over Addition
  Description: a * (b + c) = a * b + a * c
  Difficulty: 1/6
  Expected AxiomMaths Tokens: 180
  Key Lemmas: Nat.mul_zero, Nat.mul_succ, Nat.add_assoc
-/
theorem distrib_proof (a b c : Nat) : a * (b + c) = a * b + a * c := by
  induction a with
  | zero => simp
  | succ a' ih =>
    rw [Nat.mul_succ, ih, Nat.mul_succ, Nat.add_assoc]

/-
  Theorem: Sum of Even Numbers is Even
  Description: If a and b are even, then a + b is even
  Difficulty: 2/6
  Expected AxiomMaths Tokens: 320
  Key Lemmas: even_iff_two_dvd, dvd_add
-/
theorem even_add_even {a b : Nat} (ha : Even a) (hb : Even b) : Even (a + b) := by
  rw [even_iff_two_dvd] at ha hb ⊢
  obtain ⟨k, rfl⟩ := ha
  obtain ⟨l, rfl⟩ := hb
  use k + l
  ring

/-
  Theorem: Product of Odd Numbers is Odd
  Description: If a and b are odd, then a * b is odd
  Difficulty: 2/6
  Expected AxiomMaths Tokens: 350
  Key Lemmas: Odd, ring
-/
theorem odd_mul_odd {a b : Nat} (ha : Odd a) (hb : Odd b) : Odd (a * b) := by
  cases' ha with k hk
  cases' hb with l hl
  rw [hk, hl]
  use 2 * k * l + k + l
  ring

/-
  Theorem: De Morgan's Law: ¬(P ∧ Q) ↔ ¬P ∨ ¬Q
  Description: Negation of conjunction equals disjunction of negations
  Difficulty: 3/6
  Expected AxiomMaths Tokens: 580
  Key Lemmas: Iff.intro, by_cases, contradiction
-/
theorem de_morgan_and (P Q : Prop) : ¬(P ∧ Q) ↔ ¬P ∨ ¬Q := by
  apply Iff.intro
  · intro h
    by_cases
    · assume hP : P
      have hQ : Q := by
        by_contra h
        exact h ⟨hP, h⟩
      contradiction
    · exact Or.inr ‹¬Q›
  · intro h
    cases h
    · intro hPQ
      exact ‹¬P› hPQ.left
    · intro hPQ
      exact ‹¬Q› hPQ.right

/-
  Theorem: Sum Formula: 2 × Σ(i=0..n) i = n × (n+1)
  Description: The sum of first n natural numbers equals n(n+1)/2
  Difficulty: 3/6
  Expected AxiomMaths Tokens: 420
  Key Lemmas: Finset.sum_range_succ, induction, ring
-/
theorem sum_first_n_formula (n : Nat) : 
    2 * (∑ i in Finset.range (n + 1), i) = n * (n + 1) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ih]
    ring

/-
  Theorem: Geometric Series Sum: Σ(i=0..n) 2^i = 2^(n+1) - 1
  Description: Sum of powers of 2 equals next power minus 1
  Difficulty: 4/6
  Expected AxiomMaths Tokens: 650
  Key Lemmas: Finset.sum_range_succ, pow_succ, Nat.mul_two
-/
theorem geometric_series_sum (n : Nat) : 
    (∑ i in Finset.range (n + 1), 2^i) = 2^(n + 1) - 1 := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ih]
    have : 2^(n + 1) + 2^(n + 1) = 2^(n + 2) := by
      rw [← Nat.mul_two, ← pow_succ]
    rw [this]
    simp

/-
  Theorem: Divisibility Transitivity
  Description: If a|b and b|c, then a|c
  Difficulty: 3/6
  Expected AxiomMaths Tokens: 380
  Key Lemmas: dvd_mul_right, mul_assoc
-/
theorem dvd_trans {a b c : Nat} (hab : a ∣ b) (hbc : b ∣ c) : a ∣ c := by
  obtain ⟨k, hk⟩ := hab
  obtain ⟨l, hl⟩ := hbc
  use k * l
  rw [hl, hk, mul_assoc]

/-
  Theorem: √2 is Irrational
  Description: The square root of 2 cannot be expressed as a ratio
  Difficulty: 6/6
  Expected AxiomMaths Tokens: 1800
  Key Lemmas: Nat.prime_two, infinite_descent, coprime
-/
theorem sqrt_two_irrational' : ¬∃ (p q : Nat), q ≠ 0 ∧ p * p = 2 * q * q := by
  intro h
  obtain ⟨p, q, hq, hpq⟩ := h
  -- Classical proof by infinite descent
  have : p % 2 = 0 := by
    have : 2 ∣ p * p := by
      use q * q
      linarith
    exact Nat.Prime.dvd_of_dvd_pow Nat.prime_two this
  obtain ⟨k, hk⟩ := this
  rw [hk] at hpq
  ring_nf at hpq
  have : q % 2 = 0 := by
    have : 2 ∣ q * q := by
      use k * k
      linarith
    exact Nat.Prime.dvd_of_dvd_pow Nat.prime_two this
  sorry  -- Full proof requires descent argument

/-
  Theorem: Infinitude of Primes
  Description: There are infinitely many prime numbers
  Difficulty: 5/6
  Expected AxiomMaths Tokens: 1200
  Key Lemmas: Nat.exists_prime_and_dvd, Nat.dvd_factorial, factorial
-/
theorem infinitude_of_primes : ∀ n : Nat, ∃ p > n, Nat.Prime p := by
  intro n
  have : ∃ p, Nat.Prime p ∧ p ∣ (n + 1).factorial + 1 := by
    apply Nat.exists_prime_and_dvd
    simp
  obtain ⟨p, hp, hpdvd⟩ := this
  use p
  constructor
  · show p > n
    by_contra h
    push_neg at h
    have : p ∣ (n + 1).factorial := by
      apply Nat.dvd_factorial
      · exact hp.pos
      · linarith
    have : p ∣ 1 := by
      apply Nat.dvd_sub' hpdvd this
    simp at this
    contradiction
  · exact hp

/-
  Theorem: Bezout's Identity
  Description: For any a,b there exist x,y such that ax + by = gcd(a,b)
  Difficulty: 5/6
  Expected AxiomMaths Tokens: 280
  Key Lemmas: Nat.gcd_eq_gcd_ab, Nat.gcdA, Nat.gcdB
-/
theorem bezout_identity (a b : Nat) : 
    ∃ x y : Int, a * x + b * y = Nat.gcd a b := by
  use Nat.gcdA a b, Nat.gcdB a b
  apply Nat.gcd_eq_gcd_ab

/-
  Theorem: Fermat's Little Theorem
  Description: If p is prime and p ∤ a, then a^(p-1) ≡ 1 (mod p)
  Difficulty: 6/6
  Expected AxiomMaths Tokens: 520
  Key Lemmas: Nat.ModEq.pow_card_sub_one', Nat.Prime
-/
theorem fermat_little {a p : Nat} (hp : Nat.Prime p) (h : ¬p ∣ a) : 
    a^(p - 1) ≡ 1 [MOD p] := by
  apply Nat.ModEq.pow_card_sub_one'
  intro h
  apply h
  exact Nat.Prime.dvd_of_dvd_pow hp h

/-
  Theorem: Pigeonhole Principle
  Description: If n+1 pigeons in n holes, some hole has ≥2 pigeons
  Difficulty: 4/6
  Expected AxiomMaths Tokens: 850
  Key Lemmas: Fintype.card_le_of_injective, Function.Injective
-/
theorem pigeonhole_simple {α β : Type} [Fintype α] [Fintype β] 
    (f : α → β) (h : Fintype.card α > Fintype.card β) : 
    ∃ (b : β), ∃ (a₁ a₂ : α), a₁ ≠ a₂ ∧ f a₁ = b ∧ f a₂ = b := by
  by_contra h'
  push_neg at h'
  have : Function.Injective f := by
    intro a₁ a₂ hf
    by_contra hne
    specialize h' (f a₁)
    simp at h'
    contradiction
  have : Fintype.card α ≤ Fintype.card β := by
    apply Fintype.card_le_of_injective f this
  linarith

/-
  Theorem: Binomial Expansion (a+b)²
  Description: (a+b)² = a² + 2ab + b²
  Difficulty: 2/6
  Expected AxiomMaths Tokens: 120
  Key Lemmas: pow_two, ring
-/
theorem binomial_square (a b : Nat) : (a + b)^2 = a^2 + 2*a*b + b^2 := by
  rw [pow_two, pow_two, pow_two]
  ring

/-
  Theorem: Power Set Has Greater Cardinality
  Description: For any set S, |P(S)| > |S|
  Difficulty: 6/6
  Expected AxiomMaths Tokens: 1500
  Key Lemmas: Function.Bijective, diagonal_argument
-/
theorem cantor_theorem {α : Type} : 
    ¬∃ (f : α → Set α), Function.Bijective f := by
  intro h
  obtain ⟨f, hf⟩ := h
  let S := {x : α | x ∉ f x}
  obtain ⟨s, hs⟩ := hf.surjective S
  have h₁ : s ∉ f s := by
    intro h'
    have : s ∉ f s := hs s
    contradiction
  have h₂ : s ∈ S := by
    have : f s = S := hs
    rw [← this]
    exact h₁
  contradiction

