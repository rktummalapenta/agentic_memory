# Experiment 0 Cross-Dataset Pilot Report

- Results file: `results_20260315T181518Z_conds-A-B-C-D_tiers-2-3_sessions-60_model-gpt-5-mini.json`
- Summary file: `summary_20260315T181518Z_conds-A-B-C-D_tiers-2-3_sessions-60_model-gpt-5-mini.json`

## Framing

This is Experiment 0 in the enterprise AI memory program: a foundation study asking whether memory infrastructure materially improves multi-turn enterprise SQL tasks before moving on to backend comparisons or systems optimization. The practical industry framing matches the broader Forbes Technology Council angle in this repo: memory should be treated as infrastructure, not as an optional prompt add-on.

## Executive Summary

- Stateless performance remained low overall at `11.5%` (`47/410`).
- All memory-enabled conditions were far stronger overall: `B=72.0%`, `C=78.5%`, `D=72.2%`.
- The best overall condition in this pilot was `C`.
- Best condition by dataset varied: `northwind=B`, `sec_edgar=C`, `bird=C`.
- This means the pilot already supports the main E0 claim that memory matters, but it does not yet support a universal claim that one memory stack dominates all enterprise data settings.

## Overall Results

| Condition | Correct | Total | Accuracy | Gain vs A | MBS |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 47 | 410 | 11.5% | — | — |
| B | 295 | 410 | 72.0% | +60.5 pts | 527.7% |
| C | 322 | 410 | 78.5% | +67.1 pts | 585.1% |
| D | 296 | 410 | 72.2% | +60.7 pts | 529.8% |

## Key Findings

- Tier 2 favored `D` (`73.3%`), while Tier 3 slightly favored `C` (`77.6%`).
- `B` vs `C`: `B` won on `13` turns while `C` won on `40` turns.
- `B` vs `D`: `B` won on `35` turns while `D` won on `36` turns.
- `C` vs `D`: `C` won on `40` turns while `D` won on `14` turns.
- The overall pattern is that working memory already provides most of the benefit; episodic and semantic memory add value, but that value is domain-dependent rather than uniform.

## Dataset View

| Source | A | B | C | D | Best |
| --- | ---: | ---: | ---: | ---: | --- |
| bird | 3.0% | 52.2% | 61.2% | 53.0% | C |
| northwind | 8.0% | 77.4% | 77.4% | 75.9% | B |
| sec_edgar | 23.0% | 85.6% | 96.4% | 87.1% | C |

## Failure Pattern Snapshot

- `A` top failure labels: other_semantic_mismatch=273, sql_error=51, returns_extra_columns=49, wrong_granularity=30
- `B` top failure labels: other_semantic_mismatch=89, returns_extra_columns=24, wrong_granularity=23, company_name_vs_id=9
- `C` top failure labels: other_semantic_mismatch=63, returns_extra_columns=24, wrong_granularity=22, company_name_vs_id=9
- `D` top failure labels: other_semantic_mismatch=86, returns_extra_columns=26, wrong_granularity=23, company_name_vs_id=9

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
