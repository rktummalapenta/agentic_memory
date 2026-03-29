"""Helpers for Experiment 0.5 memory-scaling analysis."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def accuracy(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    correct = sum(1 for row in rows if row["is_correct"])
    return correct / len(rows)


def average_proxy_memory_cost(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    # First-pass proxy: units of memory injected into the prompt.
    # Working turns, episodic turns, and semantic hints each count as one unit.
    costs = [
        float(row.get("working_turn_count", 0))
        + float(row.get("episodic_turn_count", 0))
        + float(row.get("semantic_hint_count", 0))
        for row in rows
    ]
    return mean(costs)


def compute_mse(
    accuracy_gain: float,
    additional_memory_cost: float,
) -> float | None:
    if additional_memory_cost <= 0:
        return None
    return accuracy_gain / additional_memory_cost


def summarize_scaling_run(
    rows: list[dict[str, Any]],
    *,
    baseline_accuracy: float,
    baseline_memory_cost: float = 0.0,
) -> dict[str, int | float | None]:
    run_accuracy = accuracy(rows)
    run_memory_cost = average_proxy_memory_cost(rows)
    accuracy_gain = run_accuracy - baseline_accuracy
    additional_cost = run_memory_cost - baseline_memory_cost
    mse = compute_mse(accuracy_gain, additional_cost)
    return {
        "correct": sum(1 for row in rows if row["is_correct"]),
        "total": len(rows),
        "accuracy": round(run_accuracy, 4),
        "accuracy_gain_vs_baseline": round(accuracy_gain, 4),
        "average_proxy_memory_cost": round(run_memory_cost, 4),
        "additional_memory_cost_vs_baseline": round(additional_cost, 4),
        "mse": None if mse is None else round(mse, 6),
    }


def group_by_condition(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["condition"]].append(row)
    return dict(grouped)
