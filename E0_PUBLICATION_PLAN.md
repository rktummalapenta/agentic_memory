# E0_PUBLICATION_PLAN.md

This document formalizes the publication plan for Experiment 0 based on the two completed pilot runs on 2026-03-15.

## Baseline Evidence

Experiment 0 currently has two completed pilot runs:

- 30-session pilot:
  - `experiments/exp0_foundation/results/results_20260315T114840Z_conds-A-B-C-D_tiers-2-3_sessions-30_model-gpt-5-mini.json`
  - `experiments/exp0_foundation/reports/20260315T114840Z_conds-A-B-C-D_tiers-2-3_sessions-30_model-gpt-5-mini/report.md`
- 60-session cross-dataset pilot:
  - `experiments/exp0_foundation/results/results_20260315T181518Z_conds-A-B-C-D_tiers-2-3_sessions-60_model-gpt-5-mini.json`
  - `experiments/exp0_foundation/reports/20260315T181518Z_conds-A-B-C-D_tiers-2-3_sessions-60_model-gpt-5-mini/report.md`

The 60-session run is the current baseline artifact for publication.

Latest headline result:

| Condition | Correct | Total | Accuracy | Gain vs A |
|---|---:|---:|---:|---:|
| A | 47 | 410 | 11.5% | - |
| B | 295 | 410 | 72.0% | +60.5 pts |
| C | 322 | 410 | 78.5% | +67.1 pts |
| D | 296 | 410 | 72.2% | +60.7 pts |

Stable conclusions already supported by both runs:

- memory-enabled agents materially outperform the stateless baseline on multi-turn enterprise SQL tasks
- the main benefit appears after context must be carried across turns
- working memory provides most of the lift
- episodic and semantic memory can add value, but the benefit is domain-dependent
- the current evidence supports "memory matters" more strongly than "one memory stack always wins"

Claims not yet safe to make as final publication claims:

- that one memory condition is universally best across domains
- that memory provides negligible benefit on single-turn tasks, because the completed pilots were limited to tiers `2` and `3`
- that the observed condition ranking is statistically stable enough for paper submission without a larger run

## Publication Decision

### Forbes Technology Council
Do not wait for Experiment 1 or Experiment 2.

Experiment 0 already supports a strong CEO/CTO/industry-leader article because the executive takeaway is architectural, not academic:

- stateless agents fail when work becomes conversational
- memory should be treated as infrastructure
- the first decision is not "which vector database?" but "do we need memory at all?"

The Forbes piece should be published from Experiment 0 alone, with careful wording that this is a foundation study or pilot benchmark.

### Technical Paper
Do not wait for Experiment 1 or Experiment 2 to start writing.

Start drafting Paper 1 now, but do not finalize submission yet. The current E0 evidence is strong enough for an internal draft and outline, but there are still technical gaps that should be closed before treating it as a submission-ready research paper.

## Forbes Article Plan

### Working Positioning

Target audience:

- CEO
- CTO
- CIO
- VP Engineering
- enterprise AI leader

Core thesis:

Most organizations talk about agent memory as a feature. The Experiment 0 pilots show it behaves more like infrastructure: on follow-up analytical work, stateless systems break down and memory-enabled systems remain usable.

Recommended title directions:

- `Enterprise AI Agents Need Memory Infrastructure, Not Better Prompts`
- `Why Stateless AI Agents Fail the Moment Work Becomes Conversational`
- `Memory Matters in Enterprise AI, But Not Where Most Teams Think`

Recommended article structure:

1. Open with the core contrast from the 60-session run:
   - stateless `11.5%`
   - memory-enabled `72.0%` to `78.5%`
2. Explain the business meaning:
   - first-turn demos are misleading
   - real enterprise work is follow-up work
3. Present the practical insight:
   - working memory already captures most of the gain
   - richer memory layers help, but not uniformly across domains
4. End with operator guidance:
   - add a stateless baseline to every internal benchmark
   - measure by turn depth, not only average accuracy
   - treat memory as an infrastructure layer before backend optimization

Claims the Forbes article can safely make now:

- memory is a prerequisite for reliable follow-up analysis
- average benchmark numbers hide turn-depth failure
- backend debates are premature if the memory-vs-stateless question is not answered first

Claims the Forbes article should avoid for now:

