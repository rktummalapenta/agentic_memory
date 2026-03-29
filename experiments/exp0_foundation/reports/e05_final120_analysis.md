# Experiment 0.5 Scaling Analysis

- Baseline stateless accuracy used for MSE: `16.38%`

| Run Label | Condition | Accuracy | Gain vs A | Avg Proxy Cost | Additional Cost | MSE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| conds-A_tiers-1-2-3_sessions-120_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_final120_A | A | 16.4% | +0.0 pts | 0.00 | 0.00 | — |
| conds-B_tiers-1-2-3_sessions-120_model-gpt-5-mini_wm-2_epk-3_semk-2_e05_final120_B_wm2 | B | 79.5% | +63.1 pts | 1.45 | 1.45 | 0.435714 |
| conds-C_tiers-1-2-3_sessions-120_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_final120_C_ep3 | C | 77.4% | +61.0 pts | 4.62 | 4.62 | 0.132090 |
| conds-D_tiers-1-2-3_sessions-120_model-gpt-5-mini_wm-5_epk-3_semk-1_e05_final120_D_sem1 | D | 77.1% | +60.7 pts | 5.62 | 5.62 | 0.107975 |
