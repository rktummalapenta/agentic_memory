# Paper 1 Review Packet

Use this file when sending the work for outside opinion before the full paper is finalized.

## What This Paper Is About

This paper studies **memory benefit and memory sizing for enterprise multi-turn Text-to-SQL**.

It asks:

1. Does memory materially improve multi-turn Text-to-SQL?
2. If yes, how much memory is enough?

## Final Experimental Setup

Main inferential run:

- `A`: stateless
- `B wm2`: working memory with window size `2`
- `C ep3`: working memory plus episodic retrieval with top-k `3`
- `D sem1`: working memory plus episodic retrieval plus semantic top-k `1`

Benchmark slice:

- `120` sessions
- `tiers 1 2 3`
- sources: `Northwind`, `SEC EDGAR`, `BIRD`
- model: `gpt-5-mini`

## Main Findings

- `A=16.4%`
- `B wm2=79.5%`
- `C ep3=77.4%`
- `D sem1=77.1%`

Tier pattern:

- Tier 1 is effectively solved by all conditions
- Tier 2 and Tier 3 are where memory matters

Scaling pattern:

- smaller working memory beats larger working memory
- selective episodic retrieval helps more than high retrieval depth
- narrow semantic retrieval is preferable to larger semantic retrieval

## Statistical Conclusion

The paper can strongly claim:

- all memory-enabled conditions significantly outperform the stateless baseline

The paper should not claim:

- one memory condition is statistically proven as the universal winner among `B/C/D`

## Why This Is Interesting

The technically interesting result is not only that memory helps, but that:

- the gain is strongly tied to multi-turn reasoning
- small working memory performs extremely well
- more memory can reduce accuracy rather than improve it

## Files To Review

- [manuscript.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/manuscript.md)
- [paper1_shareable_brief.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/paper1_shareable_brief.md)
- [paper1_statistical_summary.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/paper1_statistical_summary.md)
- [final120_report.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/final120_report.md)

## Questions To Answer

1. Is the scope clear and appropriately limited to Text-to-SQL?
2. Is the memory-scaling result interesting enough for a technical paper?
3. Do any claims feel overstated?
4. What should be emphasized more strongly in the final paper?
