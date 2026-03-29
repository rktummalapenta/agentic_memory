# Paper 1 ArXiv Draft

This folder contains the first paper-format draft for Paper 1.

## Files

- [main.tex](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/arxiv/main.tex): current LaTeX manuscript draft
- [references.bib](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/arxiv/references.bib): bibliography scaffold
- [figures](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/arxiv/figures): staged report figures

## Status

This draft is structurally ready for paper writing, but it still needs:

- real author names and affiliations
- related work citations
- final wording cleanup
- figure caption refinement
- venue-specific formatting decisions

## Build

From the repo root:

```bash
cd papers/paper1/arxiv
pdflatex main.tex
```

If BibTeX is available and references are added later:

```bash
cd papers/paper1/arxiv
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Source Of Numbers

The numerical claims in `main.tex` are based on the staged evidence in:

- [../artifacts/stats/paper1_statistical_summary.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/paper1_statistical_summary.md)
- [../artifacts/reports/final120_report.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/final120_report.md)
- [../PROVENANCE.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/PROVENANCE.md)
