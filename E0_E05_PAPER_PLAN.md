# E0_E05_PAPER_PLAN.md

This document turns Experiment 0 and Experiment 0.5 into a single paper plan aligned with `master_plan.md`.

## Why Combine E0 and E0.5

`master_plan.md` explicitly treats `E0` and `E0.5` as one research-paper lane:

- `E0` establishes whether memory matters
- `E0.5` establishes how much memory is actually required before returns diminish
- both are mapped to `Research Paper #1`

That combined paper is stronger than `E0` alone because it moves from existence proof to design guidance:

- `E0`: memory helps
- `E0.5`: memory benefit saturates and can be tuned economically

That is a better technical contribution and a more defensible paper arc.

## Paper 1 Scope

### Working Title

`Memory Benefit and Memory Scaling Efficiency: Evaluating When and How Much Memory Enterprise Agents Need`

Alternative title:

`Memory Benefit Score and Memory Scaling Efficiency for Enterprise Memory-Augmented Agents`

### Core Research Questions

1. Do memory-enabled agents outperform stateless agents on enterprise workflows?
2. At what turn depth does memory begin to matter?
3. Which memory layers account for most of the gain?
4. How much working, episodic, and semantic memory is required before returns diminish?
5. What memory configuration produces the best accuracy-to-cost tradeoff?

### Claimed Contributions

The combined paper should aim to contribute:

- a controlled benchmark for `stateless vs working vs episodic vs full stack`
- `Memory Benefit Score (MBS)` for normalized benefit over a stateless baseline
- `Memory Scaling Efficiency (MSE)` for accuracy gain per additional memory cost
- cross-dataset evidence on Northwind, SEC EDGAR, and BIRD
- an empirical finding that memory value is both turn-depth dependent and capacity-dependent

## Publication Constraint

### Forbes First, Public Paper Later

Operating assumption based on your publication rule:

- if Forbes reviews an article, the overlapping content should not already be publicly published elsewhere

Practical implication:

- do not post the full quantitative paper publicly before the Forbes article that uses the same core result is accepted or published
- keep paper drafts private in the repo, private docs, or private Overleaf until the Forbes timing is safe
- avoid posting Medium or arXiv versions that reproduce the same headline figures before Forbes clears

This is a publication-sequencing rule, not a reason to delay technical work.

### Recommended Sequence

1. Build and harden `E0 + E0.5` privately.
2. Draft Forbes Article #2 privately from the same evidence base.
3. Submit the Forbes article when you are ready.
4. Continue paper drafting privately while Forbes is in review.
5. After Forbes publication or safe clearance, publish the broader technical paper and later the Medium deep-dive.

## Current State

### What Already Exists

Completed:

- `E0` 30-session pilot
- `E0` 60-session pilot
- report generation
- summary generation
- failure-label heuristics
- configurable `working_memory_window`

Now added to support `E0.5`:

- configurable `working_memory_window`
- configurable `episodic_top_k`
- configurable `semantic_top_k`
- per-run metadata output for reproducibility

### What Still Does Not Exist

Not yet implemented cleanly:

- semantic memory chunk-size variation
- full statistical testing pipeline
- paper-ready ablation tables by dataset
- paper-ready cost accounting for memory scaling

## E0 Work Required Before the Combined Paper

### 1. Close the Current E0 Rigor Gaps

Required:

- run a tier `1` control slice
- run a larger stratified `E0` slice or full corpus
- compute confidence intervals and significance tests
- expand failure analysis beyond top labels
- finish pairwise ablation for `B vs C` and `C vs D`

Reason:

`E0` is currently a strong pilot, but still not strong enough as the foundation section of Paper 1.

### 2. Freeze the E0 Methodology

Paper-ready details that need to be frozen:

- model and fallback model
- exact session corpus version
- exact evaluation rule for correctness
- exact memory configuration for A, B, C, D
- exact seed/run metadata retained with each final run

## E0.5 Work Required for the Combined Paper

### 1. Define the E0.5 Parameter Sweep

The current `master_plan.md` specifies these scaling knobs:

- episodic memory top-k: `1, 3, 5, 10, 20`
- working memory window: `2, 5, 10`
- semantic memory chunk size

Recommended staged implementation:

Stage 1:

- vary working memory window
- vary episodic retrieval top-k
- vary semantic retrieval top-k as a practical proxy while chunk-size support is being built

Stage 2:

- implement semantic chunk-size variation in the semantic-seed pipeline
- rerun the final semantic scaling section with chunk size as the semantic variable

### 2. Define the E0.5 Experimental Matrix

Recommended minimal matrix for a paper-worthy first pass:

