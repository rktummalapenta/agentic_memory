"""Combine per-condition Experiment 0 result files into one bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.mbs_calculator import summarize_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-file",
        action="append",
        dest="results_files",
        required=True,
        help="Path to a results_*.json file. Pass once per condition run.",
    )
    parser.add_argument("--output-results-file", required=True)
    parser.add_argument("--output-summary-file", required=True)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    combined: dict[str, list[dict[str, Any]]] = {}

    for results_file in args.results_files:
        path = ROOT / results_file if not Path(results_file).is_absolute() else Path(results_file)
        payload = load_json(path)
        if len(payload) != 1:
            raise ValueError(f"Expected exactly one condition in {path}, found {list(payload)}")
        condition, rows = next(iter(payload.items()))
        combined[condition] = rows

    output_results = (
        ROOT / args.output_results_file
        if not Path(args.output_results_file).is_absolute()
        else Path(args.output_results_file)
    )
    output_summary = (
        ROOT / args.output_summary_file
        if not Path(args.output_summary_file).is_absolute()
        else Path(args.output_summary_file)
    )
    output_results.parent.mkdir(parents=True, exist_ok=True)
    output_summary.parent.mkdir(parents=True, exist_ok=True)

    output_results.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    output_summary.write_text(
        json.dumps(summarize_results(combined), indent=2),
        encoding="utf-8",
    )
    print(f"Combined results: {output_results}")
    print(f"Combined summary: {output_summary}")


if __name__ == "__main__":
    main()
