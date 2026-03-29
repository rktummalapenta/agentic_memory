"""Utilities for downloading and extracting real benchmark datasets."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import zipfile
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


DEFAULT_USER_AGENT = "agentic_memory/0.1 (research benchmark setup)"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def download_to_file(url: str, destination: Path, headers: dict[str, str] | None = None) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers=_headers(headers))
    with urlopen(request, timeout=120) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return destination


def download_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request = Request(url, headers=_headers(headers))
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def download_google_drive_file(file_id: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    cookie_jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie_jar))
    base_url = "https://drive.google.com/uc"

    def fetch(url: str, query: dict[str, str] | None = None) -> bytes:
        request = Request(
            f"{url}?{urlencode(query or {})}" if query else url,
            headers=_headers(),
        )
        with opener.open(request, timeout=120) as response:
            return response.read()

    payload = fetch(base_url, {"export": "download", "id": file_id})
    if _looks_like_html(payload):
        action_url, form_fields = _extract_drive_download_form(payload.decode("utf-8", errors="ignore"))
        if not action_url or not form_fields:
            raise RuntimeError("Unable to extract Google Drive confirmation form.")
        payload = fetch(action_url, form_fields)

    destination.write_bytes(payload)
    return destination


def extract_zip_member(zip_path: Path, member_matcher: callable, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            if member_matcher(member):
                with archive.open(member) as source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
                return destination
    raise FileNotFoundError(f"No matching member found in {zip_path}")


def extract_zip_tree(zip_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination_dir)
    return destination_dir


def list_sqlite_tables(db_path: Path) -> list[str]:
    import sqlite3

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    return [row[0] for row in rows]


def temporary_directory(prefix: str) -> tempfile.TemporaryDirectory[str]:
    return tempfile.TemporaryDirectory(prefix=prefix)


def _headers(headers: dict[str, str] | None = None) -> dict[str, str]:
    base = {"User-Agent": headers.get("User-Agent") if headers and headers.get("User-Agent") else os.getenv("SEC_USER_AGENT", DEFAULT_USER_AGENT)}
    if headers:
        base.update(headers)
    return base


def _looks_like_html(payload: bytes) -> bool:
    stripped = payload.lstrip().lower()
    return stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html")


def _extract_drive_confirm_token(html: str) -> str | None:
    patterns = [
        r'confirm=([0-9A-Za-z_]+)',
        r'name="confirm" value="([0-9A-Za-z_]+)"',
        r'"confirm":"([0-9A-Za-z_]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return None


def _extract_drive_download_form(html: str) -> tuple[str | None, dict[str, str]]:
    action_match = re.search(r'<form id="download-form" action="([^"]+)" method="get">', html)
    inputs = dict(
        re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]*)">', html)
    )
    if action_match:
        return action_match.group(1), inputs
    confirm = _extract_drive_confirm_token(html)
    if confirm:
        return "https://drive.google.com/uc", {"export": "download", "confirm": confirm}
    return None, {}
