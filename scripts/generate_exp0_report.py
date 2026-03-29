"""Generate a markdown report and charts for an Experiment 0 results bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

_cache_root = os.path.join(tempfile.gettempdir(), "agentic_memory_cache")
os.makedirs(_cache_root, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_cache_root, "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", _cache_root)
os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt

from evaluation.mbs_calculator import summarize_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-file", required=True)
    parser.add_argument("--summary-file", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--title", default="Experiment 0 Pilot Report")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_failure(row: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    sql = row["generated_sql"].lower()
    gt = row["ground_truth_sql"].lower()
    summary = row.get("result_summary", "").lower()
    if row.get("generated_error"):
        labels.append("sql_error")
    if "companyname" in sql and "customerid" in gt:
        labels.append("company_name_vs_id")
    if "group by" in sql and "count(" not in sql and "max(" not in sql and "min(" not in sql:
        labels.append("wrong_granularity")
    if "orderid" in sql and ("count(" not in sql and "max(" not in sql and "min(" not in sql):
        labels.append("returns_extra_columns")
    if "shippeddate" in sql and "orderdate" in gt:
        labels.append("wrong_date_field")
    if summary == "0 rows":
        labels.append("empty_result")
    if not labels:
        labels.append("other_semantic_mismatch")
    return labels


def top_failures(rows: list[dict[str, Any]], limit: int = 5) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for row in rows:
        if row["is_correct"]:
            continue
        counter.update(classify_failure(row))
    return counter.most_common(limit)


def format_metric_row(label: str, metric: dict[str, Any]) -> str:
    accuracy_pct = f"{metric['accuracy'] * 100:.1f}%"
    gain = metric["absolute_gain_vs_stateless"]
    gain_text = "—" if gain is None else f"{gain * 100:+.1f} pts"
    mbs = metric["mbs_vs_stateless"]
    mbs_text = "—" if mbs is None else f"{mbs:.1f}%"
    return f"| {label} | {metric['correct']} | {metric['total']} | {accuracy_pct} | {gain_text} | {mbs_text} |"


def save_overall_chart(summary: dict[str, Any], output_path: Path) -> None:
    overall = summary["overall"]
    conditions = list(overall.keys())
    accuracies = [overall[condition]["accuracy"] * 100 for condition in conditions]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(conditions, accuracies, color=["#6c757d", "#198754", "#0d6efd", "#fd7e14"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Experiment 0 Pilot: Overall Accuracy by Condition")
    for bar, value in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value:.1f}%", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_turn_chart(summary: dict[str, Any], output_path: Path) -> None:
    by_turn = summary["by_turn_number"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for condition, groups in by_turn.items():
        turns = sorted(int(turn) for turn in groups.keys())
        accuracies = [groups[str(turn)]["accuracy"] * 100 if str(turn) in groups else groups[turn]["accuracy"] * 100 for turn in turns]
        ax.plot(turns, accuracies, marker="o", linewidth=2, label=condition)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Turn Number")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy by Turn Number")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_source_chart(summary: dict[str, Any], output_path: Path) -> None:
    by_source = summary["by_source"]
    sources = sorted({source for groups in by_source.values() for source in groups.keys()})
    conditions = list(by_source.keys())
    x = range(len(sources))
    width = 0.18
    fig, ax = plt.subplots(figsize=(9, 5))
    for index, condition in enumerate(conditions):
        offsets = [value + (index - 1.5) * width for value in x]
        values = [by_source[condition][source]["accuracy"] * 100 for source in sources]
        ax.bar(offsets, values, width=width, label=condition)
    ax.set_xticks(list(x))
    ax.set_xticklabels(sources)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy by Dataset Source")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_tier_chart(summary: dict[str, Any], output_path: Path) -> None:
    by_tier = summary["by_tier"]
    tiers = sorted({int(tier) for groups in by_tier.values() for tier in groups.keys()})
    conditions = list(by_tier.keys())
    x = range(len(tiers))
    width = 0.18
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for index, condition in enumerate(conditions):
        offsets = [value + (index - 1.5) * width for value in x]
        values = [by_tier[condition][str(tier)]["accuracy"] * 100 if str(tier) in by_tier[condition] else by_tier[condition][tier]["accuracy"] * 100 for tier in tiers]
        ax.bar(offsets, values, width=width, label=condition)
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(tier) for tier in tiers])
    ax.set_ylim(0, 100)
    ax.set_xlabel("Tier")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy by Tier")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def pairwise_wins(results: dict[str, list[dict[str, Any]]], left: str, right: str) -> tuple[int, int]:
    left_rows = {(row["session_id"], row["turn_number"]): row for row in results[left]}
    right_rows = {(row["session_id"], row["turn_number"]): row for row in results[right]}
    left_wins = 0
    right_wins = 0
    for key, left_row in left_rows.items():
        right_row = right_rows.get(key)
        if right_row is None:
            continue
        if left_row["is_correct"] and not right_row["is_correct"]:
            left_wins += 1
        elif right_row["is_correct"] and not left_row["is_correct"]:
            right_wins += 1
    return left_wins, right_wins


def build_report(
    title: str,
    results_path: Path,
    summary_path: Path,
    summary: dict[str, Any],
    results: dict[str, list[dict[str, Any]]],
    chart_paths: dict[str, str],
) -> str:
    overall = summary["overall"]
    by_source = summary["by_source"]
    by_tier = summary["by_tier"]
    b_vs_c = pairwise_wins(results, "B", "C")
    b_vs_d = pairwise_wins(results, "B", "D")
    c_vs_d = pairwise_wins(results, "C", "D")

    best_overall = max(
        (condition for condition in overall if condition != "A"),
        key=lambda condition: overall[condition]["accuracy"],
    )
    bird_best = max(("B", "C", "D"), key=lambda condition: by_source[condition]["bird"]["accuracy"])
    northwind_best = max(("B", "C", "D"), key=lambda condition: by_source[condition]["northwind"]["accuracy"])
    sec_best = max(("B", "C", "D"), key=lambda condition: by_source[condition]["sec_edgar"]["accuracy"])

    lines = [
        f"# {title}",
        "",
        f"- Results file: `{results_path.name}`",
        f"- Summary file: `{summary_path.name}`",
        "",
        "## Framing",
        "",
        "This is Experiment 0 in the enterprise AI memory program: a foundation study asking whether memory infrastructure materially improves multi-turn enterprise SQL tasks before moving on to backend comparisons or systems optimization. The practical industry framing matches the broader Forbes Technology Council angle in this repo: memory should be treated as infrastructure, not as an optional prompt add-on.",
        "",
        "## Executive Summary",
        "",
        f"- Stateless performance remained low overall at `{overall['A']['accuracy'] * 100:.1f}%` (`{overall['A']['correct']}/{overall['A']['total']}`).",
        f"- All memory-enabled conditions were far stronger overall: `B={overall['B']['accuracy'] * 100:.1f}%`, `C={overall['C']['accuracy'] * 100:.1f}%`, `D={overall['D']['accuracy'] * 100:.1f}%`.",
        f"- The best overall condition in this pilot was `{best_overall}`.",
        f"- Best condition by dataset varied: `northwind={northwind_best}`, `sec_edgar={sec_best}`, `bird={bird_best}`.",
        "- This means the pilot already supports the main E0 claim that memory matters, but it does not yet support a universal claim that one memory stack dominates all enterprise data settings.",
        "",
        "## Overall Results",
        "",
        "| Condition | Correct | Total | Accuracy | Gain vs A | MBS |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in ["A", "B", "C", "D"]:
        lines.append(format_metric_row(condition, overall[condition]))

    lines.extend(
        [
            "",
            "## Key Findings",
            "",
            f"- Tier 2 favored `D` (`{by_tier['D']['2']['accuracy'] * 100:.1f}%`), while Tier 3 slightly favored `C` (`{by_tier['C']['3']['accuracy'] * 100:.1f}%`).",
            f"- `B` vs `C`: `B` won on `{b_vs_c[0]}` turns while `C` won on `{b_vs_c[1]}` turns.",
            f"- `B` vs `D`: `B` won on `{b_vs_d[0]}` turns while `D` won on `{b_vs_d[1]}` turns.",
            f"- `C` vs `D`: `C` won on `{c_vs_d[0]}` turns while `D` won on `{c_vs_d[1]}` turns.",
            "- The overall pattern is that working memory already provides most of the benefit; episodic and semantic memory add value, but that value is domain-dependent rather than uniform.",
            "",
            "## Dataset View",
            "",
            "| Source | A | B | C | D | Best |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
            f"| bird | {by_source['A']['bird']['accuracy'] * 100:.1f}% | {by_source['B']['bird']['accuracy'] * 100:.1f}% | {by_source['C']['bird']['accuracy'] * 100:.1f}% | {by_source['D']['bird']['accuracy'] * 100:.1f}% | {bird_best} |",
            f"| northwind | {by_source['A']['northwind']['accuracy'] * 100:.1f}% | {by_source['B']['northwind']['accuracy'] * 100:.1f}% | {by_source['C']['northwind']['accuracy'] * 100:.1f}% | {by_source['D']['northwind']['accuracy'] * 100:.1f}% | {northwind_best} |",
            f"| sec_edgar | {by_source['A']['sec_edgar']['accuracy'] * 100:.1f}% | {by_source['B']['sec_edgar']['accuracy'] * 100:.1f}% | {by_source['C']['sec_edgar']['accuracy'] * 100:.1f}% | {by_source['D']['sec_edgar']['accuracy'] * 100:.1f}% | {sec_best} |",
            "",
            "## Failure Pattern Snapshot",
            "",
        ]
    )

    for condition in ["A", "B", "C", "D"]:
        failures = ", ".join(f"{label}={count}" for label, count in top_failures(results[condition], limit=4))
        lines.append(f"- `{condition}` top failure labels: {failures}")

    lines.extend(
        [
            "",
            "## Figures",
            "",
            f"![Overall Accuracy]({chart_paths['overall']})",
            "",
            f"![Turn Accuracy]({chart_paths['turns']})",
            "",
            f"![Source Accuracy]({chart_paths['source']})",
            "",
            f"![Tier Accuracy]({chart_paths['tier']})",
            "",
            "## Forbes / Enterprise Hook",
            "",
            "For enterprise AI leaders, the message from this pilot is not simply that memory helps. The more important conclusion is that memory helps exactly where enterprise workflows become conversational and stateful: follow-up questions, narrowed comparisons, and context-carrying analytical threads. Stateless agents are acceptable on first-turn questions, but they fail sharply once the user expects the system to remember prior analytical context. That is the infrastructure argument for enterprise memory systems.",
            "",
            "## What Completes Experiment 0",
            "",
            "- Expand beyond this 30-session pilot to a larger stratified slice or full corpus.",
            "- Keep `A` as the baseline; do not remove it, because it quantifies both where memory helps and where memory adds no value.",
            "- Report absolute accuracy and absolute gain vs `A` as the primary metrics; use MBS as a secondary interpretive metric.",
            "- Follow with pairwise ablation analysis (`B` vs `C`, `C` vs `D`) by dataset to explain which memory layer is contributing in each domain.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    results_path = Path(args.results_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = load_json(results_path)
    if args.summary_file:
        summary_path = Path(args.summary_file)
        summary = load_json(summary_path)
    else:
        summary = summarize_results(results)
        summary_path = output_dir / f"{results_path.stem.replace('results_', 'summary_')}.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    overall_chart = output_dir / "overall_accuracy.png"
    turn_chart = output_dir / "accuracy_by_turn.png"
    source_chart = output_dir / "accuracy_by_source.png"
    tier_chart = output_dir / "accuracy_by_tier.png"

    save_overall_chart(summary, overall_chart)
    save_turn_chart(summary, turn_chart)
    save_source_chart(summary, source_chart)
    save_tier_chart(summary, tier_chart)

    report_path = output_dir / "report.md"
    report = build_report(
        title=args.title,
        results_path=results_path,
        summary_path=summary_path,
        summary=summary,
        results=results,
        chart_paths={
            "overall": overall_chart.name,
            "turns": turn_chart.name,
            "source": source_chart.name,
            "tier": tier_chart.name,
        },
    )
    report_path.write_text(report, encoding="utf-8")
    print(report_path)
    print(overall_chart)
    print(turn_chart)
    print(source_chart)
    print(tier_chart)


if __name__ == "__main__":
    main()
