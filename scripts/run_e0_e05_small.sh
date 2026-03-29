#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$ROOT_DIR/experiments/exp0_foundation/results"
REPORTS_DIR="$ROOT_DIR/experiments/exp0_foundation/reports"

PYTHON_BIN="${PYTHON_BIN:-python3}"
SESSIONS="${SESSIONS:-36}"
TIERS="${TIERS:-1 2 3}"
RUN_PREFIX="${RUN_PREFIX:-small}"
RUN_E0="${RUN_E0:-1}"
RUN_E05="${RUN_E05:-1}"
RESET_MEMORY="${RESET_MEMORY:-1}"

timestamp() {
  date +"%Y-%m-%d %H:%M:%S %Z"
}

log() {
  printf '%s %s\n' "$(timestamp)" "$*"
}

find_latest_file() {
  local pattern="$1"
  "$PYTHON_BIN" - "$RESULTS_DIR" "$pattern" <<'PY'
from pathlib import Path
import sys

results_dir = Path(sys.argv[1])
pattern = sys.argv[2]
matches = sorted(results_dir.glob(pattern), key=lambda path: path.stat().st_mtime)
print(matches[-1] if matches else "")
PY
}

run_experiment() {
  local tag="$1"
  shift
  log "starting run tag=$tag"
  if [[ "$RESET_MEMORY" == "1" ]]; then
    "$PYTHON_BIN" "$ROOT_DIR/scripts/reset_runtime_memory.py" --experiment e0 >/dev/null
  fi
  "$PYTHON_BIN" "$ROOT_DIR/experiments/exp0_foundation/run_experiment.py" "$@" --run-tag "$tag"
  log "finished run tag=$tag"
}

generate_e0_report() {
  local tag="$1"
  local results_file summary_file report_dir
  results_file="$(find_latest_file "results_*${tag}.json")"
  summary_file="$(find_latest_file "summary_*${tag}.json")"
  if [[ -z "$results_file" || -z "$summary_file" ]]; then
    log "skipping E0 report generation for $tag because results were not found"
    return
  fi
  report_dir="$REPORTS_DIR/${tag}"
  mkdir -p "$report_dir"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/generate_exp0_report.py" \
    --results-file "$results_file" \
    --summary-file "$summary_file" \
    --output-dir "$report_dir" \
    --title "Experiment 0 Small Run Report"
  log "wrote E0 report to $report_dir"
}

run_e05_analysis() {
  local baseline_tag="$1"
  local output_file baseline_results
  baseline_results="$(find_latest_file "results_*${baseline_tag}.json")"
  if [[ -z "$baseline_results" ]]; then
    log "skipping E0.5 analysis because baseline results were not found"
    return
  fi
  output_file="experiments/exp0_foundation/reports/e05_${RUN_PREFIX}_analysis.md"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/analyze_e05_scaling.py" \
    --baseline-results-file "${baseline_results#$ROOT_DIR/}" \
    --run-tag-filter "e05_${RUN_PREFIX}_" \
    --output-file "$output_file"
  log "wrote E0.5 analysis to $ROOT_DIR/$output_file"
}

log "root=$ROOT_DIR"
log "sessions=$SESSIONS tiers=$TIERS run_prefix=$RUN_PREFIX"

if [[ "$RUN_E0" == "1" ]]; then
  run_experiment "e0_${RUN_PREFIX}_t123_s${SESSIONS}" \
    --conditions A B C D \
    --tiers $TIERS \
    --sessions "$SESSIONS"
  generate_e0_report "e0_${RUN_PREFIX}_t123_s${SESSIONS}"
fi

if [[ "$RUN_E05" == "1" ]]; then
  run_experiment "e05_${RUN_PREFIX}_A" \
    --conditions A \
    --tiers $TIERS \
    --sessions "$SESSIONS"

  run_experiment "e05_${RUN_PREFIX}_B_wm2" \
    --conditions B \
    --tiers $TIERS \
    --sessions "$SESSIONS" \
    --working-memory-window 2

  run_experiment "e05_${RUN_PREFIX}_B_wm10" \
    --conditions B \
    --tiers $TIERS \
    --sessions "$SESSIONS" \
    --working-memory-window 10

  run_experiment "e05_${RUN_PREFIX}_C_ep1" \
    --conditions C \
    --tiers $TIERS \
    --sessions "$SESSIONS" \
    --working-memory-window 5 \
    --episodic-top-k 1

  run_experiment "e05_${RUN_PREFIX}_C_ep10" \
    --conditions C \
    --tiers $TIERS \
    --sessions "$SESSIONS" \
    --working-memory-window 5 \
    --episodic-top-k 10

  run_experiment "e05_${RUN_PREFIX}_D_sem1" \
    --conditions D \
    --tiers $TIERS \
    --sessions "$SESSIONS" \
    --working-memory-window 5 \
    --episodic-top-k 5 \
    --semantic-top-k 1

  run_experiment "e05_${RUN_PREFIX}_D_sem4" \
    --conditions D \
    --tiers $TIERS \
    --sessions "$SESSIONS" \
    --working-memory-window 5 \
    --episodic-top-k 5 \
    --semantic-top-k 4

  run_e05_analysis "e05_${RUN_PREFIX}_A"
fi

log "all requested runs completed"
log "results directory: $RESULTS_DIR"
log "reports directory: $REPORTS_DIR"
