"""Summarize common SQL-generation failures from an Experiment 0 results file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-file",
        required=True,
        help="Path to a results_*.json file produced by Experiment 0.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=5,
        help="How many incorrect examples to print per condition.",
    )
    parser.add_argument(
        "--compare-conditions",
        nargs=2,
        metavar=("COND_A", "COND_B"),
        help="Optionally compare two conditions and show where one is correct and the other is not.",
    )
    return parser.parse_args()


def classify_failure(row: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    sql = row["generated_sql"].lower()
    gt = row["ground_truth_sql"].lower()
    summary = row.get("result_summary", "").lower()

    if row.get("generated_error"):
        labels.append("sql_error")
    if "companyname" in sql and "customerid" in gt:
        labels.append("uses_company_name_instead_of_customer_id")
    if "group by" in sql and "sales_total" in gt:
        labels.append("wrong_granularity")
    if "orderid" in sql and "sales_total" in gt:
        labels.append("returns_order_level_rows")
    if "shippeddate" in sql and "orderdate" in gt:
        labels.append("uses_shippeddate_instead_of_orderdate")
    if "suppliers" in sql or "products" in sql:
        labels.append("schema_confusion_supplier_or_product")
    if summary == "0 rows":
        labels.append("empty_result")
    if not labels:
        labels.append("other_semantic_mismatch")
    return labels


def print_condition_report(condition: str, rows: list[dict[str, Any]], sample_limit: int) -> None:
    incorrect = [row for row in rows if not row["is_correct"]]
    correct = len(rows) - len(incorrect)
    failure_counts: Counter[str] = Counter()
    for row in incorrect:
        failure_counts.update(classify_failure(row))

    print(f"Condition {condition}")
    print(f"  total turns: {len(rows)}")
    print(f"  correct: {correct}")
    print(f"  incorrect: {len(incorrect)}")
    print(f"  sources: {dict(Counter(row['source'] for row in rows))}")
    print(f"  tiers: {dict(Counter(row['tier'] for row in rows))}")
    print(f"  turn_numbers: {dict(Counter(row['turn_number'] for row in rows))}")
    print(f"  failure_labels: {dict(failure_counts)}")
    print()

    for row in incorrect[:sample_limit]:
        print(f"  - {row['session_id']} | turn {row['turn_number']} | source={row['source']}")
        print(f"    question: {row['question']}")
        print(f"    labels: {', '.join(classify_failure(row))}")
        print(f"    generated_error: {row.get('generated_error')}")
        print(f"    result_summary: {row.get('result_summary')}")
        print(f"    generated_sql: {row['generated_sql']}")
        print(f"    ground_truth_sql: {row['ground_truth_sql']}")
        print()


def print_condition_comparison(
    condition_a: str,
    condition_b: str,
    payload: dict[str, list[dict[str, Any]]],
    sample_limit: int,
) -> None:
    rows_a = {(row["session_id"], row["turn_number"]): row for row in payload[condition_a]}
    rows_b = {(row["session_id"], row["turn_number"]): row for row in payload[condition_b]}
    a_only: list[tuple[tuple[str, int], dict[str, Any], dict[str, Any]]] = []
    b_only: list[tuple[tuple[str, int], dict[str, Any], dict[str, Any]]] = []

    for key, row_a in rows_a.items():
        row_b = rows_b.get(key)
        if row_b is None:
            continue
        if row_a["is_correct"] and not row_b["is_correct"]:
            a_only.append((key, row_a, row_b))
        elif row_b["is_correct"] and not row_a["is_correct"]:
            b_only.append((key, row_a, row_b))

    print(f"Comparison {condition_a} vs {condition_b}")
    print(f"  {condition_a}_correct_{condition_b}_wrong: {len(a_only)}")
    print(f"  {condition_b}_correct_{condition_a}_wrong: {len(b_only)}")
    print()

    if a_only:
        print(f"  {condition_a} wins on:")
        for key, row_a, row_b in a_only[:sample_limit]:
            print(f"  - {key[0]} | turn {key[1]} | source={row_a['source']}")
            print(f"    question: {row_a['question']}")
            print(f"    {condition_a} sql: {row_a['generated_sql']}")
            print(f"    {condition_b} sql: {row_b['generated_sql']}")
            print(f"    {condition_b} labels: {', '.join(classify_failure(row_b))}")
            print()

    if b_only:
        print(f"  {condition_b} wins on:")
        for key, row_a, row_b in b_only[:sample_limit]:
            print(f"  - {key[0]} | turn {key[1]} | source={row_b['source']}")
            print(f"    question: {row_b['question']}")
            print(f"    {condition_a} sql: {row_a['generated_sql']}")
            print(f"    {condition_a} labels: {', '.join(classify_failure(row_a))}")
            print(f"    {condition_b} sql: {row_b['generated_sql']}")
            print()


def main() -> None:
    args = parse_args()
    results_path = Path(args.results_file)
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    for condition, rows in payload.items():
        print_condition_report(condition, rows, args.sample_limit)
    if args.compare_conditions:
        print_condition_comparison(
            args.compare_conditions[0],
            args.compare_conditions[1],
            payload,
            args.sample_limit,
        )


if __name__ == "__main__":
    main()
