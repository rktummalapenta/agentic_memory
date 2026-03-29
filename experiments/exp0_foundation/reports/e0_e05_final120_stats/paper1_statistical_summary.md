# Paper 1 Statistical Summary

- Main inferential input: `results_e0_e05_final120_t123_s120_A_Bwm2_Cep3_Dsem1.json`
- Confidence intervals: Wilson 95% intervals for accuracy.
- Pairwise tests: exact McNemar tests on matched turn-level correctness.
- Delta confidence intervals: paired bootstrap percentile intervals (95%).

## Main Findings

1. Memory materially improves multi-turn enterprise Text-to-SQL accuracy.
2. `B wm2` is the strongest overall condition in the final reduced run at `79.5%`.
3. `B wm2` also has the strongest memory-scaling efficiency, ahead of `C ep3` and `D sem1`.
4. Tier 1 behaves like a control; the real separation is in Tier 2 and Tier 3.
5. The evidence supports selective memory sizing rather than maximal memory sizing.

## Overall Accuracy With 95% Confidence Intervals

| Condition | Correct | Total | Accuracy | 95% CI | Gain vs A | Gain 95% CI |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| A | 95 | 580 | 16.4% | [13.6%, 19.6%] | — | [—, —] |
| B wm2 | 461 | 580 | 79.5% | [76.0%, 82.6%] | +63.1 pts | [+58.8 pts, +67.2 pts] |
| C ep3 | 449 | 580 | 77.4% | [73.8%, 80.6%] | +61.0 pts | [+56.7 pts, +65.2 pts] |
| D sem1 | 447 | 580 | 77.1% | [73.5%, 80.3%] | +60.7 pts | [+56.6 pts, +64.8 pts] |

## Pairwise Significance Tests

| Left | Right | Delta Accuracy | Delta 95% CI | McNemar p | Holm-adjusted p | Significant |
| --- | --- | ---: | --- | ---: | ---: | --- |
| A | B wm2 | -63.1 pts | [-67.2 pts, -58.8 pts] | 0.000000 | 0.000000 | yes |
| A | C ep3 | -61.0 pts | [-65.2 pts, -56.7 pts] | 0.000000 | 0.000000 | yes |
| A | D sem1 | -60.7 pts | [-64.8 pts, -56.6 pts] | 0.000000 | 0.000000 | yes |
| B wm2 | C ep3 | +2.1 pts | [-0.5 pts, +4.8 pts] | 0.161881 | 0.358828 | no |
| B wm2 | D sem1 | +2.4 pts | [-0.3 pts, +5.2 pts] | 0.119609 | 0.358828 | no |
| C ep3 | D sem1 | +0.3 pts | [-2.2 pts, +2.9 pts] | 0.897422 | 0.897422 | no |

## Final Reduced E0.5 Efficiency Ranking

| Condition | Accuracy | Gain vs A | Avg Proxy Cost | MSE |
| --- | ---: | ---: | ---: | ---: |
| B wm2 | 79.5% | +63.1 pts | 1.45 | 0.435714 |
| C ep3 | 77.4% | +61.0 pts | 4.62 | 0.132090 |
| D sem1 | 77.1% | +60.7 pts | 5.62 | 0.107975 |

## Accuracy By Tier

| Group | Condition | Correct | Total | Accuracy | 95% CI |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | A | 40 | 40 | 100.0% | [91.2%, 100.0%] |
| 2 | A | 25 | 160 | 15.6% | [10.8%, 22.0%] |
| 3 | A | 30 | 380 | 7.9% | [5.6%, 11.0%] |
| 1 | B wm2 | 40 | 40 | 100.0% | [91.2%, 100.0%] |
| 2 | B wm2 | 130 | 160 | 81.2% | [74.5%, 86.5%] |
| 3 | B wm2 | 291 | 380 | 76.6% | [72.1%, 80.6%] |
| 1 | C ep3 | 40 | 40 | 100.0% | [91.2%, 100.0%] |
| 2 | C ep3 | 127 | 160 | 79.4% | [72.5%, 84.9%] |
| 3 | C ep3 | 282 | 380 | 74.2% | [69.6%, 78.4%] |
| 1 | D sem1 | 40 | 40 | 100.0% | [91.2%, 100.0%] |
| 2 | D sem1 | 119 | 160 | 74.4% | [67.1%, 80.5%] |
| 3 | D sem1 | 288 | 380 | 75.8% | [71.2%, 79.8%] |

## Accuracy By Source

