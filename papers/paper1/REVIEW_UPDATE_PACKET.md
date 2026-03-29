# Paper 1 Review Update Packet

This note is intended to accompany the revised draft after incorporating feedback from the first two rounds of review.

## What Was Updated

The revised draft addresses the main reviewer concerns in five areas:

1. correctness evaluation is now explicitly defined
2. `MSE` is now explicitly defined and interpreted
3. the recommendation of `B wm2` is now framed as a practical default rather than a statistically proven universal winner
4. the scaling degradation result now includes a first mechanistic explanation
5. the manuscript now acknowledges the long-session interaction and the tier/source caveats

## Main Statistical Position

The paper now makes these statistically supported claims:

- all memory-enabled conditions significantly outperform the stateless baseline
- the main memory effect is large and stable
- `B wm2`, `C ep3`, and `D sem1` are not statistically separable at `0.05` in the final reduced run

The paper therefore does **not** claim that `B` is a universal winner. Instead it claims:

- `B wm2` is the strongest current default for short-to-moderate sessions because it has the best observed accuracy, best `MSE`, and lowest complexity among the top-performing conditions

## Important New Clarification: Long-Session Interaction

The revised draft now explicitly acknowledges the long-session pattern:

| Condition | Turns 1-4 | Turns 5-7 | Turns 8-10 |
| --- | ---: | ---: | ---: |
| B wm2 | 79.7% | 77.5% | 81.0% |
| C ep3 | 78.3% | 69.2% | 84.0% |
| D sem1 | 78.1% | 63.3% | 90.0% |

Interpretation:

- `B wm2` is the best overall default
- deeper memory becomes more competitive at the longest turn band
- this supports a more nuanced decision rule:
  - use `B wm2` for typical short sessions
  - consider deeper retrieval for long, state-heavy analytical chains

## Per-Source Turn-Band Breakdown

The reviewer asked whether the late-turn `D` advantage is driven only by `sec_edgar`. It is not.

From [per_source_turn_band.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/per_source_turn_band.csv):

### `bird`

- turns `8-10`
  - `B=75.0%`
  - `C=100.0%`
  - `D=100.0%`

### `northwind`

- turns `8-10`
  - `B=78.8%`
  - `C=78.8%`
  - `D=78.8%`

### `sec_edgar`

- turns `8-10`
  - `B=88.6%`
  - `C=74.3%`
  - `D=91.4%`

Interpretation:

- the late-turn `D` advantage is not only a `sec_edgar` artifact
- `bird` also strongly favors deeper memory at turns `8-10`
- `northwind` is effectively tied
- the session-depth interaction is therefore real, but still should be treated cautiously because the late-turn subsets are smaller than the early-turn subsets

## Correctness Evaluation Is Now Locked Down

The paper now states explicitly:

- correctness is execution-based
- both generated SQL and ground-truth SQL must execute
- normalized result rows must match exactly

This means:

- extra columns are incorrect
- wrong granularity is incorrect
- wrong aggregate values are incorrect

## Mechanistic Explanation Added

The revised paper now gives a first mechanistic explanation for why larger working-memory windows can lose:

- larger-window losses are dominated by:
  - semantic mismatches
  - extra-column outputs
  - wrong-granularity outputs
- these occur disproportionately in later turns
- the likely mechanism is:
  - context dilution
  - stale carryover
  - over-preservation of prior answer structure

## SEC EDGAR Baseline Anomaly

The revised paper now discusses the higher stateless baseline on `sec_edgar`:

- `bird`: `9.0%`
- `northwind`: `14.3%`
- `sec_edgar`: `26.2%`

And within `A`, by tier:

- `bird`: Tier 2 `1.8%`, Tier 3 `2.3%`
- `northwind`: Tier 2 `11.5%`, Tier 3 `6.5%`
- `sec_edgar`: Tier 2 `34.6%`, Tier 3 `15.1%`

The revised draft frames this as a source-difficulty difference rather than ignoring it.

## Tier Imbalance Is Now Explicit

The revised manuscript now states that the final reduced bundle is tier-weighted:

- Tier 1: `40` turns
- Tier 2: `160` turns
- Tier 3: `380` turns

So the overall accuracy is intentionally dominated by deeper multi-turn behavior.

## Stability Table Caveat Is Now Explicit

The revised paper now states that:

- earlier `36` and `60` runs are replication and stability evidence
- they are not exact configuration replications of the final reduced run
- the final reduced run uses tuned settings:
  - `B wm2`
  - `C ep3`
  - `D sem1`

## Files To Review

- revised manuscript:
  - [main.tex](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/arxiv/main.tex)
  - [main.pdf](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/arxiv/main.pdf)
- statistical summary:
  - [paper1_statistical_summary.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/paper1_statistical_summary.md)
- review response tracker:
  - [REVIEW_RESPONSE.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/REVIEW_RESPONSE.md)
- per-source turn-band data:
  - [per_source_turn_band.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/per_source_turn_band.csv)

## Remaining Open Items

Still open for later revision:

- per-dataset pairwise significance tests
- multiple-comparison correction for subgroup-level inferential claims
- additional effect-size metrics beyond accuracy delta
- further expansion of related work
