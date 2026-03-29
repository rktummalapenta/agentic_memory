# Paper 1 Shareable Brief

## Working Title

`Memory Benefit and Memory Scaling Efficiency for Enterprise Text-to-SQL Agents`

Alternative title:

`When Memory Helps and How Much Memory Is Enough for Enterprise Text-to-SQL`

## One-Line Scope

This paper is about **memory benefit and memory sizing for multi-turn enterprise Text-to-SQL systems**. It is not a general agent-memory paper across all tasks.

## Objective

The paper asks two concrete questions:

1. Does memory materially improve multi-turn enterprise Text-to-SQL accuracy?
2. If memory helps, how much memory is enough before returns flatten or decline?

The practical goal is to help enterprise teams decide whether memory should be added to Text-to-SQL systems and how aggressively it should be sized.

## Benchmark Framing

The experiments use an enterprise-oriented Text-to-SQL benchmark spanning:

- `Northwind`
- `SEC EDGAR`
- `BIRD`

The benchmark includes single-turn and multi-turn sessions so the paper can separate:

- easy control tasks
- stateful follow-up tasks
- longer analytical chains

## Experimental Conditions

The paper studies four memory conditions:

- `A`: stateless baseline
- `B`: working memory only
- `C`: working memory + episodic retrieval
- `D`: working memory + episodic retrieval + semantic hints

The paper also studies memory scaling:

- working-memory window size
- episodic retrieval depth
- semantic retrieval depth

## Experiment Set Used

Current evidence comes from:

- E0 pilot: `tiers 2 3`, `30` sessions
- E0 pilot: `tiers 2 3`, `60` sessions
- E0 exploratory: `tiers 1 2 3`, `36` sessions
- E0 confirmatory: `tiers 1 2 3`, `60` sessions
- E0/E0.5 final reduced confirmatory set: `tiers 1 2 3`, `120` sessions

The final inferential result bundle is:

- `A`
- `B wm2`
- `C ep3`
- `D sem1`

with:

- `tiers 1 2 3`
- `120` sessions
- model: `gpt-5-mini`

## Core Findings

### 1. Memory materially improves multi-turn Text-to-SQL accuracy

From the final reduced `120`-session run:

- `A`: `16.4%`
- `B wm2`: `79.5%`
- `C ep3`: `77.4%`
- `D sem1`: `77.1%`

Interpretation:

- memory changes performance from failure-level to usable-level on multi-turn enterprise Text-to-SQL

### 2. The benefit is concentrated in multi-turn work, not simple controls

From the final reduced run:

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

Interpretation:

- memory is not the story for simple one-turn tasks
- memory becomes decisive once the user asks follow-up analytical questions

### 3. Working memory provides most of the gain

Across runs, `B` remains consistently strong. In the final reduced run:

- `B wm2` is the best overall configuration
- `B` beats `C` on `37` turns and loses on `25`
- `B` beats `D` on `42` turns and loses on `28`

Interpretation:

- short-range conversational context retention is doing most of the useful work

### 4. More memory is not monotonically better

Key scaling evidence:

- `B wm2`: `79.5%`
- `B wm5`: `71.0%`
- `B wm10`: `73.3%`
- `C ep3`: `77.4%`
- `C ep10`: `72.8%`
- `D sem1`: `77.1%`
- `D sem4`: `74.4%`

Interpretation:

- larger memory windows and deeper retrieval do not automatically improve Text-to-SQL accuracy
- selective memory appears better than maximal memory

### 5. The best current operating point is small working memory with optional selective retrieval

From the final reduced E0.5 analysis:

- `B wm2`: `79.5%`, `MSE=0.435714`
- `C ep3`: `77.4%`, `MSE=0.132090`
- `D sem1`: `77.1%`, `MSE=0.107975`

Interpretation:

- `B wm2` is currently the strongest practical default
- `C ep3` is the best escalation option if extra recall is needed
- `D sem1` is domain-helpful in some cases but not the overall best default

## Statistical Summary

The current statistical analysis on the final reduced `120`-session run shows:

- `A` vs `B wm2`: significant
- `A` vs `C ep3`: significant
- `A` vs `D sem1`: significant
- `B wm2` vs `C ep3`: not significant at `0.05`
- `B wm2` vs `D sem1`: not significant at `0.05`
- `C ep3` vs `D sem1`: not significant at `0.05`

Interpretation:

- the paper can strongly claim that memory helps
- the paper should not overclaim that one memory stack is universally dominant

## Dataset-Level Observation

The best condition varies by dataset:

- `bird`: `B`
- `northwind`: `C`
- `sec_edgar`: `D`

Interpretation:

- deeper memory layers may help in domain-specific ways
- the strongest general default is still the lightweight working-memory setup

## Product-Relevant Observation

For short follow-up chains, which is the main intended product use case:

- turns `1-4`:
  - `A=25.0%`
  - `B=79.7%`
  - `C=78.3%`
  - `D=78.1%`

Interpretation:

- for enterprise Text-to-SQL sessions with a few follow-up questions, `B wm2` is the best current default

## Main Contribution Of The Paper

The paper is not just claiming that memory helps.

The stronger contribution is:

- a controlled enterprise Text-to-SQL memory benchmark
- a comparison of stateless, working, episodic, and semantic memory layers
- evidence that memory benefit is strongly turn-depth dependent
- evidence that memory should be sized selectively because more memory is not always better
- practical guidance for enterprise Text-to-SQL system design

## What The Paper Should Claim

The paper should claim:

1. Memory materially improves multi-turn enterprise Text-to-SQL accuracy.
2. The benefit is concentrated in multi-turn follow-up tasks.
3. Working memory provides most of the gain.
4. Selective episodic retrieval can help, but large retrieval depth is not justified.
5. Small-memory configurations can outperform heavier memory setups.

## What The Paper Should Not Claim

The paper should not claim:

- one universal winning memory stack
- semantic memory is always best
- the findings generalize beyond Text-to-SQL without further experiments
- the optimal memory size is fully solved for every domain

## Why This Is Publishable

This is publishable because the result is not a generic slogan like "memory helps."

The interesting technical result is:

- memory benefit is large and stable for enterprise Text-to-SQL
- the effect is specifically tied to multi-turn reasoning
- lightweight working memory can match or beat heavier memory stacks
- larger memory can add noise instead of value

That is a practical and non-trivial result for enterprise AI system design.

## Remaining Work Before Full arXiv Draft

- convert the current markdown into formal paper structure
- add related work
- add methods details and benchmark construction details
- add figure selection
- refine the limitations section
- tighten the failure-analysis subsection

## Feedback Questions For Reviewer

1. Are the paper objective and scope clear?
2. Are the findings technically interesting enough for an arXiv paper?
3. Are the claims appropriately scoped for Text-to-SQL?
4. Is the "small memory beats heavier memory" result convincing and useful?
5. What claim feels strongest, and what claim feels overstated?
