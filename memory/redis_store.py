"""Redis working-memory adapter with a socket implementation and fallback store."""

from __future__ import annotations

import asyncio
import json
import os
import socket
from collections import defaultdict
from typing import Any


class RedisWorkingMemoryStore:
    def __init__(
        self,
        namespace: str,
        host: str | None = None,
        port: int | None = None,
        timeout_seconds: float = 2.0,
        force_fallback: bool = False,
    ) -> None:
        self.namespace = namespace
        self.host = host or os.getenv("REDIS_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.timeout_seconds = timeout_seconds
        self.turns: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._use_socket = False if force_fallback else self._can_connect()

    def append_turn(self, session_id: str, payload: dict[str, Any]) -> None:
        if self._use_socket:
            self._execute("RPUSH", self._session_key(session_id), json.dumps(payload))
            return
        self.turns[session_id].append(payload)

    def resolve_context(
        self, session_id: str, required_keys: list[str], window_size: int
    ) -> dict[str, Any]:
        recent_turns = self.get_recent_turns(session_id, window_size)
        resolved: dict[str, Any] = {}
        for payload in reversed(recent_turns):
            state = payload.get("state_updates", {})
            for key in required_keys:
                if key in state and key not in resolved:
                    resolved[key] = state[key]
            if len(resolved) == len(required_keys):
                break
        return resolved

    def get_recent_turns(self, session_id: str, window_size: int) -> list[dict[str, Any]]:
        if self._use_socket:
            raw_items = self._execute("LRANGE", self._session_key(session_id), -window_size, -1)
            return [json.loads(item) for item in raw_items]
        return list(self.turns.get(session_id, [])[-window_size:])

    def clear_session(self, session_id: str) -> None:
        if self._use_socket:
            self._execute("DEL", self._session_key(session_id))
            return
        self.turns.pop(session_id, None)

    def clear_namespace(self) -> int:
        if self._use_socket:
            keys = self._execute("KEYS", f"{self.namespace}:*")
            if not keys:
                return 0
            deleted = self._execute("DEL", *keys)
            return int(deleted)
        deleted = len(self.turns)
        self.turns.clear()
        return deleted

    def ping(self) -> bool:
        if self._use_socket:
            return self._execute("PING") == "PONG"
        return True

    async def append_turn_async(self, session_id: str, payload: dict[str, Any]) -> None:
        await asyncio.to_thread(self.append_turn, session_id, payload)

    async def resolve_context_async(
        self, session_id: str, required_keys: list[str], window_size: int
    ) -> dict[str, Any]:
        return await asyncio.to_thread(self.resolve_context, session_id, required_keys, window_size)

    async def get_recent_turns_async(
        self, session_id: str, window_size: int
    ) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self.get_recent_turns, session_id, window_size)

    async def clear_session_async(self, session_id: str) -> None:
        await asyncio.to_thread(self.clear_session, session_id)

    async def clear_namespace_async(self) -> int:
        return await asyncio.to_thread(self.clear_namespace)

    async def ping_async(self) -> bool:
        return await asyncio.to_thread(self.ping)

    def _session_key(self, session_id: str) -> str:
        return f"{self.namespace}:{session_id}"

    def _can_connect(self) -> bool:
        try:
            return self._execute("PING") == "PONG"
        except OSError:
            return False

    def _execute(self, *parts: Any) -> Any:
        with socket.create_connection((self.host, self.port), self.timeout_seconds) as sock:
            sock.sendall(_encode_command(parts))
            return _decode_response(sock)


def _encode_command(parts: tuple[Any, ...]) -> bytes:
    encoded = [f"*{len(parts)}\r\n".encode("utf-8")]
    for part in parts:
        if isinstance(part, bytes):
            data = part
        else:
            data = str(part).encode("utf-8")
        encoded.append(f"${len(data)}\r\n".encode("utf-8"))
        encoded.append(data + b"\r\n")
    return b"".join(encoded)


def _decode_response(sock: socket.socket) -> Any:
    prefix = _read_exact(sock, 1)
    if prefix == b"+":
        return _read_line(sock)
    if prefix == b"-":
        raise OSError(_read_line(sock))
    if prefix == b":":
        return int(_read_line(sock))
    if prefix == b"$":
        size = int(_read_line(sock))
        if size == -1:
            return None
        data = _read_exact(sock, size)
        _read_exact(sock, 2)
        return data.decode("utf-8")
    if prefix == b"*":
        length = int(_read_line(sock))
        if length == -1:
            return None
        return [_decode_response(sock) for _ in range(length)]
    raise OSError(f"Unsupported Redis response prefix: {prefix!r}")


def _read_line(sock: socket.socket) -> str:
    chunks: list[bytes] = []
    while True:
        char = _read_exact(sock, 1)
        if char == b"\r":
            _read_exact(sock, 1)
            break
        chunks.append(char)
    return b"".join(chunks).decode("utf-8")


def _read_exact(sock: socket.socket, length: int) -> bytes:
    data = bytearray()
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise OSError("Redis socket closed unexpectedly")
        data.extend(chunk)
    return bytes(data)
