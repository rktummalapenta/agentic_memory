"""Downloads the real Northwind SQLite database used for E0."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.download_utils import (
    download_to_file,
    extract_zip_member,
    list_sqlite_tables,
    temporary_directory,
    write_json,
)


RAW_DIR = ROOT / "data" / "northwind" / "raw"
DB_PATH = ROOT / "data" / "northwind" / "northwind.db"
MANIFEST_PATH = ROOT / "data" / "northwind" / "manifest.json"

GITHUB_ZIP_URLS = [
    "https://codeload.github.com/jpwhite3/northwind-SQLite3/zip/refs/heads/main",
    "https://codeload.github.com/jpwhite3/northwind-SQLite3/zip/refs/heads/master",
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with temporary_directory("northwind_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        zip_path = tmp_dir / "northwind.zip"

        last_error: Exception | None = None
        for url in GITHUB_ZIP_URLS:
            try:
                download_to_file(url, zip_path)
                extract_zip_member(
                    zip_path,
                    lambda member: member.lower().endswith("dist/northwind.db"),
                    DB_PATH,
                )
                tables = list_sqlite_tables(DB_PATH)
                write_json(
                    MANIFEST_PATH,
                    {
                        "source": url,
                        "database_path": str(DB_PATH.relative_to(ROOT)),
                        "table_count": len(tables),
                        "tables": tables,
                    },
                )
                return
            except Exception as exc:  # pragma: no cover - exercised in integration
                last_error = exc

        raise RuntimeError(f"Unable to download Northwind dataset: {last_error}")


if __name__ == "__main__":
    main()
