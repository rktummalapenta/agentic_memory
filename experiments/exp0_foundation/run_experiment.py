"""Runs the local Experiment 0 benchmark."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path
from typing import Any
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.base_agent import BaseSqlAgent
from agents.gateway_client import GatewayClient
from evaluation.mbs_calculator import summarize_by_turn_depth, summarize_results
from evaluation.sql_evaluator import SqlEvaluator
from memory.chromadb_store import ChromaMemoryStore
from memory.redis_store import RedisWorkingMemoryStore


class ProgressTracker:
    def __init__(self, condition: str, sessions: list[dict[str, Any]]) -> None:
        self.condition = condition
        self.total_sessions = len(sessions)
        self.total_turns = sum(len(session["turns"]) for session in sessions)
        self.completed_sessions = 0
        self.completed_turns = 0
        self._lock = asyncio.Lock()

    def print_start(self) -> None:
        print(
            f"{timestamp_now()} [{self.condition}] starting {self.total_sessions} sessions / {self.total_turns} turns",
            flush=True,
        )

    async def session_started(self, session: dict[str, Any]) -> None:
        async with self._lock:
            print(
                f"{timestamp_now()} [{self.condition}] session start {session['session_id']} "
                f"({len(session['turns'])} turns, source={session['source']}, tier={session['tier']})",
                flush=True,
            )

    async def turn_completed(
        self,
        session: dict[str, Any],
        turn_number: int,
        is_correct: bool,
    ) -> None:
        async with self._lock:
            self.completed_turns += 1
            print(
                f"{timestamp_now()} [{self.condition}] turn {self.completed_turns}/{self.total_turns} "
                f"session={session['session_id']} turn={turn_number} correct={is_correct}",
                flush=True,
            )

    async def session_completed(self, session: dict[str, Any]) -> None:
        async with self._lock:
            self.completed_sessions += 1
            print(
                f"{timestamp_now()} [{self.condition}] session done {self.completed_sessions}/{self.total_sessions} "
                f"{session['session_id']}",
                flush=True,
            )

    def print_end(self) -> None:
        print(
            f"{timestamp_now()} [{self.condition}] finished {self.completed_sessions} sessions / {self.completed_turns} turns",
            flush=True,
        )


DEFAULT_CONFIG = {
    "experiment": {
        "default_condition_order": ["A", "B", "C", "D"],
        "working_memory_window": 5,
        "episodic_memory_top_k": 3,
        "semantic_memory_top_k": 2,
        "smoke_test_sessions_per_source": 1,
        "max_parallel_sessions": 2,
        "results_dir": "experiments/exp0_foundation/results",
    },
    "datasets": {
        "session_file": "data/sessions/all_sessions.json",
        "source_databases": {
            "northwind": "data/northwind/northwind.db",
            "sec_edgar": "data/sec_edgar/sec_edgar.db",
            "bird": "data/bird/bird.db",
        },
    },
    "memory": {
        "semantic_seed_file": "data/sessions/semantic_memory.json",
        "chroma_namespace": "exp0",
        "semantic_namespace": "exp0_semantic",
        "redis_namespace": "exp0",
    },
    "services": {
        "redis": {"host": "127.0.0.1", "port": 6379},
        "chroma": {
            "base_url": "http://127.0.0.1:8000",
            "tenant": "default_tenant",
            "database": "default_database",
        },
        "gateway": {
            "base_url": "http://127.0.0.1:8090",
            "chat_completions_path": "/v1/chat/completions",
            "model_provider": "openai",
            "model": "gpt-5-mini",
            "fallback_model": "gpt-4.1-mini",
        },
    },
}


def load_config() -> dict[str, Any]:
    config_path = ROOT / "config" / "experiment_config.yaml"
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return DEFAULT_CONFIG
    if not config_path.exists():
        config = DEFAULT_CONFIG
    else:
        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
    apply_env_overrides(config)
    return config


def apply_env_overrides(config: dict[str, Any]) -> None:
    experiment = config.setdefault("experiment", {})
    chroma = config.setdefault("services", {}).setdefault("chroma", {})
    gateway = config.setdefault("services", {}).setdefault("gateway", {})
    redis = config.setdefault("services", {}).setdefault("redis", {})

    experiment["max_parallel_sessions"] = int(
        os.getenv("MAX_PARALLEL_SESSIONS", str(experiment.get("max_parallel_sessions", 2)))
    )

    chroma["base_url"] = os.getenv("CHROMA_BASE_URL", chroma.get("base_url", "http://127.0.0.1:8000"))
    chroma["tenant"] = os.getenv("CHROMA_TENANT", chroma.get("tenant", "default_tenant"))
    chroma["database"] = os.getenv("CHROMA_DATABASE", chroma.get("database", "default_database"))

    gateway["base_url"] = os.getenv("GATEWAY_BASE_URL", gateway.get("base_url", "http://127.0.0.1:8090"))
    gateway["chat_completions_path"] = os.getenv(
        "GATEWAY_CHAT_COMPLETIONS_PATH",
        gateway.get("chat_completions_path", "/v1/chat/completions"),
    )
    gateway["model_provider"] = os.getenv(
        "GATEWAY_MODEL_PROVIDER", gateway.get("model_provider", "openai")
    )
    gateway["model"] = os.getenv("GATEWAY_MODEL", gateway.get("model", "gpt-5-mini"))
    gateway["fallback_model"] = os.getenv(
        "GATEWAY_FALLBACK_MODEL", gateway.get("fallback_model", "gpt-4.1-mini")
    )

    redis["host"] = os.getenv("REDIS_HOST", redis.get("host", "127.0.0.1"))
    redis["port"] = int(os.getenv("REDIS_PORT", str(redis.get("port", 6379))))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conditions", nargs="+", default=None)
    parser.add_argument("--tiers", nargs="+", type=int, default=None)
    parser.add_argument("--sessions", type=int, default=None)
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--working-memory-window", type=int, default=None)
    parser.add_argument("--episodic-top-k", type=int, default=None)
    parser.add_argument("--semantic-top-k", type=int, default=None)
    parser.add_argument("--run-tag", default=None)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def select_sessions(
    all_sessions: list[dict[str, Any]],
    tiers: list[int] | None,
    session_limit: int | None,
    smoke_per_source: int | None,
) -> list[dict[str, Any]]:
    filtered = [session for session in all_sessions if tiers is None or session["tier"] in tiers]
    if smoke_per_source is not None:
        selected: list[dict[str, Any]] = []
        counts: dict[str, int] = {}
        for session in filtered:
            source = session["source"]
            counts.setdefault(source, 0)
            if counts[source] < smoke_per_source:
                selected.append(session)
                counts[source] += 1
        return selected
    if session_limit is not None:
        return stratified_session_sample(filtered, session_limit)
    return filtered


def stratified_session_sample(
    sessions: list[dict[str, Any]],
    session_limit: int,
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for session in sessions:
        buckets[(session["source"], session["tier"])].append(session)

    ordered_bucket_keys = sorted(buckets.keys(), key=lambda item: (item[0], item[1]))
    selected: list[dict[str, Any]] = []

    while len(selected) < session_limit:
        made_progress = False
        for bucket_key in ordered_bucket_keys:
            bucket = buckets[bucket_key]
            if not bucket:
                continue
            selected.append(bucket.pop(0))
            made_progress = True
            if len(selected) >= session_limit:
                break
        if not made_progress:
            break
    return selected


async def run_single_session(
    condition: str,
    session: dict[str, Any],
    config: dict[str, Any],
    gateway_client: GatewayClient,
    semantic_memory: ChromaMemoryStore,
    evaluator: SqlEvaluator,
    source_schemas: dict[str, str],
    run_namespace: str,
    redis_namespace: str,
    progress: ProgressTracker,
) -> list[dict[str, Any]]:
    chroma_service = config["services"]["chroma"]
    redis_service = config["services"]["redis"]
    working_memory = RedisWorkingMemoryStore(
        namespace=redis_namespace,
        host=redis_service["host"],
        port=redis_service["port"],
    )
    episodic_memory = ChromaMemoryStore(
        namespace=run_namespace,
        base_url=chroma_service["base_url"],
        tenant=chroma_service["tenant"],
        database=chroma_service["database"],
    )
    await working_memory.clear_session_async(session["session_id"])
    agent = BaseSqlAgent(
        condition=condition,
        working_memory=working_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        gateway_client=gateway_client,
        source_schemas=source_schemas,
        window_size=config["experiment"]["working_memory_window"],
        episodic_top_k=config["experiment"]["episodic_memory_top_k"],
        semantic_top_k=config["experiment"]["semantic_memory_top_k"],
    )

    results: list[dict[str, Any]] = []
    try:
        await progress.session_started(session)
        for turn in session["turns"]:
            turn_result = await agent.run_turn(session, turn)
            evaluation = await evaluator.evaluate_async(
                session["source"], turn_result.generated_sql, turn["ground_truth_sql"]
            )
            await agent.remember_turn(
                session=session,
                turn=turn,
                generated_sql=turn_result.generated_sql,
                result_summary=evaluation.result_summary,
            )
            results.append(
                {
                    "condition": condition,
                    "session_id": session["session_id"],
                    "source": session["source"],
                    "tier": session["tier"],
                    "turn_number": turn["turn_number"],
                    "memory_benefit_expected": turn["memory_benefit_expected"],
                    "question": turn["question"],
                    "generated_sql": turn_result.generated_sql,
                    "ground_truth_sql": turn["ground_truth_sql"],
                    "is_correct": evaluation.is_correct,
                    "generated_error": evaluation.generated_error,
                    "result_summary": evaluation.result_summary,
                    "used_context": turn_result.used_context,
                    "semantic_hints": turn_result.semantic_hints,
                    "working_turn_count": turn_result.working_turn_count,
                    "episodic_turn_count": turn_result.episodic_turn_count,
                    "semantic_hint_count": len(turn_result.semantic_hints),
                }
            )
            await progress.turn_completed(session, turn["turn_number"], evaluation.is_correct)
    finally:
        await episodic_memory.aclose()
    await progress.session_completed(session)
    return results


async def run_condition(
    condition: str,
    sessions: list[dict[str, Any]],
    config: dict[str, Any],
    semantic_seed: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    db_paths = {
        name: ROOT / value for name, value in config["datasets"]["source_databases"].items()
    }
    source_schemas = {name: load_source_schema(path) for name, path in db_paths.items()}
    evaluator = SqlEvaluator(db_paths)
    run_namespace = f"{config['memory']['chroma_namespace']}_{condition}_{uuid4().hex[:8]}"
    redis_namespace = f"{config['memory']['redis_namespace']}_{condition}_{uuid4().hex[:8]}"
    chroma_service = config["services"]["chroma"]
    gateway_service = config["services"]["gateway"]
    gateway_client = GatewayClient(
        base_url=gateway_service["base_url"],
        chat_completions_path=gateway_service["chat_completions_path"],
        model=gateway_service["model"],
        fallback_model=gateway_service.get("fallback_model"),
        model_provider=gateway_service.get("model_provider", "openai"),
    )
    semantic_memory = ChromaMemoryStore(
        namespace=config["memory"]["semantic_namespace"],
        semantic_seed=semantic_seed,
        base_url=chroma_service["base_url"],
        tenant=chroma_service["tenant"],
        database=chroma_service["database"],
    )
    semaphore = asyncio.Semaphore(config["experiment"].get("max_parallel_sessions", 4))
    progress = ProgressTracker(condition, sessions)
    progress.print_start()

    async def guarded_run(session: dict[str, Any]) -> list[dict[str, Any]]:
        async with semaphore:
            return await run_single_session(
                condition=condition,
                session=session,
                config=config,
                gateway_client=gateway_client,
                semantic_memory=semantic_memory,
                evaluator=evaluator,
                source_schemas=source_schemas,
                run_namespace=run_namespace,
                redis_namespace=redis_namespace,
                progress=progress,
            )

    try:
        session_results = await asyncio.gather(*(guarded_run(session) for session in sessions))
    finally:
        await semantic_memory.aclose()
        await gateway_client.aclose()
        progress.print_end()
    results: list[dict[str, Any]] = []
    for batch in session_results:
        results.extend(batch)
    return results


def write_results(
    output_dir: Path,
    results_by_condition: dict[str, list[dict[str, Any]]],
    run_label: str,
    run_metadata: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    detail_path = output_dir / f"results_{timestamp}_{run_label}.json"
    summary_path = output_dir / f"summary_{timestamp}_{run_label}.json"
    metadata_path = output_dir / f"runmeta_{timestamp}_{run_label}.json"
    detail_path.write_text(json.dumps(results_by_condition, indent=2))
    summary_path.write_text(json.dumps(summarize_results(results_by_condition), indent=2))
    metadata_path.write_text(json.dumps(run_metadata, indent=2))
    print(f"Detailed results: {detail_path}", flush=True)
    print(f"Summary results: {summary_path}", flush=True)
    print(f"Run metadata: {metadata_path}", flush=True)


def apply_arg_overrides(config: dict[str, Any], args: argparse.Namespace) -> None:
    experiment = config.setdefault("experiment", {})

    if args.working_memory_window is not None:
        experiment["working_memory_window"] = args.working_memory_window
    if args.episodic_top_k is not None:
        experiment["episodic_memory_top_k"] = args.episodic_top_k
    if args.semantic_top_k is not None:
        experiment["semantic_memory_top_k"] = args.semantic_top_k


def build_run_metadata(
    config: dict[str, Any],
    conditions: list[str],
    tiers: list[int] | None,
    selected_sessions: list[dict[str, Any]],
    run_label: str,
) -> dict[str, Any]:
    experiment = config["experiment"]
    gateway = config["services"]["gateway"]
    return {
        "run_label": run_label,
        "conditions": conditions,
        "tiers": tiers or [],
        "session_count": len(selected_sessions),
        "sources": sorted({session["source"] for session in selected_sessions}),
        "tier_counts": summarize_session_counts(selected_sessions, "tier"),
        "source_counts": summarize_session_counts(selected_sessions, "source"),
        "model_provider": gateway.get("model_provider"),
        "model": gateway["model"],
        "working_memory_window": experiment["working_memory_window"],
        "episodic_memory_top_k": experiment["episodic_memory_top_k"],
        "semantic_memory_top_k": experiment["semantic_memory_top_k"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
    }


def summarize_session_counts(
    sessions: list[dict[str, Any]],
    field: str,
) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for session in sessions:
        counts[str(session[field])] += 1
    return dict(sorted(counts.items()))


async def async_main() -> None:
    args = parse_args()
    config = load_config()
    apply_arg_overrides(config, args)
    sessions_path = ROOT / config["datasets"]["session_file"]
    semantic_seed_path = ROOT / config["memory"]["semantic_seed_file"]
    sessions = load_json(sessions_path)
    semantic_seed = load_json(semantic_seed_path)
    selected_sessions = select_sessions(
        all_sessions=sessions,
        tiers=args.tiers,
        session_limit=args.sessions,
        smoke_per_source=config["experiment"]["smoke_test_sessions_per_source"]
        if args.smoke_test
        else None,
    )
    conditions = args.conditions or config["experiment"]["default_condition_order"]
    run_label = build_run_label(
        conditions=conditions,
        tiers=args.tiers,
        session_count=len(selected_sessions),
        model=config["services"]["gateway"]["model"],
        working_memory_window=config["experiment"]["working_memory_window"],
        episodic_top_k=config["experiment"]["episodic_memory_top_k"],
        semantic_top_k=config["experiment"]["semantic_memory_top_k"],
        run_tag=args.run_tag,
    )
    results_by_condition = {}
    for condition in conditions:
        results_by_condition[condition] = await run_condition(
            condition, selected_sessions, config, semantic_seed
        )
    output_dir = ROOT / config["experiment"]["results_dir"]
    write_results(
        output_dir,
        results_by_condition,
        run_label,
        build_run_metadata(config, conditions, args.tiers, selected_sessions, run_label),
    )
    print(json.dumps(summarize_by_turn_depth(results_by_condition), indent=2))


def load_source_schema(db_path: Path) -> str:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT name, type, sql
            FROM sqlite_master
            WHERE type IN ('table', 'view')
              AND name NOT LIKE 'sqlite_%'
            ORDER BY type, name
            """
        ).fetchall()
    blocks = []
    for name, object_type, sql in rows:
        if not sql:
            continue
        blocks.append(f"{object_type.upper()} {name}\n{sql}")
    return "\n\n".join(blocks)


def build_run_label(
    conditions: list[str],
    tiers: list[int] | None,
    session_count: int,
    model: str,
    working_memory_window: int,
    episodic_top_k: int,
    semantic_top_k: int,
    run_tag: str | None = None,
) -> str:
    tier_label = "alltiers" if not tiers else "tiers-" + "-".join(str(tier) for tier in tiers)
    condition_label = "conds-" + "-".join(conditions)
    model_label = "model-" + sanitize_label(model)
    memory_label = (
        f"wm-{working_memory_window}_epk-{episodic_top_k}_semk-{semantic_top_k}"
    )
    label = f"{condition_label}_{tier_label}_sessions-{session_count}_{model_label}_{memory_label}"
    if run_tag:
        label = f"{label}_{sanitize_label(run_tag)}"
    return label


def sanitize_label(value: str) -> str:
    cleaned = []
    for char in value:
        if char.isalnum():
            cleaned.append(char)
        elif char in {"-", "_"}:
            cleaned.append(char)
        else:
            cleaned.append("-")
    return "".join(cleaned).strip("-")


def timestamp_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


if __name__ == "__main__":
    asyncio.run(async_main())
