#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$ROOT_DIR/experiments/exp0_foundation/results"
REPORTS_DIR="$ROOT_DIR/experiments/exp0_foundation/reports"

PYTHON_BIN="${PYTHON_BIN:-python3}"
SESSIONS="${SESSIONS:-120}"
TIERS="${TIERS:-1 2 3}"
RUN_PREFIX="${RUN_PREFIX:-final120}"
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

build_combined_bundle() {
  local bundle_name="$1"
  local output_results="$RESULTS_DIR/results_${bundle_name}.json"
  local output_summary="$RESULTS_DIR/summary_${bundle_name}.json"
  local a_file b_file c_file d_file

  a_file="$(find_latest_file "results_*e05_${RUN_PREFIX}_A.json")"
  b_file="$(find_latest_file "results_*e05_${RUN_PREFIX}_B_wm2.json")"
  c_file="$(find_latest_file "results_*e05_${RUN_PREFIX}_C_ep3.json")"
  d_file="$(find_latest_file "results_*e05_${RUN_PREFIX}_D_sem1.json")"

  if [[ -z "$a_file" || -z "$b_file" || -z "$c_file" || -z "$d_file" ]]; then
    log "unable to build combined bundle because one or more result files are missing"
    return 1
  fi

  "$PYTHON_BIN" "$ROOT_DIR/scripts/combine_exp_results.py" \
    --results-file "${a_file#$ROOT_DIR/}" \
    --results-file "${b_file#$ROOT_DIR/}" \
    --results-file "${c_file#$ROOT_DIR/}" \
    --results-file "${d_file#$ROOT_DIR/}" \
    --output-results-file "${output_results#$ROOT_DIR/}" \
    --output-summary-file "${output_summary#$ROOT_DIR/}"
}

generate_report_and_errors() {
  local bundle_name="$1"
  local report_dir="$REPORTS_DIR/e0_e05_${RUN_PREFIX}"
  mkdir -p "$report_dir"

  "$PYTHON_BIN" "$ROOT_DIR/scripts/generate_exp0_report.py" \
    --results-file "$RESULTS_DIR/results_${bundle_name}.json" \
    --summary-file "$RESULTS_DIR/summary_${bundle_name}.json" \
    --output-dir "$report_dir" \
    --title "Paper 1 Final Reduced 120-Session Report"

  {
    echo "# B vs C"
    "$PYTHON_BIN" "$ROOT_DIR/scripts/analyze_exp0_errors.py" \
      --results-file "$RESULTS_DIR/results_${bundle_name}.json" \
      --compare-conditions B C \
      --sample-limit 12
    echo
    echo "# C vs D"
    "$PYTHON_BIN" "$ROOT_DIR/scripts/analyze_exp0_errors.py" \
      --results-file "$RESULTS_DIR/results_${bundle_name}.json" \
      --compare-conditions C D \
      --sample-limit 12
  } >"$report_dir/error_analysis.txt"

  log "wrote combined reduced-set report to $report_dir"
}

run_e05_analysis() {
  local baseline_results
  baseline_results="$(find_latest_file "results_*e05_${RUN_PREFIX}_A.json")"
  if [[ -z "$baseline_results" ]]; then
    log "skipping E0.5 analysis because baseline results were not found"
    return
  fi

  "$PYTHON_BIN" "$ROOT_DIR/scripts/analyze_e05_scaling.py" \
    --baseline-results-file "${baseline_results#$ROOT_DIR/}" \
    --run-tag-filter "e05_${RUN_PREFIX}_" \
    --output-file "experiments/exp0_foundation/reports/e05_${RUN_PREFIX}_analysis.md"

  log "wrote E0.5 analysis to $REPORTS_DIR/e05_${RUN_PREFIX}_analysis.md"
}

log "root=$ROOT_DIR"
log "sessions=$SESSIONS tiers=$TIERS run_prefix=$RUN_PREFIX"

run_experiment "e05_${RUN_PREFIX}_A" \
  --conditions A \
  --tiers $TIERS \
  --sessions "$SESSIONS"

run_experiment "e05_${RUN_PREFIX}_B_wm2" \
  --conditions B \
  --tiers $TIERS \
  --sessions "$SESSIONS" \
  --working-memory-window 2

run_experiment "e05_${RUN_PREFIX}_C_ep3" \
  --conditions C \
  --tiers $TIERS \
  --sessions "$SESSIONS" \
  --working-memory-window 5 \
  --episodic-top-k 3

run_experiment "e05_${RUN_PREFIX}_D_sem1" \
  --conditions D \
  --tiers $TIERS \
  --sessions "$SESSIONS" \
  --working-memory-window 5 \
  --episodic-top-k 3 \
  --semantic-top-k 1

BUNDLE_NAME="e0_e05_${RUN_PREFIX}_t123_s${SESSIONS}_A_Bwm2_Cep3_Dsem1"
build_combined_bundle "$BUNDLE_NAME"
generate_report_and_errors "$BUNDLE_NAME"
run_e05_analysis

log "all final reduced runs completed"
log "results directory: $RESULTS_DIR"
log "reports directory: $REPORTS_DIR"
