# Experiment 0 Confirmatory 60-Session Report

- Results file: `results_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60.json`
- Summary file: `summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60.json`

## Framing

This is Experiment 0 in the enterprise AI memory program: a foundation study asking whether memory infrastructure materially improves multi-turn enterprise SQL tasks before moving on to backend comparisons or systems optimization. The practical industry framing matches the broader Forbes Technology Council angle in this repo: memory should be treated as infrastructure, not as an optional prompt add-on.

## Executive Summary

- Stateless performance remained low overall at `16.8%` (`50/297`).
- All memory-enabled conditions were far stronger overall: `B=76.1%`, `C=76.4%`, `D=72.7%`.
- The best overall condition in this pilot was `C`.
- Best condition by dataset varied: `northwind=C`, `sec_edgar=B`, `bird=C`.
- This means the pilot already supports the main E0 claim that memory matters, but it does not yet support a universal claim that one memory stack dominates all enterprise data settings.

## Overall Results

| Condition | Correct | Total | Accuracy | Gain vs A | MBS |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 50 | 297 | 16.8% | — | — |
| B | 226 | 297 | 76.1% | +59.3 pts | 352.0% |
| C | 227 | 297 | 76.4% | +59.6 pts | 354.0% |
| D | 216 | 297 | 72.7% | +55.9 pts | 332.0% |

## Key Findings

- Tier 2 favored `D` (`72.5%`), while Tier 3 slightly favored `C` (`75.1%`).
- `B` vs `C`: `B` won on `14` turns while `C` won on `15` turns.
- `B` vs `D`: `B` won on `28` turns while `D` won on `18` turns.
- `C` vs `D`: `C` won on `24` turns while `D` won on `13` turns.
- The overall pattern is that working memory already provides most of the benefit; episodic and semantic memory add value, but that value is domain-dependent rather than uniform.

## Dataset View

| Source | A | B | C | D | Best |
| --- | ---: | ---: | ---: | ---: | --- |
| bird | 9.8% | 57.8% | 63.7% | 60.8% | C |
| northwind | 13.3% | 73.3% | 75.2% | 75.2% | C |
| sec_edgar | 28.9% | 100.0% | 92.2% | 83.3% | B |

## Failure Pattern Snapshot

- `A` top failure labels: other_semantic_mismatch=179, sql_error=40, returns_extra_columns=35, wrong_granularity=21
- `B` top failure labels: other_semantic_mismatch=50, returns_extra_columns=21, wrong_granularity=19, company_name_vs_id=10
- `C` top failure labels: other_semantic_mismatch=51, returns_extra_columns=19, wrong_granularity=16, company_name_vs_id=8
- `D` top failure labels: other_semantic_mismatch=60, returns_extra_columns=19, wrong_granularity=16, company_name_vs_id=8

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
