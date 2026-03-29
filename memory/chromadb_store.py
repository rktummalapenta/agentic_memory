"""ChromaDB v2 HTTP adapter with a local fallback store."""

from __future__ import annotations

import asyncio
import json
import math
import os
from collections import defaultdict
from hashlib import sha256
from typing import Any

import httpx


class ChromaMemoryStore:
    def __init__(
        self,
        namespace: str,
        semantic_seed: dict[str, list[dict[str, str]]] | None = None,
        collection_name: str | None = None,
        base_url: str | None = None,
        tenant: str | None = None,
        database: str | None = None,
        timeout_seconds: float = 2.0,
        force_fallback: bool = False,
    ) -> None:
        self.namespace = namespace
        self.collection_name = collection_name or f"{namespace}_episodic"
        self.semantic_seed = semantic_seed or {}
        self._fallback_episodes: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.client = ChromaHttpClient(
            base_url=base_url or os.getenv("CHROMA_BASE_URL", "http://127.0.0.1:8000"),
            tenant=tenant or os.getenv("CHROMA_TENANT", "default_tenant"),
            database=database or os.getenv("CHROMA_DATABASE", "default_database"),
            timeout_seconds=timeout_seconds,
            enabled=not force_fallback,
        )

    async def add_episode(self, session_id: str, payload: dict[str, Any]) -> None:
        if await self.client.ensure_enabled():
            document = json.dumps(payload, sort_keys=True)
            metadata = {
                "session_id": session_id,
                "turn_number": payload["turn_number"],
                "question": payload["question"],
                **payload.get("state_updates", {}),
            }
            await self.client.add_records(
                collection_name=self.collection_name,
                ids=[f"{session_id}-turn-{payload['turn_number']}"],
                documents=[document],
                metadatas=[metadata],
                embeddings=[embed_text(payload["question"])],
            )
            return
        self._fallback_episodes[session_id].append(payload)

    async def resolve_context(
        self, session_id: str, question: str, required_keys: list[str]
    ) -> dict[str, Any]:
        episodes = await self.retrieve_episodes(
            session_id, question, top_k=max(8, len(required_keys))
        )
        resolved = extract_context_from_metadatas(
            required_keys,
            [episode.get("metadata", {}) for episode in episodes],
        )
        if resolved:
            return resolved

        resolved = {}
        for payload in reversed(self._fallback_episodes.get(session_id, [])):
            state = payload.get("state_updates", {})
            for key in required_keys:
                if key in state and key not in resolved:
                    resolved[key] = state[key]
            if len(resolved) == len(required_keys):
                break
        return resolved

    async def retrieve_episodes(
        self, session_id: str, question: str, top_k: int = 3
    ) -> list[dict[str, Any]]:
        if await self.client.ensure_enabled():
            results = await self.client.query(
                collection_name=self.collection_name,
                query_embedding=embed_text(question),
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
                where={"session_id": session_id},
            )
            documents = flatten_query_field(results, "documents")
            metadatas = flatten_query_field(results, "metadatas")
            distances = flatten_query_field(results, "distances")
            episodes: list[dict[str, Any]] = []
            for index, document in enumerate(documents):
                try:
                    payload = json.loads(document)
                except (TypeError, json.JSONDecodeError):
                    payload = {"raw_document": document}
                metadata = metadatas[index] if index < len(metadatas) else {}
                distance = distances[index] if index < len(distances) else None
                episodes.append(
                    {
                        "payload": payload,
                        "metadata": metadata if isinstance(metadata, dict) else {},
                        "distance": distance,
                    }
                )
            if episodes:
                return episodes

        return [
            {
                "payload": payload,
                "metadata": payload.get("state_updates", {}),
                "distance": None,
            }
            for payload in self._fallback_episodes.get(session_id, [])[-top_k:]
        ][::-1]

    async def retrieve_semantic_notes(
        self, source: str, question: str, top_k: int = 2
    ) -> list[str]:
        semantic_collection = f"{self.namespace}_{source}"
        if await self.client.ensure_enabled():
            results = await self.client.query(
                collection_name=semantic_collection,
                query_embedding=embed_text(question),
                n_results=top_k,
                include=["documents"],
            )
            documents = flatten_query_field(results, "documents")
            if documents:
                return [str(document) for document in documents[:top_k]]
        return [item["note"] for item in self.semantic_seed.get(source, [])[:top_k]]

    async def clear_collection(self) -> None:
        if await self.client.ensure_enabled():
            await self.client.delete_collection(self.collection_name)
            return
        self._fallback_episodes.clear()

    async def aclose(self) -> None:
        await self.client.aclose()


