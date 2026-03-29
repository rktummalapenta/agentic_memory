"""Memory Benefit Score helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def accuracy(results: list[dict[str, Any]]) -> float:
    if not results:
        return 0.0
    correct = sum(1 for row in results if row["is_correct"])
    return correct / len(results)


def compute_mbs(memory_accuracy: float, stateless_accuracy: float) -> float | None:
    if stateless_accuracy == 0:
        return None
    return ((memory_accuracy - stateless_accuracy) / stateless_accuracy) * 100.0


def summarize_by_turn_depth(
    results_by_condition: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[int, dict[str, float | None]]]:
    return summarize_dimension(results_by_condition, "turn_number")


def summarize_results(
    results_by_condition: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[str, Any]]:
    return {
        "overall": summarize_overall(results_by_condition),
        "by_turn_number": summarize_dimension(results_by_condition, "turn_number"),
        "by_tier": summarize_dimension(results_by_condition, "tier"),
        "by_source": summarize_dimension(results_by_condition, "source"),
    }


def summarize_overall(
    results_by_condition: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[str, int | float | None]]:
    stateless_rows = results_by_condition.get("A", [])
    stateless_accuracy = accuracy(stateless_rows)
    summary: dict[str, dict[str, int | float | None]] = {}
    for condition, rows in results_by_condition.items():
        condition_accuracy = accuracy(rows)
        mbs = compute_mbs(condition_accuracy, stateless_accuracy)
        summary[condition] = metric_record(
            rows=rows,
            condition_accuracy=condition_accuracy,
            stateless_accuracy=stateless_accuracy,
            include_mbs=condition != "A",
            mbs=mbs,
        )
    return summary


def summarize_dimension(
    results_by_condition: dict[str, list[dict[str, Any]]],
    field: str,
) -> dict[str, dict[Any, dict[str, int | float | None]]]:
    grouped: dict[str, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for condition, rows in results_by_condition.items():
        for row in rows:
            grouped[condition][row[field]].append(row)

    stateless_group_accuracy = {
        group_value: accuracy(rows) for group_value, rows in grouped.get("A", {}).items()
    }

    summary: dict[str, dict[Any, dict[str, int | float | None]]] = {}
    for condition, grouped_rows in grouped.items():
        summary[condition] = {}
        for group_value, rows in grouped_rows.items():
            condition_accuracy = accuracy(rows)
            stateless_accuracy = stateless_group_accuracy.get(group_value, 0.0)
            mbs = compute_mbs(condition_accuracy, stateless_accuracy)
            summary[condition][group_value] = metric_record(
                rows=rows,
                condition_accuracy=condition_accuracy,
                stateless_accuracy=stateless_accuracy,
                include_mbs=condition != "A",
                mbs=mbs,
            )
    return summary


def metric_record(
    rows: list[dict[str, Any]],
    condition_accuracy: float,
    stateless_accuracy: float,
    include_mbs: bool,
    mbs: float | None,
) -> dict[str, int | float | None]:
    correct = sum(1 for row in rows if row["is_correct"])
    total = len(rows)
    absolute_gain = None if not include_mbs else round(condition_accuracy - stateless_accuracy, 4)
    return {
        "correct": correct,
        "total": total,
        "accuracy": round(condition_accuracy, 4),
        "absolute_gain_vs_stateless": absolute_gain,
        "mbs_vs_stateless": None if not include_mbs or mbs is None else round(mbs, 4),
    }
