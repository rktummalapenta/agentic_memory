"""Clears local runtime memory artifacts for development runs."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory.chromadb_store import ChromaHttpClient
from memory.redis_store import RedisWorkingMemoryStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", default="e0")
    parser.add_argument("--include-semantic", action="store_true")
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    manifest_path = ROOT / "results" / f"{args.experiment}_semantic_seed.json"
    if manifest_path.exists():
        manifest_path.unlink()
    if args.experiment == "e0":
        redis_store = RedisWorkingMemoryStore(namespace="exp0")
        await redis_store.clear_namespace_async()
        chroma_client = ChromaHttpClient(
            base_url=os.getenv("CHROMA_BASE_URL", "http://127.0.0.1:8000"),
            tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
            database=os.getenv("CHROMA_DATABASE", "default_database"),
            timeout_seconds=2.0,
        )
        try:
            if await chroma_client.ensure_enabled():
                for collection in await chroma_client.list_collections():
                    name = collection.get("name", "")
                    if name.startswith("exp0_") and (
                        args.include_semantic or not name.startswith("exp0_semantic_")
                    ):
                        await chroma_client.delete_collection(name)
        finally:
            await chroma_client.aclose()
    print(f"Cleared runtime artifacts for {args.experiment}")


if __name__ == "__main__":
    asyncio.run(async_main())
