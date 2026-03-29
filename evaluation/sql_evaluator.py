"""SQL execution and exact-match evaluation helpers."""

from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SqlEvaluationResult:
    is_correct: bool
    generated_rows: list[tuple[Any, ...]]
    ground_truth_rows: list[tuple[Any, ...]]
    generated_error: str | None = None
    result_summary: str = ""


class SqlEvaluator:
    def __init__(self, db_paths: dict[str, Path]) -> None:
        self.db_paths = db_paths

    def evaluate(self, source: str, generated_sql: str, ground_truth_sql: str) -> SqlEvaluationResult:
        db_path = self.db_paths[source]
        gt_rows, gt_error = self._execute(db_path, ground_truth_sql)
        gen_rows, gen_error = self._execute(db_path, generated_sql)
        is_correct = (
            gt_error is None
            and gen_error is None
            and normalized_rows(gt_rows) == normalized_rows(gen_rows)
        )
        summary = self._summarize(gen_rows, gen_error)
        return SqlEvaluationResult(
            is_correct=is_correct,
            generated_rows=gen_rows,
            ground_truth_rows=gt_rows,
            generated_error=gen_error,
            result_summary=summary,
        )

    async def evaluate_async(
        self, source: str, generated_sql: str, ground_truth_sql: str
    ) -> SqlEvaluationResult:
        return await asyncio.to_thread(self.evaluate, source, generated_sql, ground_truth_sql)

    def _execute(self, db_path: Path, sql: str) -> tuple[list[tuple[Any, ...]], str | None]:
        try:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(sql).fetchall()
            return rows, None
        except sqlite3.Error as exc:
            return [], str(exc)

    @staticmethod
    def _summarize(rows: list[tuple[Any, ...]], error: str | None) -> str:
        if error:
            return f"sql_error={error}"
        if not rows:
            return "0 rows"
        return f"{len(rows)} rows; first_row={rows[0]}"


def normalized_rows(rows: list[tuple[Any, ...]]) -> list[tuple[str, ...]]:
    return sorted(tuple(repr(value) for value in row) for row in rows)
