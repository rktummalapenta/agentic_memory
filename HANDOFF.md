# HANDOFF.md

This file is the restart-safe status record for the repo. If chat history is lost, start here.

## Current Status
**Last reconciled:** 2026-03-16

Experiment 0 and 0.5 now have exploratory and confirmatory runs. The repo already contains:

- a 30-session pilot run
- a 60-session cross-dataset pilot run
- a 36-session `tiers 1 2 3` exploratory run
- a 60-session `tiers 1 2 3` confirmatory run
- a reduced 36-session E0.5 scaling sweep
- a reduced 60-session E0.5 confirmatory sweep
- generated summary JSON files
- generated markdown reports and charts

Current conclusion:

- memory clearly helps on multi-turn enterprise SQL tasks
- stateless performance collapses after early turns
- Tier 1 is easy; the real separation happens in Tier 2 and Tier 3
- working memory provides most of the gain
- more memory is not monotonically better
- dataset winners vary, so the current evidence supports "memory matters" more strongly than "one memory stack always wins"

## Authoritative Artifacts

Read these in order:

1. `PHASES.md`
2. `E0_PUBLICATION_PLAN.md`
3. `E0_E05_PAPER_PLAN.md`
4. `experiments/exp0_foundation/reports/e0_e05_findings_20260316.md`
5. `experiments/exp0_foundation/reports/paper1_draft_e0_e05.md`
6. `experiments/exp0_foundation/reports/e0_confirm60_t123_s60/report.md`
7. `experiments/exp0_foundation/reports/e05_confirm60_analysis.md`
8. `experiment_results/exp0`

These files are enough to reconstruct the current Experiment 0 state, the combined `E0 + E0.5` paper direction, and the publication sequencing without prior chat context.

## Latest Experiment 0 and 0.5 Result

Baseline artifact:

- E0 report: `experiments/exp0_foundation/reports/e0_confirm60_t123_s60/report.md`
- E0.5 analysis: `experiments/exp0_foundation/reports/e05_confirm60_analysis.md`
- combined findings: `experiments/exp0_foundation/reports/e0_e05_findings_20260316.md`
- paper draft workspace: `experiments/exp0_foundation/reports/paper1_draft_e0_e05.md`

Headline numbers:

- E0 confirmatory:
  - `A`: `50/297` = `16.8%`
  - `B`: `226/297` = `76.1%`
  - `C`: `227/297` = `76.4%`
  - `D`: `216/297` = `72.7%`
- E0.5 confirmatory:
  - `B wm2`: `77.1%`
  - `B wm5`: `71.0%`
  - `C ep1`: `72.4%`
  - `C ep3`: `77.1%`
  - `D sem1`: `72.7%`
  - `D sem2`: `72.7%`

Publication interpretation:

- Forbes: memory matters when work becomes conversational and stateful
- Paper 1: memory materially improves multi-turn Text-to-SQL, but the efficient operating point is small working memory plus selective retrieval

## Next Steps

These are the next actions that were pending when work stopped:

1. Use the `60`-session confirmatory run as the current E0 baseline.
2. Use the `60`-session reduced sweep as the current E0.5 baseline.
3. Keep updating `paper1_draft_e0_e05.md` as findings stabilize.
4. Add statistical testing and confidence intervals.
5. Decide whether one final reduced confirmatory pass is needed on `A`, `B wm2`, `C ep3`, `D sem1`.
6. Expand the failure-analysis section for the paper.
7. Freeze Paper 1 narrative before moving hard into E1.

## Restart Recovery Workflow

When the laptop restarts or chat history is gone:

1. Run `git status --short` to see what changed since the last session.
2. Read `HANDOFF.md`.
3. Read `PHASES.md`.
4. Open the latest E0 report under `experiments/exp0_foundation/reports/`.
5. Continue from the `Next Steps` section above.

## Operating Rule Going Forward

After every substantial run or decision:

- update `HANDOFF.md`
- update `PHASES.md` if the project state changed
- keep one canonical report path for the current baseline artifact

That keeps progress recoverable from the repo even if chat history disappears.
