# Paper 1 Review Response

This file maps the major reviewer comments to the current revision actions.

## Status

Reviewer summary:

- arXiv-ready after caveats and methodology gaps are fixed
- stronger venue submission would still need major revision

Current revision strategy:

- fix the methodology gaps first
- narrow the paper claims where the statistics do not support stronger claims
- add a first mechanistic explanation for the scaling degradation result

## Major Reviewer Concerns And Responses

### 1. Mechanistic explanation for why larger memory loses

Reviewer concern:

- `wm10` losing to `wm2` was interesting but underexplained

Response:

- Added an explicit failure-mode discussion to the manuscript
- Compared `wm2` against `wm10` and `wm5`
- The larger-window losses are dominated by:
  - semantic mismatches
  - extra-column outputs
  - wrong-granularity outputs
- These failures cluster in later turns and support a plausible mechanism:
  - context dilution
  - stale carryover
  - over-preservation of prior answer structure

### 2. Recommendation of `B` despite non-significant `B/C/D` differences

Reviewer concern:

- the paper should not treat `B` as universally best if `B/C/D` differences are not statistically significant

Response:

- Manuscript now states this explicitly
- The recommendation of `B wm2` is framed as a practical default, not a statistically proven universal winner
- The justification is:
  - highest observed accuracy
  - highest MSE
  - lowest proxy memory cost among top-performing conditions
  - simpler implementation

### 3. Correctness evaluation was undefined

Reviewer concern:

- correctness methodology was a critical missing piece

Response:

- Fixed in the manuscript
- The paper now states that correctness is execution-based result equivalence:
  - both queries must execute
  - normalized result rows must match exactly
- This makes extra columns, wrong granularity, and wrong aggregation all count as incorrect

### 4. Thin per-cell sample for dataset conclusions

Reviewer concern:

- source-wise claims may be overinterpreted

Response:

- Manuscript now explicitly treats source-wise rankings as heterogeneity evidence rather than final domain rankings
- Source-level findings remain in the paper, but with a narrower claim

### 5. Single-model limitation

Reviewer concern:

- findings may depend on `gpt-5-mini` context behavior

Response:

- Manuscript now states this directly in limitations
- The scaling degradation result is framed as evidence for this model family and benchmark, not as a universal law

## Moderate Reviewer Concerns And Responses

### 6. Tier 1 ceiling effect

Response:

- Manuscript now clarifies that Tier 1 is a ceiling-effect control
- It is not used to claim memory is irrelevant to every simple query

### 7. MSE clarity

Response:

- Manuscript now states explicitly that higher MSE is better
- It is defined as accuracy gain per unit of additional injected memory

### 8. Dataset heterogeneity underexplored

Response:

- Manuscript now emphasizes dataset heterogeneity as a qualified but meaningful result
- The claim is framed as domain dependence, not universal ranking

### 9. Enterprise framing too broad

Response:

- Manuscript now uses `enterprise-oriented`
- It explains why Northwind and BIRD are treated as enterprise-relevant rather than as proprietary enterprise corpora

### 10. Related work missing

Response:

- Added first-pass citations for:
  - `Spider`
  - `SParC`
  - `CoSQL`
  - `CQR-SQL`
  - `BIRD`
  - `RAG`
  - `Mem0`

## Remaining Work

Still needed before submission:

- add more related-work coverage and polish the positioning section
- tighten the results and discussion wording
- replace placeholder author and affiliation text
- decide whether to keep plain arXiv style or move to a target-venue template

## Evidence Used For The New Responses

- [main.tex](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/arxiv/main.tex)
- [paper1_statistical_summary.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/paper1_statistical_summary.md)
- [error_analysis.txt](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/error_analysis.txt)
- [sql_evaluator.py](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/evaluation/sql_evaluator.py)
