# Memory Benefit and Memory Scaling Efficiency for Enterprise Text-to-SQL Agents

## Abstract

Memory is widely treated as a necessary component of production AI agents, but the actual benefit and required memory footprint are often unclear. We evaluate memory-augmented agents on a multi-turn enterprise Text-to-SQL benchmark spanning Northwind, SEC EDGAR, and BIRD under four conditions: stateless, working memory only, working plus episodic memory, and a full stack including semantic hints. We then study memory scaling by varying working-memory window size and retrieval depth. Across exploratory, confirmatory, and final reduced runs, memory increases accuracy from roughly `16%` to `17%` in the stateless condition to roughly `77%` to `80%` in memory-enabled conditions on multi-turn tasks, while providing little additional value on single-turn controls. In the final reduced `120`-session run, a small working-memory configuration (`wm2`) achieves the best overall accuracy (`79.5%`) and the best memory-scaling efficiency. Exact paired tests show that all memory-enabled conditions significantly outperform the stateless baseline, while differences among the top memory-enabled conditions are not statistically significant at `0.05`. These findings suggest that enterprise Text-to-SQL memory should be sized selectively rather than maximized by default.

## 1. Introduction

Enterprise Text-to-SQL systems are often evaluated as if each request is independent. In actual use, however, users ask follow-up questions, refine filters, request alternate aggregations, and revisit earlier context. This makes memory a first-class systems question rather than an optional prompting trick.

The problem is that memory is usually discussed in broad terms. It is often assumed that more memory is better, or that a full memory stack is inherently preferable to a lighter approach. For enterprise deployment, those assumptions are too weak. Teams need to know whether memory materially changes accuracy, which layer of memory is doing most of the work, and how much memory is enough before the additional complexity stops paying off.

This paper studies those questions in the setting of multi-turn enterprise Text-to-SQL. We compare stateless execution with working memory, episodic retrieval, and semantic hints. We also examine whether larger memory settings improve or degrade performance. The result is a practical claim: memory clearly helps multi-turn Text-to-SQL, but more memory is not monotonically better. The strongest current operating point is a small working-memory configuration, with selective retrieval used only when necessary.

## 2. Research Questions

This paper addresses two research questions:

1. Does memory materially improve multi-turn enterprise Text-to-SQL accuracy?
2. If memory helps, how much memory is enough before returns flatten or decline?

## 3. Benchmark and Setup

### 3.1 Task Domain

The benchmark is focused on enterprise-oriented Text-to-SQL across three datasets:

- `Northwind`
- `SEC EDGAR`
- `BIRD`

The sessions include single-turn and multi-turn analytical tasks. This allows the benchmark to distinguish easy controls from stateful follow-up reasoning.

### 3.2 Memory Conditions

We evaluate four memory conditions:

- `A`: stateless baseline
- `B`: working memory only
- `C`: working memory plus episodic retrieval
- `D`: working memory plus episodic retrieval plus semantic hints

For scaling analysis, we vary:

- working-memory window size
- episodic retrieval top-k
- semantic retrieval top-k

### 3.3 Runs Used In This Paper

The paper uses three layers of evidence:

- exploratory runs
- confirmatory runs
- one final reduced inferential bundle

The current final inferential bundle is:

- `A`
- `B wm2`
- `C ep3`
- `D sem1`

with:

- `tiers 1 2 3`
- `120` sessions
- `gpt-5-mini`

The earlier `36`-session and `60`-session runs are used as stability evidence rather than pooled into the main inferential test.

## 4. Methods

### 4.1 Accuracy

The primary metric is exact task correctness as recorded in the experiment result bundles.

### 4.2 Memory Benefit

We report absolute accuracy and absolute gain versus the stateless baseline `A`. We treat absolute accuracy as primary and `MBS` as a secondary interpretive measure because relative gains become distorted when the baseline is near zero.

### 4.3 Memory Scaling Efficiency

We use `MSE` as a practical efficiency metric. It relates accuracy gain to a proxy for memory injected into the prompt. This paper uses the existing first-pass proxy based on:

- working turns injected
- episodic turns injected
- semantic hints injected

### 4.4 Statistical Analysis

For the final reduced `120`-session bundle, we compute:

- Wilson `95%` confidence intervals for accuracy
- paired bootstrap `95%` intervals for accuracy deltas
- exact McNemar tests for matched condition comparisons
- Holm correction across the pairwise tests

All statistical analysis is deterministic and based on saved JSON results. No LLM calls are used in the analysis stage.

## 5. Results

### 5.1 Overall Accuracy

From the final reduced `120`-session run:

- `A`: `16.4%`
- `B wm2`: `79.5%`
- `C ep3`: `77.4%`
- `D sem1`: `77.1%`

The corresponding `95%` confidence intervals are:

- `A`: `[13.6%, 19.6%]`
- `B wm2`: `[76.0%, 82.6%]`
- `C ep3`: `[73.8%, 80.6%]`
- `D sem1`: `[73.5%, 80.3%]`

