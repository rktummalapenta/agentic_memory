# Experiment 0.5 Scaling Analysis

- Baseline stateless accuracy used for MSE: `16.16%`

| Run Label | Condition | Accuracy | Gain vs A | Avg Proxy Cost | Additional Cost | MSE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| conds-A_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_confirm60_A | A | 16.2% | +0.0 pts | 0.00 | 0.00 | — |
| conds-B_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-2_epk-3_semk-2_e05_confirm60_B_wm2 | B | 77.1% | +60.9 pts | 1.46 | 1.46 | 0.417051 |
| conds-B_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_confirm60_B_wm5 | B | 71.0% | +54.9 pts | 2.71 | 2.71 | 0.202484 |
| conds-C_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_confirm60_C_ep3 | C | 77.1% | +60.9 pts | 4.70 | 4.70 | 0.129656 |
| conds-C_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-1_semk-2_e05_confirm60_C_ep1 | C | 72.4% | +56.2 pts | 3.51 | 3.51 | 0.160269 |
| conds-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-1_e05_confirm60_D_sem1 | D | 72.7% | +56.6 pts | 5.70 | 5.70 | 0.099232 |
| conds-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_confirm60_D_sem2 | D | 72.7% | +56.6 pts | 6.70 | 6.70 | 0.084422 |
