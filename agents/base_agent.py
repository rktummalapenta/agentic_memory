"""Condition-aware SQL agent for Experiment 0."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from agents.gateway_client import GatewayClient
from memory.chromadb_store import ChromaMemoryStore
from memory.redis_store import RedisWorkingMemoryStore


WORKING_MEMORY_CONDITIONS = {"B", "C", "D"}
EPISODIC_MEMORY_CONDITIONS = {"C", "D"}
SEMANTIC_MEMORY_CONDITIONS = {"D"}


@dataclass
class AgentTurnResult:
    condition: str
    generated_sql: str
    used_context: dict[str, Any]
    semantic_hints: list[str]
    working_turn_count: int
    episodic_turn_count: int


class BaseSqlAgent:
    """Generates SQL from a benchmark turn using the configured memory condition."""

    def __init__(
        self,
        condition: str,
        working_memory: RedisWorkingMemoryStore,
        episodic_memory: ChromaMemoryStore,
        semantic_memory: ChromaMemoryStore,
        gateway_client: GatewayClient,
        source_schemas: dict[str, str],
        window_size: int = 5,
        episodic_top_k: int = 3,
        semantic_top_k: int = 2,
    ) -> None:
        if condition not in {"A", "B", "C", "D"}:
            raise ValueError(f"Unsupported condition: {condition}")
        self.condition = condition
        self.working_memory = working_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self.gateway_client = gateway_client
        self.source_schemas = source_schemas
        self.window_size = window_size
        self.episodic_top_k = episodic_top_k
        self.semantic_top_k = semantic_top_k

    async def run_turn(self, session: dict[str, Any], turn: dict[str, Any]) -> AgentTurnResult:
        resolved_context, working_turns, episodic_turns, semantic_hints = await asyncio.gather(
            self._resolve_context(session["session_id"], turn),
            self._working_memory_turns(session["session_id"]),
            self._episodic_memory_turns(session["session_id"], turn["question"]),
            self._semantic_hints(turn),
        )
        messages = self._build_messages(
            source=session["source"],
            turn=turn,
            resolved_context=resolved_context,
            working_turns=working_turns,
            episodic_turns=episodic_turns,
            semantic_hints=semantic_hints,
        )
        generated_sql = await self.gateway_client.generate_sql(messages)

        return AgentTurnResult(
            condition=self.condition,
            generated_sql=generated_sql,
            used_context=resolved_context,
            semantic_hints=semantic_hints,
            working_turn_count=len(working_turns),
            episodic_turn_count=len(episodic_turns),
        )

    async def remember_turn(
        self,
        session: dict[str, Any],
        turn: dict[str, Any],
        generated_sql: str,
        result_summary: str,
    ) -> None:
        payload = {
            "turn_number": turn["turn_number"],
            "question": turn["question"],
            "generated_sql": generated_sql,
            "result_summary": result_summary,
            "state_updates": turn.get("state_updates", {}),
            "source": session["source"],
            "session_id": session["session_id"],
        }
        if self.condition in WORKING_MEMORY_CONDITIONS:
            await self.working_memory.append_turn_async(session["session_id"], payload)
        if self.condition in EPISODIC_MEMORY_CONDITIONS:
            await self.episodic_memory.add_episode(session["session_id"], payload)

    async def _resolve_context(self, session_id: str, turn: dict[str, Any]) -> dict[str, Any]:
        if self.condition == "A":
            return {}

        required_keys = turn.get("referenced_context_keys", [])
        resolved: dict[str, Any] = {}

        if self.condition in WORKING_MEMORY_CONDITIONS:
            resolved.update(
                await self.working_memory.resolve_context_async(
                    session_id, required_keys, self.window_size
                )
            )

        if self.condition in EPISODIC_MEMORY_CONDITIONS and missing_keys(required_keys, resolved):
            resolved.update(
                await self.episodic_memory.resolve_context(
                    session_id, turn["question"], missing_keys(required_keys, resolved)
                )
            )

        return {key: resolved[key] for key in required_keys if key in resolved}

    async def _semantic_hints(self, turn: dict[str, Any]) -> list[str]:
        if self.condition not in SEMANTIC_MEMORY_CONDITIONS:
            return []
        return await self.semantic_memory.retrieve_semantic_notes(
            turn["source"], turn["question"], top_k=self.semantic_top_k
        )

    async def _working_memory_turns(self, session_id: str) -> list[dict[str, Any]]:
        if self.condition not in WORKING_MEMORY_CONDITIONS:
            return []
        return await self.working_memory.get_recent_turns_async(session_id, self.window_size)

    async def _episodic_memory_turns(
        self, session_id: str, question: str
    ) -> list[dict[str, Any]]:
        if self.condition not in EPISODIC_MEMORY_CONDITIONS:
            return []
        return await self.episodic_memory.retrieve_episodes(
            session_id, question, top_k=self.episodic_top_k
        )

    def _build_messages(
        self,
        source: str,
        turn: dict[str, Any],
        resolved_context: dict[str, Any],
        working_turns: list[dict[str, Any]],
        episodic_turns: list[dict[str, Any]],
        semantic_hints: list[str],
    ) -> list[dict[str, str]]:
        content_blocks = [
            f"Source dataset: {source}",
            "Database schema:",
            self.source_schemas[source],
            "Source-specific guidance:",
            source_guidance(source),
        ]

        if working_turns:
            content_blocks.extend(
                [
                    "Recent conversation history:",
                    _format_working_turns(working_turns),
                ]
            )

        if episodic_turns:
            content_blocks.extend(
                [
                    "Relevant prior retrieved episodes:",
                    _format_episodic_turns(episodic_turns),
                ]
            )

        if resolved_context:
            content_blocks.extend(
                [
                    "Resolved structured context:",
                    json_like(resolved_context),
                ]
            )

        if semantic_hints:
            content_blocks.extend(
                [
                    "Additional semantic hints:",
                    "\n".join(f"- {hint}" for hint in semantic_hints),
                ]
            )

        content_blocks.extend(
            [
                "Current user question:",
                turn["question"],
                "Output requirements:",
                output_requirements(source, turn["question"]),
                "Return exactly one SQLite SQL query and nothing else.",
            ]
        )

        return [
            {
                "role": "system",
                "content": (
                    "You are an expert SQLite analyst. Generate one valid SQLite query for the user's question. "
                    "Return SQL only. No markdown, comments, or explanation. Use only the provided schema and context. "
                    "If resolved structured context is provided, those values are authoritative and must be used exactly. "
                    "Match the requested result shape exactly. If the question asks for a total, return a single aggregate value only, "
                    "not supporting columns, not grouped rows, and not explanatory text."
                ),
            },
            {
                "role": "user",
                "content": "\n\n".join(block for block in content_blocks if block),
            },
        ]


def missing_keys(required_keys: list[str], resolved: dict[str, Any]) -> list[str]:
    return [key for key in required_keys if key not in resolved]


def _format_working_turns(turns: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for turn in turns:
        lines.append(
            "\n".join(
                [
                    f"Turn {turn.get('turn_number')}: {turn.get('question', '')}",
                    f"SQL: {turn.get('generated_sql', '')}",
                    f"Result: {turn.get('result_summary', '')}",
                    f"State updates: {json_like(turn.get('state_updates', {}))}",
                ]
            )
        )
    return "\n\n".join(lines)


def _format_episodic_turns(turns: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for index, turn in enumerate(turns, start=1):
        payload = turn.get("payload", {})
        lines.append(
            "\n".join(
                [
                    f"Retrieved episode {index}: {payload.get('question', '')}",
                    f"SQL: {payload.get('generated_sql', '')}",
                    f"Result: {payload.get('result_summary', '')}",
                    f"State updates: {json_like(payload.get('state_updates', {}))}",
                ]
            )
        )
    return "\n\n".join(lines)


def json_like(payload: dict[str, Any]) -> str:
    if not payload:
        return "{}"
    return ", ".join(f"{key}={value}" for key, value in payload.items())


def source_guidance(source: str) -> str:
    if source == "northwind":
        return "\n".join(
            [
                "- Customer names are stored in Customers.CompanyName.",
                "- Orders.CustomerID joins to Customers.CustomerID.",
                "- Sales totals come from [Order Details] using UnitPrice * Quantity * (1 - Discount).",
                "- For yearly sales questions, use Orders.OrderDate, not Orders.ShippedDate.",
                "- If the question asks for total sales for one customer and one year, return one row with one numeric aggregate column only.",
                "- For those total-sales questions, do not return CompanyName, OrderID, or per-order subtotals.",
                "- Do not GROUP BY unless the user explicitly asks for a breakdown by year, month, country, customer, or another dimension.",
                "- Do not confuse customer company names with product names or category names.",
                "- If resolved context contains customer_id, use that exact CustomerID.",
            ]
        )
    if source == "sec_edgar":
        return "\n".join(
            [
                "- annual_financials joins to companies by ticker.",
                "- Company names live in companies.company_name.",
                "- value_billions is the normalized metric used in benchmark queries.",
                "- Metric values must use exact lowercase stored values such as revenue, net_income, cash, total_assets, total_liabilities.",
                "- If resolved context contains ticker, metric, or years, use them exactly.",
            ]
        )
    if source == "bird":
        return "\n".join(
            [
                "- Region names are in district.A3.",
                "- loan joins to account, then disp where type='OWNER', then client, then district.",
                "- Loan status values are raw codes A, B, C, D.",
                "- If resolved context contains region or loan_status, use them exactly.",
            ]
        )
    return ""


def output_requirements(source: str, question: str) -> str:
    normalized_question = question.lower()
    if source == "northwind" and "sales for" in normalized_question:
        return "\n".join(
            [
                "- Return exactly one row and one column.",
                "- Alias the output column as sales_total.",
                "- Use Orders.OrderDate for the year filter.",
                "- Aggregate at the customer-total level only; no GROUP BY for customer or order.",
            ]
        )
    if source == "sec_edgar" and any(
        phrase in normalized_question for phrase in ["how much", "what was", "show", "total", "value"]
    ):
        return "\n".join(
            [
                "- Return only the columns needed to answer the question.",
                "- If the user asks for a single value, return one row and one column only.",
            ]
        )
    return "- Return only the columns and rows required to answer the question."
