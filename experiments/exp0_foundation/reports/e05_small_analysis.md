# Experiment 0.5 Scaling Analysis

- Baseline stateless accuracy used for MSE: `15.00%`

| Run Label | Condition | Accuracy | Gain vs A | Avg Proxy Cost | Additional Cost | MSE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| conds-A_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e05_small_A | A | 15.0% | +0.0 pts | 0.00 | 0.00 | — |
| conds-B_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-2_epk-3_semk-2_e05_small_B_wm2 | B | 76.7% | +61.7 pts | 1.47 | 1.47 | 0.420455 |
| conds-B_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-10_epk-3_semk-2_e05_small_B_wm10 | B | 73.3% | +58.3 pts | 3.40 | 3.40 | 0.171569 |
| conds-C_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-1_semk-2_e05_small_C_ep1 | C | 78.3% | +63.3 pts | 3.53 | 3.53 | 0.179245 |
| conds-C_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-10_semk-2_e05_small_C_ep10 | C | 72.8% | +57.8 pts | 6.13 | 6.13 | 0.094203 |
| conds-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-5_semk-1_e05_small_D_sem1 | D | 76.1% | +61.1 pts | 6.47 | 6.47 | 0.094502 |
| conds-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-5_semk-4_e05_small_D_sem4 | D | 74.4% | +59.4 pts | 7.47 | 7.47 | 0.079613 |
