"""Performs lightweight local setup checks for E0 development."""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory.chromadb_store import ChromaHttpClient
from memory.redis_store import RedisWorkingMemoryStore


def check_db(path: Path, table: str) -> tuple[bool, str]:
    if not path.exists():
        return False, f"missing file: {path}"
    try:
        with sqlite3.connect(path) as conn:
            conn.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone()
        return True, "ok"
    except sqlite3.Error as exc:
        return False, str(exc)


async def async_main() -> None:
    redis_store = RedisWorkingMemoryStore(namespace="exp0_verify")
    chroma_client = ChromaHttpClient(
        base_url=os.getenv("CHROMA_BASE_URL", "http://127.0.0.1:8000"),
        tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
        database=os.getenv("CHROMA_DATABASE", "default_database"),
        timeout_seconds=2.0,
    )
    redis_ping = await redis_store.ping_async()
    chroma_heartbeat = await chroma_client.ping()
    checks = {
        "northwind_db": check_db(ROOT / "data" / "northwind" / "northwind.db", "orders"),
        "sec_edgar_db": check_db(
            ROOT / "data" / "sec_edgar" / "sec_edgar.db", "annual_financials"
        ),
        "bird_db": check_db(ROOT / "data" / "bird" / "bird.db", "loan"),
        "sessions_file": (
            (ROOT / "data" / "sessions" / "all_sessions.json").exists(),
            "ok" if (ROOT / "data" / "sessions" / "all_sessions.json").exists() else "missing file",
        ),
        "semantic_seed_file": (
            (ROOT / "data" / "sessions" / "semantic_memory.json").exists(),
            "ok"
            if (ROOT / "data" / "sessions" / "semantic_memory.json").exists()
            else "missing file",
        ),
        "redis_ping": (redis_ping, "ok" if redis_ping else "unreachable"),
        "chroma_heartbeat": (
            chroma_heartbeat,
            "ok" if chroma_heartbeat else "unreachable",
        ),
    }
    await chroma_client.aclose()
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    asyncio.run(async_main())
