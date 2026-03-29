"""Downloads or extracts the real BIRD financial SQLite database."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.download_utils import (
    download_google_drive_file,
    list_sqlite_tables,
    load_env_file,
    temporary_directory,
    write_json,
)


RAW_DIR = ROOT / "data" / "bird" / "raw"
DB_PATH = ROOT / "data" / "bird" / "bird.db"
QUESTIONS_PATH = ROOT / "data" / "bird" / "bird_questions.json"
MANIFEST_PATH = ROOT / "data" / "bird" / "manifest.json"

BIRD_MINI_DEV_DRIVE_ID = "13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG"
EXTRACTED_MEMBERS = [
    "minidev/MINIDEV/dev_databases/financial/financial.sqlite",
    "minidev/MINIDEV/mini_dev_sqlite.json",
    "minidev/MINIDEV/dev_tables.json",
]


def main() -> None:
    load_env_file(ROOT / ".env")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    archive_override = os.getenv("BIRD_ARCHIVE_PATH")
    extracted_dir = RAW_DIR / "mini_dev"
    extract_dir = _resolve_extract_dir(extracted_dir, archive_override)
    database_path = _resolve_database_path(extract_dir, archive_override)
    if database_path != DB_PATH:
        shutil.copyfile(database_path, DB_PATH)

    question_file = _find_question_file(extract_dir) if extract_dir else None
    questions = _extract_financial_questions(question_file) if question_file else []
    QUESTIONS_PATH.write_text(json.dumps(questions, indent=2), encoding="utf-8")
    source_archive = archive_override or f"google-drive:{BIRD_MINI_DEV_DRIVE_ID}"
    if not extract_dir:
        source_archive = "recovered-local-db"

    tables = list_sqlite_tables(DB_PATH)
    write_json(
        MANIFEST_PATH,
        {
            "source_archive": source_archive,
            "question_source": str(question_file.relative_to(ROOT)) if question_file else None,
            "selected_database": str(DB_PATH.relative_to(ROOT)),
            "question_count": len(questions),
            "table_count": len(tables),
            "tables": tables,
            "extracted_members": EXTRACTED_MEMBERS if extract_dir else [],
        },
    )


def _ensure_extracted_dir(extracted_dir: Path, archive_override: str | None) -> Path:
    if extracted_dir.exists():
        shutil.rmtree(extracted_dir)

    with temporary_directory("bird_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        archive_path = Path(archive_override) if archive_override else tmp_dir / "bird_mini_dev.zip"
        if not archive_override:
            download_google_drive_file(BIRD_MINI_DEV_DRIVE_ID, archive_path)
        return _extract_required_members(archive_path, extracted_dir)


def _resolve_extract_dir(extracted_dir: Path, archive_override: str | None) -> Path | None:
    if extracted_dir.exists():
        return extracted_dir
    try:
        return _ensure_extracted_dir(extracted_dir, archive_override)
    except Exception:
        return None


def _resolve_database_path(extracted_dir: Path | None, archive_override: str | None) -> Path:
    if extracted_dir:
        try:
            return _find_financial_database(extracted_dir)
        except FileNotFoundError:
            pass
    if DB_PATH.exists():
        return DB_PATH
    refreshed_dir = _ensure_extracted_dir(RAW_DIR / "mini_dev", archive_override)
    return _find_financial_database(refreshed_dir)


def _find_financial_database(root: Path) -> Path:
    candidates = list(root.rglob("*.sqlite")) + list(root.rglob("*.db"))
    for path in candidates:
        name = path.name.lower()
        if "financial" in name:
            return path
        if "financial" in str(path.parent).lower():
            return path
    raise FileNotFoundError("Unable to locate the financial SQLite database in the BIRD archive.")


def _find_question_file(root: Path) -> Path | None:
    for path in root.rglob("*.json"):
        if "mini_dev_sqlite" in path.name.lower() or path.name.lower() == "dev.json":
            return path
    return None


def _extract_financial_questions(question_file: Path) -> list[dict]:
    payload = json.loads(question_file.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                payload = value
                break
    if not isinstance(payload, list):
        return []
    questions = [item for item in payload if str(item.get("db_id", "")).lower() == "financial"]
    return questions


def _extract_required_members(zip_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    required_suffixes = tuple(member.replace("minidev/MINIDEV", "/MINIDEV") for member in EXTRACTED_MEMBERS)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            normalized = member.replace("\\", "/")
            if normalized.endswith(required_suffixes) and not normalized.endswith("/"):
                archive.extract(member, destination_dir)
    return destination_dir


if __name__ == "__main__":
    main()