class ChromaHttpClient:
    def __init__(
        self,
        base_url: str,
        tenant: str,
        database: str,
        timeout_seconds: float,
        enabled: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.tenant = tenant
        self.database = database
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled
        self._configured_enabled = enabled
        self._availability_checked = False
        self.collection_cache: dict[str, str] = {}
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout_seconds),
            headers={"Content-Type": "application/json"},
        )

    async def add_records(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> None:
        collection_id = await self.ensure_collection(collection_name)
        payload = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings,
        }
        await self._request(
            "POST",
            f"/collections/{collection_id}/add",
            payload=payload,
            expected_statuses={201},
        )

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int,
        include: list[str],
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        collection_id = await self.ensure_collection(collection_name)
        payload: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": include,
        }
        if where:
            payload["where"] = where
        return await self._request("POST", f"/collections/{collection_id}/query", payload=payload)

    async def ensure_collection(self, collection_name: str) -> str:
        if collection_name in self.collection_cache:
            return self.collection_cache[collection_name]
        payload = {"name": collection_name, "get_or_create": True}
        response = await self._request("POST", "/collections", payload=payload)
        collection_id = response["id"]
        self.collection_cache[collection_name] = collection_id
        return collection_id

    async def list_collections(self) -> list[dict[str, Any]]:
        response = await self._request("GET", "/collections?limit=1000&offset=0")
        return list(response)

    async def delete_collection(self, collection_name: str) -> bool:
        collection_id = self.collection_cache.get(collection_name)
        if collection_id is None:
            for collection in await self.list_collections():
                if collection.get("name") == collection_name:
                    collection_id = collection["id"]
                    break
        if collection_id is None:
            return False
        try:
            await self._request("DELETE", f"/collections/{collection_id}")
        except OSError:
            self.collection_cache.pop(collection_name, None)
            return False
        self.collection_cache.pop(collection_name, None)
        return True

    async def ensure_enabled(self) -> bool:
        if not self._configured_enabled:
            self.enabled = False
            return False
        if self._availability_checked:
            return self.enabled
        self.enabled = await self._heartbeat()
        self._availability_checked = True
        return self.enabled

    async def ping(self) -> bool:
        return await self.ensure_enabled()

    async def _heartbeat(self) -> bool:
        try:
            response = await self._client.get(f"{self.base_url}/api/v2/heartbeat")
            response.raise_for_status()
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        expected_statuses: set[int] | None = None,
    ) -> Any:
        expected = expected_statuses or {200}
        url = f"{self.base_url}/api/v2/tenants/{self.tenant}/databases/{self.database}{path}"
        try:
            response = await self._client.request(method, url, json=payload)
            if response.status_code not in expected:
                raise OSError(f"Unexpected Chroma status {response.status_code} for {url}")
            return response.json() if response.content else {}
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            raise OSError(f"Chroma request failed: {exc}") from exc

    async def aclose(self) -> None:
        await self._client.aclose()


def embed_text(text: str, dimensions: int = 16) -> list[float]:
    vector = [0.0] * dimensions
    tokens = [token for token in text.lower().split() if token]
    if not tokens:
        return vector
    for token in tokens:
        digest = sha256(token.encode("utf-8")).digest()
        for index in range(dimensions):
            vector[index] += digest[index] / 255.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


def flatten_query_field(query_response: dict[str, Any], field: str) -> list[Any]:
    values = query_response.get(field) or []
    if not values:
        return []
    flattened: list[Any] = []
    for group in values:
        flattened.extend(group or [])
    return flattened


def extract_context_from_metadatas(required_keys: list[str], metadatas: list[Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for metadata in metadatas:
        if not isinstance(metadata, dict):
            continue
        for key in required_keys:
            if key in metadata and key not in resolved:
                resolved[key] = metadata[key]
        if len(resolved) == len(required_keys):
            break
    return resolved
