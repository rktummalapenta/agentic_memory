"""Analyze Experiment 0.5 scaling runs and compute first-pass MSE tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.mse_calculator import summarize_scaling_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        default="experiments/exp0_foundation/results",
        help="Directory containing results_*, summary_*, and runmeta_* files.",
    )
    parser.add_argument(
        "--baseline-results-file",
        default=None,
        help="Optional results_*.json file for a stateless A baseline on the same slice.",
    )
    parser.add_argument(
        "--run-tag-filter",
        default="e05_",
        help="Only include runmeta files whose run_tag-containing filename matches this substring.",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Optional markdown output path.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_runmeta_files(results_dir: Path, run_tag_filter: str) -> list[Path]:
    return sorted(
        path for path in results_dir.glob("runmeta_*.json") if run_tag_filter in path.name
    )


def baseline_accuracy_from_results(path: Path) -> float:
    payload = load_json(path)
    rows = payload.get("A", [])
    if not rows:
        raise ValueError(f"No A rows found in baseline results file: {path}")
    correct = sum(1 for row in rows if row["is_correct"])
    return correct / len(rows)


def build_report(
    rows: list[dict[str, Any]],
    baseline_accuracy: float,
) -> str:
    lines = [
        "# Experiment 0.5 Scaling Analysis",
        "",
        f"- Baseline stateless accuracy used for MSE: `{baseline_accuracy * 100:.2f}%`",
        "",
        "| Run Label | Condition | Accuracy | Gain vs A | Avg Proxy Cost | Additional Cost | MSE |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        mse = "—" if row["mse"] is None else f"{row['mse']:.6f}"
        lines.append(
            f"| {row['run_label']} | {row['condition']} | {row['accuracy'] * 100:.1f}% | "
            f"{row['accuracy_gain_vs_baseline'] * 100:+.1f} pts | "
            f"{row['average_proxy_memory_cost']:.2f} | "
            f"{row['additional_memory_cost_vs_baseline']:.2f} | {mse} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    results_dir = ROOT / args.results_dir
    if args.baseline_results_file:
        baseline_accuracy = baseline_accuracy_from_results(ROOT / args.baseline_results_file)
    else:
        baseline_accuracy = 0.0

    records: list[dict[str, Any]] = []

    for runmeta_path in discover_runmeta_files(results_dir, args.run_tag_filter):
        results_path = runmeta_path.with_name(runmeta_path.name.replace("runmeta_", "results_"))
        if not results_path.exists():
            continue
        runmeta = load_json(runmeta_path)
        results_payload = load_json(results_path)
        if len(runmeta["conditions"]) != 1:
            continue
        condition = runmeta["conditions"][0]
        condition_rows = results_payload.get(condition, [])
        if not condition_rows:
            continue
        summary = summarize_scaling_run(
            condition_rows,
            baseline_accuracy=baseline_accuracy,
            baseline_memory_cost=0.0,
        )
        records.append(
            {
                "run_label": runmeta["run_label"],
                "condition": condition,
                **summary,
            }
        )

    records.sort(key=lambda item: (item["condition"], -item["accuracy"], item["run_label"]))
    report = build_report(records, baseline_accuracy)

    if args.output_file:
        output_path = ROOT / args.output_file
        output_path.write_text(report, encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