The main result is stable: memory changes performance from failure-level to usable-level on multi-turn enterprise Text-to-SQL.

### 5.2 Tier-Level Behavior

The benchmark shows a clear separation between simple control tasks and stateful multi-turn tasks.

In the final reduced run:

- Tier 1:
  - `A=100.0%`
  - `B=100.0%`
  - `C=100.0%`
  - `D=100.0%`
- Tier 2:
  - `A=15.6%`
  - `B=81.2%`
  - `C=79.4%`
  - `D=74.4%`
- Tier 3:
  - `A=7.9%`
  - `B=76.6%`
  - `C=74.2%`
  - `D=75.8%`

This shows that memory is not the main differentiator on simple one-turn tasks. The effect is concentrated in follow-up analytical work.

### 5.3 Pairwise Statistical Results

All memory-enabled conditions significantly outperform `A`.

For the final reduced run:

- `A` vs `B wm2`: significant
- `A` vs `C ep3`: significant
- `A` vs `D sem1`: significant

Differences among the top memory-enabled conditions are directionally meaningful but not statistically significant at `0.05` after correction:

- `B wm2` vs `C ep3`: not significant
- `B wm2` vs `D sem1`: not significant
- `C ep3` vs `D sem1`: not significant

This means the paper should emphasize the strength of the memory effect, while keeping the ranking among top memory configurations appropriately cautious.

### 5.4 Memory Scaling

The scaling result is one of the most important contributions of the paper.

Key evidence:

- `B wm2`: `79.5%`
- `B wm5`: `71.0%`
- `B wm10`: `73.3%`
- `C ep3`: `77.4%`
- `C ep10`: `72.8%`
- `D sem1`: `77.1%`
- `D sem4`: `74.4%`

This shows that larger memory settings do not monotonically improve accuracy.

### 5.5 Efficiency

From the final reduced `120`-session analysis:

- `B wm2`: `MSE=0.435714`
- `C ep3`: `MSE=0.132090`
- `D sem1`: `MSE=0.107975`

`B wm2` is both the best accuracy result and the strongest efficiency result in the final reduced set.

### 5.6 Dataset-Level Variation

The best condition varies by dataset:

- `bird`: `B`
- `northwind`: `C`
- `sec_edgar`: `D`

This supports a narrower and more defensible claim: deeper memory layers can help in domain-specific ways, but they are not the universal best default.

### 5.7 Turn-Band View

For the practical product use case of short follow-up chains:

- turns `1-4`
  - `A=25.0%`
  - `B=79.7%`
  - `C=78.3%`
  - `D=78.1%`

This suggests that a small working-memory configuration is the strongest current default for enterprise Text-to-SQL systems where users ask a few follow-up questions.

## 6. Discussion

The main result is not merely that memory helps. The stronger result is that **selective memory helps**, while heavier memory is not automatically better.

Working memory appears to provide most of the useful lift. Episodic memory can help, especially when additional recall is needed, but high retrieval depth is not justified by the current results. Semantic hints can be useful in domain-specific settings, particularly `sec_edgar`, but the full stack is not the overall winner.

This has direct implications for enterprise Text-to-SQL design. Teams should not default to maximal memory windows or broad retrieval injection. Instead, they should begin with a lightweight working-memory configuration and add retrieval selectively only when the product behavior actually needs it.

## 7. Practical Claims

The paper supports the following claims:

1. Memory materially improves multi-turn enterprise Text-to-SQL accuracy.
2. The benefit is concentrated in multi-turn follow-up tasks rather than single-turn controls.
3. Working memory provides most of the gain.
4. Selective retrieval can help, but larger memory is not monotonically better.
5. The best current operating point is small working memory with optional selective retrieval.

The paper should not claim:

- one universal winning memory stack
- semantic memory as the best default in general
- generalization beyond Text-to-SQL without additional experiments
- a fully solved universal memory optimum

## 8. Limitations

- The current evidence is from one model family, `gpt-5-mini`.
- The main inferential result is based on the reduced `120`-session set rather than a full large-grid sweep.
- The proxy memory-cost metric is useful for relative comparison, but it is not yet a full latency or dollar-cost model.
- The findings are scoped to enterprise multi-turn Text-to-SQL.

## 9. Reproducibility And Evidence Trail

The paper workspace includes:

- exact staged result bundles
- exact statistical outputs
- the analysis script used to compute the inferential tables
- the shell script used to run the final reduced experiment set
- a hashed artifact manifest

See [PROVENANCE.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/PROVENANCE.md) and [artifact_manifest.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifact_manifest.md).

## 10. Next Writing Steps

1. Add related work and citations.
2. Convert the markdown draft into arXiv/LaTeX format.
3. Select the final figures from the staged report assets.
4. Tighten the methods and evaluation wording.
