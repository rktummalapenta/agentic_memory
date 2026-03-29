# Paper 1 Draft: E0 + E0.5

Working title:

`Memory Benefit and Memory Scaling Efficiency for Enterprise Text-to-SQL Agents`

Alternative title:

`When Memory Helps and How Much Memory Is Enough for Enterprise Text-to-SQL Agents`

## Status

This is a working draft that captures the current paper narrative and concrete findings from:

- the exploratory `36`-session `tiers 1 2 3` runs
- the confirmatory `60`-session `tiers 1 2 3` runs
- the final reduced `120`-session confirmatory run on `A`, `B wm2`, `C ep3`, and `D sem1`

It is not submission-ready yet because statistical testing and confidence intervals are still missing. It is the current paper workspace so we can continue from the final reduced run without rebuilding the argument from scratch.

## Abstract Draft

Memory is widely treated as a necessary component of production AI agents, but the actual benefit and required memory footprint are often unclear. We evaluate memory-augmented agents on a multi-turn enterprise Text-to-SQL benchmark spanning Northwind, SEC EDGAR, and BIRD under four conditions: stateless, working memory only, working plus episodic memory, and a full stack including semantic hints. We then study memory scaling by varying working-memory window size and retrieval depth. Across exploratory, confirmatory, and final reduced runs, memory increases accuracy from roughly `16%` to `17%` in the stateless condition to roughly `77%` to `80%` in memory-enabled conditions on multi-turn tasks, while providing little additional value on single-turn controls. We further find that more memory is not monotonically better: a small working-memory window (`wm2`) outperforms heavier memory configurations and achieves the strongest memory-scaling efficiency. These findings suggest that enterprise agent memory should be sized selectively rather than maximized by default.

## Current Concrete Findings

### Finding 1: Memory materially improves multi-turn enterprise Text-to-SQL accuracy

From the final reduced `120`-session run:

- `A`: `16.4%`
- `B wm2`: `79.5%`
- `C ep3`: `77.4%`
- `D sem1`: `77.1%`

Interpretation:

- memory is the difference between failure-level performance and usable performance on multi-turn enterprise SQL tasks
- the effect size is large and stable across runs

### Finding 2: Tier 1 is not the main story

From the final reduced `120`-session `tiers 1 2 3` run:

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

- memory is not the differentiator on simple single-turn tasks
- memory becomes decisive once tasks become conversational and stateful

### Finding 3: Working memory provides most of the gain

Across the final reduced run:

- `B wm2` is the best overall condition
- `B` beats `C` on `37` turns and loses on `25`
- `B` beats `D` on `42` turns and loses on `28`

Interpretation:

- recent-turn context retention is already doing most of the useful lifting
- deeper layers can help, but their value is conditional rather than universal

### Finding 4: More memory is not always better

From the final reduced `120`-session `E0.5` set:

- `B wm2`: `79.5%`
- `C ep3`: `77.4%`
- `D sem1`: `77.1%`

And from earlier reduced sweeps:

- `B wm10`: `73.3%`
- `B wm5`: `71.0%`
- `C ep10`: `72.8%`
- `D sem4`: `74.4%`

Interpretation:

- small working memory beats a larger working-memory window
- selective episodic retrieval helps, but retrieval should remain small
- additional semantic hints are not improving results

### Finding 5: The efficient operating point is selective memory, not maximal memory

From the final reduced `120`-session `E0.5` MSE table:

- `B wm2`: `0.435714`
- `C ep3`: `0.132090`
- `D sem1`: `0.107975`

Interpretation:

- the best current practical default is small working memory
- episodic recall should be added selectively
- semantic retrieval should stay narrow

## Current Paper Claims

The draft currently supports these claims:

1. Memory materially improves multi-turn enterprise Text-to-SQL accuracy.
2. The benefit is concentrated in multi-turn complexity rather than single-turn controls.
3. Working memory provides most of the gain.
4. Episodic retrieval can help, but should remain selective.
5. More memory is not monotonically better.
6. A small-memory operating point can maximize both accuracy and efficiency.

The draft does not yet support these claims:

- one universal winning memory stack
- semantic memory as a dominant general-purpose layer
- a globally optimal memory size across all domains and turn depths

## Enterprise Relevance

For enterprise teams, the current practical message is:

- use a stateless baseline when benchmarking agents
- do not assume larger memory windows are better
- start with lightweight working memory for short follow-up chains
- add selective episodic retrieval only when longer context carryover is needed
- do not pay semantic-memory complexity costs unless a concrete domain benefit is shown

## Suggested Figures

Current figures to carry into the paper:

1. E0 overall accuracy by condition
2. E0 tier-level accuracy
3. E0 dataset-level accuracy
4. E0.5 working-memory scaling comparison
5. E0.5 episodic scaling comparison
6. E0.5 semantic scaling comparison
7. MSE ranking table or chart

## Methods Section To Fill In

Still needs:

- final benchmark slice selection policy
- exact session counts per tier and source
- exact model and fallback model
- exact correctness evaluation rule
- confidence intervals and significance testing
- final failure-analysis subsection

## Remaining Work Before Submission

1. Add statistical testing and confidence intervals.
2. Expand failure analysis into a paper-ready section.
3. Freeze the final run set and tables.
4. Convert this draft into a paper format in LaTeX or journal template form.
