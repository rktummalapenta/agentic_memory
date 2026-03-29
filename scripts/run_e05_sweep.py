"""Run a first-pass Experiment 0.5 scaling sweep."""

from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments" / "exp0_foundation" / "run_experiment.py"


def parse_csv_ints(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tiers", default="1,2,3")
    parser.add_argument("--sessions", type=int, default=60)
    parser.add_argument("--include-baseline-a", action="store_true")
    parser.add_argument("--working-windows", default="2,5,10")
    parser.add_argument("--episodic-topks", default="1,3,5,10,20")
    parser.add_argument("--semantic-topks", default="1,2,4")
    parser.add_argument("--max-runs", type=int, default=None)
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    args = parse_args()
    tiers = parse_csv_ints(args.tiers)
    windows = parse_csv_ints(args.working_windows)
    episodic_topks = parse_csv_ints(args.episodic_topks)
    semantic_topks = parse_csv_ints(args.semantic_topks)

    commands: list[list[str]] = []

    if args.include_baseline_a:
        commands.append(
            [
                sys.executable,
                str(RUNNER),
                "--conditions",
                "A",
                "--tiers",
                *[str(tier) for tier in tiers],
                "--sessions",
                str(args.sessions),
                "--run-tag",
                "e05_baseline_a",
            ]
        )

    for window in windows:
        commands.append(
            [
                sys.executable,
                str(RUNNER),
                "--conditions",
                "B",
                "--tiers",
                *[str(tier) for tier in tiers],
                "--sessions",
                str(args.sessions),
                "--working-memory-window",
                str(window),
                "--run-tag",
                f"e05_B_wm{window}",
            ]
        )

    for window, episodic_top_k in itertools.product(windows, episodic_topks):
        commands.append(
            [
                sys.executable,
                str(RUNNER),
                "--conditions",
                "C",
                "--tiers",
                *[str(tier) for tier in tiers],
                "--sessions",
                str(args.sessions),
                "--working-memory-window",
                str(window),
                "--episodic-top-k",
                str(episodic_top_k),
                "--run-tag",
                f"e05_C_wm{window}_ep{episodic_top_k}",
            ]
        )

    for window, episodic_top_k, semantic_top_k in itertools.product(
        windows, episodic_topks, semantic_topks
    ):
        commands.append(
            [
                sys.executable,
                str(RUNNER),
                "--conditions",
                "D",
                "--tiers",
                *[str(tier) for tier in tiers],
                "--sessions",
                str(args.sessions),
                "--working-memory-window",
                str(window),
                "--episodic-top-k",
                str(episodic_top_k),
                "--semantic-top-k",
                str(semantic_top_k),
                "--run-tag",
                f"e05_D_wm{window}_ep{episodic_top_k}_sem{semantic_top_k}",
            ]
        )

    if args.max_runs is not None:
        commands = commands[: args.max_runs]

    for command in commands:
        run_command(command)


if __name__ == "__main__":
    main()