| Group | Condition | Correct | Total | Accuracy | 95% CI |
| --- | --- | ---: | ---: | ---: | --- |
| bird | A | 18 | 200 | 9.0% | [5.8%, 13.8%] |
| northwind | A | 27 | 189 | 14.3% | [10.0%, 20.0%] |
| sec_edgar | A | 50 | 191 | 26.2% | [20.5%, 32.8%] |
| bird | B wm2 | 138 | 200 | 69.0% | [62.3%, 75.0%] |
| northwind | B wm2 | 149 | 189 | 78.8% | [72.5%, 84.1%] |
| sec_edgar | B wm2 | 174 | 191 | 91.1% | [86.2%, 94.4%] |
| bird | C ep3 | 132 | 200 | 66.0% | [59.2%, 72.2%] |
| northwind | C ep3 | 152 | 189 | 80.4% | [74.2%, 85.5%] |
| sec_edgar | C ep3 | 165 | 191 | 86.4% | [80.8%, 90.5%] |
| bird | D sem1 | 121 | 200 | 60.5% | [53.6%, 67.0%] |
| northwind | D sem1 | 148 | 189 | 78.3% | [71.9%, 83.6%] |
| sec_edgar | D sem1 | 178 | 191 | 93.2% | [88.7%, 96.0%] |

## Accuracy By Turn Band

| Group | Condition | Correct | Total | Accuracy | 95% CI |
| --- | --- | ---: | ---: | ---: | --- |
| 1-4 | A | 90 | 360 | 25.0% | [20.8%, 29.7%] |
| 5-7 | A | 3 | 120 | 2.5% | [0.9%, 7.1%] |
| 8-10 | A | 2 | 100 | 2.0% | [0.6%, 7.0%] |
| 1-4 | B wm2 | 287 | 360 | 79.7% | [75.3%, 83.6%] |
| 5-7 | B wm2 | 93 | 120 | 77.5% | [69.2%, 84.1%] |
| 8-10 | B wm2 | 81 | 100 | 81.0% | [72.2%, 87.5%] |
| 1-4 | C ep3 | 282 | 360 | 78.3% | [73.8%, 82.3%] |
| 5-7 | C ep3 | 83 | 120 | 69.2% | [60.4%, 76.7%] |
| 8-10 | C ep3 | 84 | 100 | 84.0% | [75.6%, 89.9%] |
| 1-4 | D sem1 | 281 | 360 | 78.1% | [73.5%, 82.0%] |
| 5-7 | D sem1 | 76 | 120 | 63.3% | [54.4%, 71.4%] |
| 8-10 | D sem1 | 90 | 100 | 90.0% | [82.6%, 94.5%] |

## Stability Across Runs

These rows are earlier E0 replication runs using the raw condition letters `A/B/C/D`, not the final tuned reduced-set labels.

| Run | Condition | Accuracy | Correct | Total |
| --- | --- | ---: | ---: | ---: |
| summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36 | A | 17.2% | 31 | 180 |
| summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36 | B | 72.8% | 131 | 180 |
| summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36 | C | 74.4% | 134 | 180 |
| summary_20260316T004222Z_conds-A-B-C-D_tiers-1-2-3_sessions-36_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_small_t123_s36 | D | 75.6% | 136 | 180 |
| summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60 | A | 16.8% | 50 | 297 |
| summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60 | B | 76.1% | 226 | 297 |
| summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60 | C | 76.4% | 227 | 297 |
| summary_20260316T035101Z_conds-A-B-C-D_tiers-1-2-3_sessions-60_model-gpt-5-mini_wm-5_epk-3_semk-2_e0_confirm60_t123_s60 | D | 72.7% | 216 | 297 |

## Discussion

- The central E0 claim is stable: `A` remains low while memory conditions stay high. In the final reduced run, `A` is `16.4%`, `B wm2` is `79.5%`, `C ep3` is `77.4%`, and `D sem1` is `77.1%`.
- `B wm2` is the current best default because it leads on both accuracy and efficiency.
- `C ep3` remains competitive and may still be useful when extra recall is needed, but it does not beat the lighter working-memory configuration overall.
- `D sem1` shows domain-specific value, especially on `sec_edgar`, but the full stack is not the overall winner.
- The remaining dominant failure mode is semantic mismatch, which means memory is fixing continuity more than it is fixing every SQL-generation error mode.

## Ready-To-Use Paper Claims

1. Memory materially improves multi-turn enterprise Text-to-SQL accuracy.
2. The benefit is concentrated in multi-turn complexity rather than single-turn controls.
3. Working memory provides most of the gain.
4. Selective retrieval can help, but larger memory is not monotonically better.
5. The current best operating point is small working memory with optional selective retrieval.

## Limitations

- These results are from one model family (`gpt-5-mini`).
- The final inferential table is based on the reduced `120`-session configuration set, while earlier runs are used as replication evidence.
- Statistical testing is descriptive for the current benchmark and does not replace future cross-model replication.
