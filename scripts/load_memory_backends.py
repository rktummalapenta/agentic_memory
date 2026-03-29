"""Seeds local semantic memory for development runs."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory.chromadb_store import ChromaHttpClient, embed_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", default="e0")
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    semantic_path = ROOT / "data" / "sessions" / "semantic_memory.json"
    output_path = ROOT / "results" / f"{args.experiment}_semantic_seed.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    semantic_seed = json.loads(semantic_path.read_text(encoding="utf-8")) if semantic_path.exists() else {}

    if args.experiment == "e0":
        client = ChromaHttpClient(
            base_url=os.getenv("CHROMA_BASE_URL", "http://127.0.0.1:8000"),
            tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
            database=os.getenv("CHROMA_DATABASE", "default_database"),
            timeout_seconds=2.0,
        )
        try:
            if await client.ensure_enabled():
                for source, items in semantic_seed.items():
                    collection_name = f"exp0_semantic_{source}"
                    await client.delete_collection(collection_name)
                    await client.ensure_collection(collection_name)
                    await client.add_records(
                        collection_name=collection_name,
                        ids=[f"{source}-semantic-{index}" for index, _ in enumerate(items, start=1)],
                        documents=[item["note"] for item in items],
                        metadatas=[{"source": source} for _ in items],
                        embeddings=[embed_text(item["note"]) for item in items],
                    )
        finally:
            await client.aclose()

    payload = {
        "experiment": args.experiment,
        "semantic_seed": semantic_seed,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Seeded semantic memory manifest: {output_path}")


if __name__ == "__main__":
    asyncio.run(async_main())
