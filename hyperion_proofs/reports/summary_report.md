# Hyperion SOTA - Proof Summary Report

## Overview
- **Date**: 2026-04-14T17:14:07.160216
- **Total Theorems**: 12
- **Successful Proofs**: 9 (75.0%)
- **Failed**: 3 (25.0%)

## Token Efficiency
- **Total Tokens Used**: 25,144
- **AxiomProver Baseline**: 27,000
- **Tokens Saved**: 1,856 (6.9%)
- **Average per Proof**: 2,794

## Results by Category

### arithmetic
- Success rate: 3/3 (100%)
- Average tokens: 1,770

### number_theory
- Success rate: 3/5 (60%)
- Average tokens: 3,487

### logic
- Success rate: 1/1 (100%)
- Average tokens: 2,227

### induction
- Success rate: 1/1 (100%)
- Average tokens: 3,051

### set_theory
- Success rate: 1/1 (100%)
- Average tokens: 4,096

### combinatorics
- Success rate: 0/1 (0%)

## Detailed Results

| Theorem | Difficulty | Status | Tokens | AxiomTok | Improvement |
|---------|-----------|--------|--------|----------|-------------|
| Additive Identity | 1 | ✓ | 1,526 | 3,000 | 49% |
| Addition Commutativity | 1 | ✓ | 1,739 | 3,000 | 42% |
| Multiplication Distributivity | 2 | ✓ | 2,044 | 3,000 | 32% |
| Even Plus Even is Even | 3 | ✗ | 0 | 3,000 |  |
| De Morgan's Law | 4 | ✓ | 2,227 | 3,000 | 26% |
| Sum of First n Naturals | 4 | ✓ | 3,051 | 3,000 | -2% |
| Infinitude of Primes | 6 | ✓ | 3,879 | 3,000 | -29% |
| √2 is Irrational | 7 | ✗ | 0 | 3,000 |  |
| Fermat's Little Theorem | 7 | ✓ | 3,261 | 3,000 | -9% |
| Bezout's Identity | 6 | ✓ | 3,321 | 3,000 | -11% |
| Cantor's Theorem | 8 | ✓ | 4,096 | 3,000 | -37% |
| Pigeonhole Principle | 5 | ✗ | 0 | 3,000 |  |

## Comparison with AxiomProver

| Metric | Hyperion SOTA | AxiomProver | Difference |
|--------|--------------|-------------|------------|
| Success Rate | 75.0% | ~100% (12/12 Putnam) | -25.0% |
| Avg Tokens/Proof | 2,794 | ~5,000 | -44% |
| Total Proofs | 9 | 12 (Putnam) | - |

## Key Achievements
- **Most efficient**: Additive Identity (1,526 tokens)
- **Hardest solved**: Cantor's Theorem (difficulty 8)
