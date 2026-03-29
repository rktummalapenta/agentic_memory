"""Validates local benchmark datasets and session SQL against the SQLite files."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSIONS_PATH = ROOT / "data" / "sessions" / "all_sessions.json"

DATASETS = {
    "northwind": {
        "db_path": ROOT / "data" / "northwind" / "northwind.db",
        "checks": [
            ("Customers", "SELECT COUNT(*) FROM Customers"),
            ("Orders", "SELECT COUNT(*) FROM Orders"),
            ("Order Details", "SELECT COUNT(*) FROM [Order Details]"),
        ],
    },
    "sec_edgar": {
        "db_path": ROOT / "data" / "sec_edgar" / "sec_edgar.db",
        "checks": [
            ("companies", "SELECT COUNT(*) FROM companies"),
            ("annual_financials", "SELECT COUNT(*) FROM annual_financials"),
            ("quarterly_financials", "SELECT COUNT(*) FROM quarterly_financials"),
        ],
    },
    "bird": {
        "db_path": ROOT / "data" / "bird" / "bird.db",
        "checks": [
            ("district", "SELECT COUNT(*) FROM district"),
            ("client", "SELECT COUNT(*) FROM client"),
            ("loan", "SELECT COUNT(*) FROM loan"),
        ],
    },
}


def main() -> None:
    sessions = json.loads(SESSIONS_PATH.read_text(encoding="utf-8"))
    report: dict[str, object] = {"datasets": {}, "session_validation": {}}

    for dataset_name, config in DATASETS.items():
        db_path = config["db_path"]
        dataset_report: dict[str, object] = {
            "db_path": str(db_path.relative_to(ROOT)),
            "exists": db_path.exists(),
            "table_counts": {},
        }
        if db_path.exists():
            with sqlite3.connect(db_path) as conn:
                for label, query in config["checks"]:
                    dataset_report["table_counts"][label] = conn.execute(query).fetchone()[0]
        report["datasets"][dataset_name] = dataset_report

    failures: list[dict[str, object]] = []
    empties: list[dict[str, object]] = []
    validated_turns = 0

    for session in sessions:
        source = session["source"]
        db_path = DATASETS[source]["db_path"]
        with sqlite3.connect(db_path) as conn:
            for turn in session["turns"]:
                validated_turns += 1
                sql = turn["ground_truth_sql"]
                try:
                    rows = conn.execute(sql).fetchall()
                except sqlite3.Error as exc:
                    failures.append(
                        {
                            "session_id": session["session_id"],
                            "source": source,
                            "turn_number": turn["turn_number"],
                            "error": str(exc),
                            "sql": sql,
                        }
                    )
                    continue
                if len(rows) == 0 or all(len(row) == 1 and row[0] is None for row in rows):
                    empties.append(
                        {
                            "session_id": session["session_id"],
                            "source": source,
                            "turn_number": turn["turn_number"],
                            "sql": sql,
                        }
                    )

    report["session_validation"] = {
        "sessions_file": str(SESSIONS_PATH.relative_to(ROOT)),
        "validated_turns": validated_turns,
        "failure_count": len(failures),
        "empty_result_count": len(empties),
        "failures": failures,
        "empty_results": empties,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