- `C` is definitively the best enterprise memory architecture
- the result generalizes to every enterprise task category
- the exact benefit curve for single-turn tasks, because tier `1` was not part of the completed pilots

### What Makes the Forbes Piece Strong Enough Now

- there are two runs, not one
- the directional result is consistent across both runs
- the result is legible to executive readers
- the article can be framed around the infrastructure decision, not a paper-level universal claim

## Technical Paper Plan

### Working Paper

Title:

`Memory Benefit Score: A Normalized Metric for Evaluating Memory-Augmented Agent Performance on Enterprise Tasks`

Core claim:

Memory benefit should be evaluated as a controlled comparison against a stateless baseline, and the benefit is non-linear with respect to conversational depth and task context.

Submission recommendation:

- start the draft now
- do not submit yet
- target arXiv after E0 is tightened
- then consider IEEE Access or ACL Findings

### Current Paper Contributions Already Supported

- an explicit E0 benchmark framing: stateless vs working vs episodic vs full stack
- a named metric: `MBS`
- cross-dataset pilot evidence on Northwind, SEC EDGAR, and BIRD
- evidence that memory benefit is large in multi-turn enterprise SQL sessions
- evidence that layer contributions differ by dataset

### Gaps Before the Paper Is Submission-Ready

#### Gap 1: Missing Tier 1 Control

The current completed pilots use `--tiers 2 3`.

That means the paper is not yet strong enough to make the full claim that memory adds little or no benefit on single-turn tasks. If that claim is central to the paper, a tier `1` control run is still needed.

Required action:

- run a stratified E0 slice including tier `1`
- recompute turn-depth and tier-level summaries with tier `1` present

#### Gap 2: Pilot Scale Is Still Limited

The 60-session run is strong as a pilot, but still better described as a pilot than a finalized benchmark corpus.

Required action:

- either run a larger stratified sample or run the full planned E0 corpus
- keep condition `A` as the baseline in every table

#### Gap 3: Missing Statistical Rigor

The current reports are descriptive. A technical paper should also show uncertainty and significance.

Required action:

- compute confidence intervals on condition accuracies
- run pairwise significance tests for `A vs B`, `A vs C`, `A vs D`
- run pairwise significance or matched comparison tests for `B vs C` and `C vs D`

#### Gap 4: Pairwise Ablation Analysis Is Not Finished

The reports already show win counts, but the causal interpretation is still too shallow for a paper.

Required action:

- analyze `B vs C` and `C vs D` by dataset
- identify where episodic retrieval helps or hurts
- identify where semantic memory recovers failures from `B` or `C`

#### Gap 5: Failure Analysis Needs a Fuller Section

The current reports include top failure labels, which is a good start but not yet a complete error-analysis section.

Required action:

- expand error analysis by source and by turn range
- include representative failure examples
- quantify how memory changes error type, not only total accuracy

#### Gap 6: Methodology Freeze Is Not Yet Explicit

A paper needs a stable methods section with exact run settings and reproducibility details.

Required action:

- lock the model name and run date in the methods section
- record dataset versions and session-generation version
- document memory configuration for A/B/C/D in a paper-ready table
- record evaluation criteria for exact result-set match

#### Gap 7: MBS Should Be Secondary in Tables

The pilots show that `MBS` becomes hard to interpret when the stateless baseline is near zero.

Required action:

- keep `MBS` as the named contribution
- use absolute accuracy and absolute gain vs `A` as the primary reported results
- move `MBS` to secondary tables or interpretation text

## Recommended Immediate Work Order

### For Forbes

Proceed now.

Next concrete steps:

1. Draft the Forbes article from the 60-session report.
2. Use the 30-session run as supporting consistency evidence, not as the main artifact.
3. Frame the piece as a foundation benchmark and infrastructure lesson.

### For the Paper

Proceed with drafting, but hold submission.

Next concrete steps:

1. Build the paper outline and methods section now.
2. Run the missing tier `1` control slice.
3. Run a larger E0 slice or full corpus.
4. Add significance testing, ablation, and expanded failure analysis.
5. Freeze the final E0 narrative only after those are done.

## Final Recommendation

Do not wait for Experiments 1 and 2 to write the Forbes article.

Do not wait for Experiments 1 and 2 to start the technical paper draft.

But do wait before submitting the technical paper. Experiment 0 is already good enough for executive publication and internal paper drafting, yet it still needs more rigor before it should be treated as a finished research contribution.
