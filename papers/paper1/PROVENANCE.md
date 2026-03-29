# Paper 1 Provenance And Reproducibility

## Goal

This file documents where each major paper claim comes from and how to reproduce the statistical summary.

## Main Evidence Bundle

The final inferential input is:

- [results_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/results/results_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json)
- [summary_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/results/summary_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json)

Supporting earlier runs:

- [summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36.json](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/results/summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36.json)
- [summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60.json](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/results/summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60.json)

Per-condition final run files are also staged in [artifacts/results](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/results).

## Exact Commands Used

Final reduced run script:

- [run_e0_e05_final_120.sh](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/scripts/run_e0_e05_final_120.sh)

Statistical analysis script:

- [analyze_paper1_stats.py](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/scripts/analyze_paper1_stats.py)

To regenerate the paper statistics package from the repo root:

```bash
python3 scripts/analyze_paper1_stats.py \
  --results-file experiments/exp0_foundation/results/results_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json \
  --output-dir experiments/exp0_foundation/reports/e0_e05_final120_stats \
  --comparison-summary-file experiments/exp0_foundation/results/summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36.json \
  --comparison-summary-file experiments/exp0_foundation/results/summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60.json \
  --display-label A=A \
  --display-label "B=B wm2" \
  --display-label "C=C ep3" \
  --display-label "D=D sem1"
```

## Statistical Method

The current statistical package uses:

- Wilson `95%` confidence intervals for accuracy
- exact McNemar tests on matched turn-level correctness
- Holm correction for multiple pairwise comparisons
- paired bootstrap percentile intervals for accuracy deltas

No LLM calls are used for the statistical analysis.

## Claim-To-Evidence Mapping

### Claim: memory materially improves multi-turn enterprise Text-to-SQL

Primary evidence:

- [paper1_statistical_summary.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/paper1_statistical_summary.md)
- [overall_accuracy.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/overall_accuracy.csv)

### Claim: the main benefit is in multi-turn tasks, not single-turn controls

Primary evidence:

- [accuracy_by_tier.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/accuracy_by_tier.csv)
- [final120_report.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/final120_report.md)

### Claim: small working memory is the best current operating point

Primary evidence:

- [mse_ranking.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/mse_ranking.csv)
- [pairwise_significance.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/pairwise_significance.csv)
- [e05_final120_analysis.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/e05_final120_analysis.md)

### Claim: more memory is not monotonically better

Primary evidence:

- [paper1_shareable_brief.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/paper1_shareable_brief.md)
- [e0_e05_findings_20260316.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/e0_e05_findings_20260316.md)
- [stability_across_runs.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/stability_across_runs.csv)

### Claim: deeper memory helps in domain-dependent ways

Primary evidence:

- [accuracy_by_source.csv](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/stats/accuracy_by_source.csv)
- [final120_report.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifacts/reports/final120_report.md)

## Authenticity Notes

If someone questions the paper evidence:

- the raw final combined result bundle is staged in this folder
- the per-condition final run files are staged in this folder
- the exact analysis script is staged in this folder
- the hashed manifest is included in this folder

See [artifact_manifest.md](/Users/ravikumartummalapenta/Documents/github/rktummalapenta/agentic_memory/papers/paper1/artifact_manifest.md) for the hash-verified artifact list.
