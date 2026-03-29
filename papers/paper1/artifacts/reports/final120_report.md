# Paper 1 Final Reduced 120-Session Report

- Results file: `results_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json`
- Summary file: `summary_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json`

## Framing

This is Experiment 0 in the enterprise AI memory program: a foundation study asking whether memory infrastructure materially improves multi-turn enterprise SQL tasks before moving on to backend comparisons or systems optimization. The practical industry framing matches the broader Forbes Technology Council angle in this repo: memory should be treated as infrastructure, not as an optional prompt add-on.

## Executive Summary

- Stateless performance remained low overall at `16.4%` (`95/580`).
- All memory-enabled conditions were far stronger overall: `B=79.5%`, `C=77.4%`, `D=77.1%`.
- The best overall condition in this pilot was `B`.
- Best condition by dataset varied: `northwind=C`, `sec_edgar=D`, `bird=B`.
- This means the pilot already supports the main E0 claim that memory matters, but it does not yet support a universal claim that one memory stack dominates all enterprise data settings.

## Overall Results

| Condition | Correct | Total | Accuracy | Gain vs A | MBS |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 95 | 580 | 16.4% | — | — |
| B | 461 | 580 | 79.5% | +63.1 pts | 385.3% |
| C | 449 | 580 | 77.4% | +61.0 pts | 372.6% |
| D | 447 | 580 | 77.1% | +60.7 pts | 370.5% |

## Key Findings

- Tier 2 favored `D` (`74.4%`), while Tier 3 slightly favored `C` (`74.2%`).
- `B` vs `C`: `B` won on `37` turns while `C` won on `25` turns.
- `B` vs `D`: `B` won on `42` turns while `D` won on `28` turns.
- `C` vs `D`: `C` won on `31` turns while `D` won on `29` turns.
- The overall pattern is that working memory already provides most of the benefit; episodic and semantic memory add value, but that value is domain-dependent rather than uniform.

## Dataset View

| Source | A | B | C | D | Best |
| --- | ---: | ---: | ---: | ---: | --- |
| bird | 9.0% | 69.0% | 66.0% | 60.5% | B |
| northwind | 14.3% | 78.8% | 80.4% | 78.3% | C |
| sec_edgar | 26.2% | 91.1% | 86.4% | 93.2% | D |

## Failure Pattern Snapshot

- `A` top failure labels: other_semantic_mismatch=361, returns_extra_columns=64, sql_error=63, wrong_granularity=48
- `B` top failure labels: other_semantic_mismatch=84, returns_extra_columns=33, wrong_granularity=29, company_name_vs_id=13
- `C` top failure labels: other_semantic_mismatch=99, returns_extra_columns=30, wrong_granularity=28, company_name_vs_id=12
- `D` top failure labels: other_semantic_mismatch=96, returns_extra_columns=34, wrong_granularity=30, company_name_vs_id=16

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
