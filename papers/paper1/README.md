# Paper 1 Workspace

Working title:

`Memory Benefit and Memory Scaling Efficiency for Enterprise Text-to-SQL Agents`

This folder is the standalone workspace for Paper 1. It is meant to hold:

- the manuscript draft
- the exact result artifacts used by the paper
- the statistical summaries
- provenance and reproducibility notes
- a hashed manifest of the evidence bundle

## Scope

Paper 1 is specifically about **multi-turn enterprise Text-to-SQL**. It is not framed as a general memory-for-agents paper.

The paper answers two questions:

1. Does memory materially improve multi-turn enterprise Text-to-SQL accuracy?
2. If memory helps, how much memory is enough before returns flatten or decline?

## Current Status

The experimental evidence is now strong enough for a first arXiv draft.

What is already done:

- exploratory, confirmatory, and final reduced runs
- final reduced `120`-session inferential bundle
- confidence intervals
- paired significance tests
- efficiency analysis (`MSE`)
- findings summaries and shareable review brief

What is still needed before submission:

- convert the draft into full paper prose and citation style
- add related work
- tighten methods wording
- select figures for the final paper
- add a final limitations section

## Folder Layout

- [manuscript.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/manuscript.md): working paper draft
- [REVIEW_PACKET.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/REVIEW_PACKET.md): short review-facing summary
- [PROVENANCE.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/PROVENANCE.md): exact evidence trail and reproducibility notes
- [artifact_manifest.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifact_manifest.csv): hashed manifest of core artifacts
- [artifact_manifest.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifact_manifest.md): readable manifest
- [artifacts](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts): staged copies of the experiment artifacts used by the paper

## Main Paper Claim

The strongest current claim is:

Memory materially improves multi-turn enterprise Text-to-SQL accuracy, but more memory is not monotonically better. A small working-memory configuration is the best current operating point, while deeper memory layers help in domain-dependent ways.

## Key Final Numbers

From the final reduced `120`-session run:

- `A`: `16.4%`
- `B wm2`: `79.5%`
- `C ep3`: `77.4%`
- `D sem1`: `77.1%`

From the statistical summary:

- `A` vs each memory condition: significant
- `B wm2` vs `C ep3`: not significant
- `B wm2` vs `D sem1`: not significant
- `C ep3` vs `D sem1`: not significant

This means the paper should strongly claim **memory benefit**, but should avoid overclaiming a universal winning stack.