- Conditions:
  - `B` for working-memory scaling
  - `C` for episodic-memory scaling
  - `D` for full-stack scaling
- Working-memory window:
  - `2`, `5`, `10`
- Episodic top-k:
  - `1`, `3`, `5`, `10`, `20`
- Semantic top-k:
  - `1`, `2`, `4`

Interpretation plan:

- for `B`, vary only working-memory window
- for `C`, vary working-memory window and episodic top-k
- for `D`, vary working-memory window, episodic top-k, and semantic top-k

That keeps the study tractable and makes the scaling story interpretable.

### 3. Define the E0.5 Metric

From `master_plan.md`:

`MSE = accuracy_gain / additional_memory_cost`

For the first implementation, define memory cost explicitly as:

- prompt-side working-memory cost: recent-turn tokens included
- episodic-memory retrieval cost: number of retrieved episodes plus retrieval-token footprint
- semantic-memory retrieval cost: number of retrieved notes plus retrieval-token footprint

Paper recommendation:

- report both raw accuracy and `MSE`
- if token-cost instrumentation is not ready immediately, use a documented proxy cost first and replace it with measured token cost before submission

## Engineering Next Steps

### Already Enabled

You can now run `E0.5` style sweeps directly from the existing runner:

```bash
python3 experiments/exp0_foundation/run_experiment.py \
  --conditions B \
  --tiers 1 2 3 \
  --sessions 60 \
  --working-memory-window 2 \
  --run-tag e05_b_wm2
```

```bash
python3 experiments/exp0_foundation/run_experiment.py \
  --conditions C \
  --tiers 1 2 3 \
  --sessions 60 \
  --working-memory-window 5 \
  --episodic-top-k 10 \
  --run-tag e05_c_ep10
```

```bash
python3 experiments/exp0_foundation/run_experiment.py \
  --conditions D \
  --tiers 1 2 3 \
  --sessions 60 \
  --working-memory-window 5 \
  --episodic-top-k 5 \
  --semantic-top-k 4 \
  --run-tag e05_d_full
```

Each run now also writes a `runmeta_*.json` file so the paper methods section can trace the exact configuration.

### Still Needed in Code

Before `E0.5` is finished, add:

- semantic chunk-size support in the semantic memory generation pipeline
- token-cost capture per run or per turn
- a sweep orchestrator script for batch `E0.5` runs
- analysis scripts for `MSE`, saturation curves, and confidence intervals

## Analysis and Figure Plan

### Figures for the Combined Paper

The paper should aim for these figures:

1. `E0` overall accuracy by condition
2. `E0` accuracy by turn depth
3. `E0` accuracy by dataset
4. `E0` pairwise ablation summary by dataset
5. `E0.5` working-memory saturation curve
6. `E0.5` episodic top-k saturation curve
7. `E0.5` full-stack scaling tradeoff curve
8. `MSE` vs memory-cost plot

### Tables for the Combined Paper

Minimum tables:

1. E0 benchmark setup and conditions
2. E0 overall results with absolute gain vs `A`
3. E0 dataset-level results
4. E0 pairwise significance tests
5. E0.5 parameter grid
6. E0.5 best configurations by dataset
7. MSE summary table

## 8-Week Execution Plan

### Weeks 1-2

- close `E0` methodology gaps
- run tier `1` control
- run larger `E0` confirmatory slice
- produce final `E0` baseline tables

### Weeks 3-4

- implement remaining `E0.5` analysis infrastructure
- run the first scaling sweep
- identify promising configurations and prune weak ones

### Weeks 5-6

- run final `E0.5` confirmatory sweep
- compute `MSE`
- generate paper figures and tables
- draft the full paper privately

### Weeks 7-8

- refine Paper 1
- submit Forbes Article #2 if not already submitted
- keep the technical manuscript private until Forbes timing is safe
- prepare arXiv and journal versions after Forbes clearance

## Immediate Priority Order

1. Harden `E0` into a submission-quality foundation.
2. Use the newly exposed runner knobs to start `E0.5` sweep design.
3. Add cost instrumentation and semantic chunk-size support.
4. Draft Paper 1 as `E0 + E0.5`, not `E0` alone.
5. Keep all public release sequencing aligned with the Forbes exclusivity rule.

## Bottom Line

If the goal is a paper in the next `3` to `4` months, the best path is:

- do not wait for `E1` or `E2`
- make `E0` rigorous
- turn `E0.5` into the scaling section
- keep the manuscript private until the Forbes publication window is safe

That gives you one stronger paper rather than one weak paper and one unfinished scaling experiment.
