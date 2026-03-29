# Experiment 0 Pilot Report

- Results file: `results_20260315T114840Z_conds-A-B-C-D_tiers-2-3_sessions-30_model-gpt-5-mini.json`
- Summary file: `summary_20260315T114840Z_conds-A-B-C-D_tiers-2-3_sessions-30_model-gpt-5-mini.json`

## Framing

This is Experiment 0 in the enterprise AI memory program: a foundation study asking whether memory infrastructure materially improves multi-turn enterprise SQL tasks before moving on to backend comparisons or systems optimization. The practical industry framing matches the broader Forbes Technology Council angle in this repo: memory should be treated as infrastructure, not as an optional prompt add-on.

## Executive Summary

- Stateless performance remained low overall at `13.4%` (`28/209`).
- All memory-enabled conditions were far stronger overall: `B=74.2%`, `C=72.7%`, `D=73.7%`.
- The best overall condition in this pilot was `B`.
- Best condition by dataset varied: `northwind=D`, `sec_edgar=B`, `bird=C`.
- This means the pilot already supports the main E0 claim that memory matters, but it does not yet support a universal claim that one memory stack dominates all enterprise data settings.

## Overall Results

| Condition | Correct | Total | Accuracy | Gain vs A | MBS |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 28 | 209 | 13.4% | — | — |
| B | 155 | 209 | 74.2% | +60.8 pts | 453.6% |
| C | 152 | 209 | 72.7% | +59.3 pts | 442.9% |
| D | 154 | 209 | 73.7% | +60.3 pts | 450.0% |

## Key Findings

- Tier 2 favored `D` (`81.7%`), while Tier 3 slightly favored `C` (`75.2%`).
- `B` vs `C`: `B` won on `16` turns while `C` won on `13` turns.
- `B` vs `D`: `B` won on `16` turns while `D` won on `15` turns.
- `C` vs `D`: `C` won on `18` turns while `D` won on `20` turns.
- The overall pattern is that working memory already provides most of the benefit; episodic and semantic memory add value, but that value is domain-dependent rather than uniform.

## Dataset View

| Source | A | B | C | D | Best |
| --- | ---: | ---: | ---: | ---: | --- |
| bird | 4.3% | 46.4% | 62.3% | 59.4% | C |
| northwind | 8.6% | 75.7% | 74.3% | 78.6% | D |
| sec_edgar | 27.1% | 100.0% | 81.4% | 82.9% | B |

## Failure Pattern Snapshot

- `A` top failure labels: other_semantic_mismatch=131, sql_error=27, returns_extra_columns=24, wrong_granularity=16
- `B` top failure labels: other_semantic_mismatch=41, returns_extra_columns=12, wrong_granularity=10, company_name_vs_id=5
- `C` top failure labels: other_semantic_mismatch=42, returns_extra_columns=13, wrong_granularity=11, company_name_vs_id=6
- `D` top failure labels: other_semantic_mismatch=43, returns_extra_columns=10, wrong_granularity=8, company_name_vs_id=4

## Figures

![Overall Accuracy](overall_accuracy.png)

![Turn Accuracy](accuracy_by_turn.png)

![Source Accuracy](accuracy_by_source.png)

![Tier Accuracy](accuracy_by_tier.png)

## Forbes / Enterprise Hook

For enterprise AI leaders, the message from this pilot is not simply that memory helps. The more important conclusion is that memory helps exactly where enterprise workflows become conversational and stateful: follow-up questions, narrowed comparisons, and context-carrying analytical threads. Stateless agents are acceptable on first-turn questions, but they fail sharply once the user expects the system to remember prior analytical context. That is the infrastructure argument for enterprise memory systems.

## What Completes Experiment 0

- Expand beyond this 30-session pilot to a larger stratified slice or full corpus.
- Keep `A` as the baseline; do not remove it, because it quantifies both where memory helps and where memory adds no value.
- Report absolute accuracy and absolute gain vs `A` as the primary metrics; use MBS as a secondary interpretive metric.
- Follow with pairwise ablation analysis (`B` vs `C`, `C` vs `D`) by dataset to explain which memory layer is contributing in each domain.
