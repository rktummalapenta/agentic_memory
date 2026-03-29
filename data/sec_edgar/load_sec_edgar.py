"""Downloads and normalizes real SEC EDGAR companyfacts into SQLite."""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.download_utils import download_json, load_env_file, write_json

DB_PATH = ROOT / "data" / "sec_edgar" / "sec_edgar.db"
MANIFEST_PATH = ROOT / "data" / "sec_edgar" / "manifest.json"
TMP_DB_PATH = ROOT / "data" / "sec_edgar" / "sec_edgar.tmp.db"

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

TARGET_TICKERS = [
    "AAPL",
    "MSFT",
    "JPM",
    "NVDA",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "V",
    "XOM",
    "UNH",
    "WMT",
    "JNJ",
    "PG",
    "MA",
    "HD",
    "BAC",
    "KO",
    "PFE",
    "CSCO",
]

METRIC_CONCEPTS = {
    "revenue": {
        "concepts": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
        ],
        "units": ["USD"],
    },
    "operating_income": {
        "concepts": ["OperatingIncomeLoss"],
        "units": ["USD"],
    },
    "net_income": {
        "concepts": ["NetIncomeLoss"],
        "units": ["USD"],
    },
    "total_assets": {
        "concepts": ["Assets"],
        "units": ["USD"],
    },
    "total_liabilities": {
        "concepts": ["Liabilities"],
        "units": ["USD"],
    },
    "eps": {
        "concepts": ["EarningsPerShareDiluted", "EarningsPerShareBasic"],
        "units": ["USD/shares"],
    },
    "cash": {
        "concepts": ["CashAndCashEquivalentsAtCarryingValue"],
        "units": ["USD"],
    },
}


def main() -> None:
    load_env_file(ROOT / ".env")
    user_agent = os.getenv("SEC_USER_AGENT")
    if not user_agent:
        raise RuntimeError(
            "SEC_USER_AGENT is required. Set it in the environment or .env as 'Name email@domain'."
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tickers_payload = download_json(COMPANY_TICKERS_URL, headers={"User-Agent": user_agent})
    ticker_index = {
        entry["ticker"].upper(): entry for entry in tickers_payload.values() if "ticker" in entry
    }
    if TMP_DB_PATH.exists():
        TMP_DB_PATH.unlink()

    with sqlite3.connect(TMP_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executescript(
            """
            DROP TABLE IF EXISTS annual_financials;
            DROP TABLE IF EXISTS quarterly_financials;
            DROP TABLE IF EXISTS companies;

            CREATE TABLE companies (
                cik TEXT NOT NULL UNIQUE,
                ticker TEXT PRIMARY KEY,
                company_name TEXT NOT NULL
            );

            CREATE TABLE annual_financials (
                ticker TEXT NOT NULL,
                fiscal_year INTEGER NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                value_billions REAL,
                unit TEXT NOT NULL,
                concept TEXT NOT NULL,
                form TEXT NOT NULL,
                filed TEXT NOT NULL,
                PRIMARY KEY (ticker, fiscal_year, metric),
                FOREIGN KEY (ticker) REFERENCES companies(ticker)
            );

            CREATE TABLE quarterly_financials (
                ticker TEXT NOT NULL,
                fiscal_year INTEGER NOT NULL,
                fiscal_period TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                value_billions REAL,
                unit TEXT NOT NULL,
                concept TEXT NOT NULL,
                form TEXT NOT NULL,
                filed TEXT NOT NULL,
                PRIMARY KEY (ticker, fiscal_year, fiscal_period, metric),
                FOREIGN KEY (ticker) REFERENCES companies(ticker)
            );
            """
        )

        annual_rows: dict[tuple[str, int, str], tuple] = {}
        quarterly_rows: dict[tuple[str, int, str, str], tuple] = {}
        loaded_tickers: list[str] = []
        skipped_tickers: list[str] = []

        for index, ticker in enumerate(TARGET_TICKERS, start=1):
            company = ticker_index.get(ticker)
            if not company:
                skipped_tickers.append(ticker)
                continue
            print(f"[{index}/{len(TARGET_TICKERS)}] loading {ticker}")
            cik = str(company["cik_str"]).zfill(10)
            facts = download_json(
                COMPANY_FACTS_URL.format(cik=cik),
                headers={"User-Agent": user_agent},
            )
            cursor.execute(
                "INSERT INTO companies(cik, ticker, company_name) VALUES (?, ?, ?)",
                (cik, ticker, facts["entityName"]),
            )
            loaded_tickers.append(ticker)
            _collect_metric_rows(ticker, facts, annual_rows, quarterly_rows)
            time.sleep(0.2)

        cursor.executemany(
            """
            INSERT INTO annual_financials(
                ticker,
                fiscal_year,
                metric,
                value,
                value_billions,
                unit,
                concept,
                form,
                filed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            annual_rows.values(),
        )
        cursor.executemany(
            """
            INSERT INTO quarterly_financials(
                ticker,
                fiscal_year,
                fiscal_period,
                metric,
                value,
                value_billions,
                unit,
                concept,
                form,
                filed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            quarterly_rows.values(),
        )
        conn.commit()

    TMP_DB_PATH.replace(DB_PATH)
    write_json(
        MANIFEST_PATH,
        {
            "source": COMPANY_FACTS_URL,
            "tickers_loaded": loaded_tickers,
            "skipped_tickers": skipped_tickers,
            "annual_row_count": len(annual_rows),
            "quarterly_row_count": len(quarterly_rows),
            "metrics": sorted(METRIC_CONCEPTS.keys()),
        },
    )


def _collect_metric_rows(
    ticker: str,
    facts: dict,
    annual_rows: dict[tuple[str, int, str], tuple],
    quarterly_rows: dict[tuple[str, int, str, str], tuple],
) -> None:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    for metric, config in METRIC_CONCEPTS.items():
        concept_name, unit_name, entries = _select_entries(us_gaap, config["concepts"], config["units"])
        if not entries:
            continue
        for entry in entries:
            fy = entry.get("fy")
            form = entry.get("form", "")
            filed = entry.get("filed", "")
            if not isinstance(fy, int) or not filed:
                continue
            value = entry.get("val")
            if value is None:
                continue
            numeric_value = float(value)
            value_billions = _to_billions(numeric_value, unit_name)
            if _is_annual_form(form):
                key = (ticker, fy, metric)
                row = (
                    ticker,
                    fy,
                    metric,
                    numeric_value,
                    value_billions,
                    unit_name,
                    concept_name,
                    form,
                    filed,
                )
                _keep_latest_row(annual_rows, key, row, filed_index=8)
            elif _is_quarterly_form(form):
                fiscal_period = entry.get("fp")
                if not fiscal_period:
                    continue
                key = (ticker, fy, fiscal_period, metric)
                row = (
                    ticker,
                    fy,
                    fiscal_period,
                    metric,
                    numeric_value,
                    value_billions,
                    unit_name,
                    concept_name,
                    form,
                    filed,
                )
                _keep_latest_row(quarterly_rows, key, row, filed_index=9)


def _select_entries(us_gaap: dict, concepts: list[str], preferred_units: list[str]) -> tuple[str, str, list[dict]]:
    for concept in concepts:
        concept_payload = us_gaap.get(concept)
        if not concept_payload:
            continue
        units = concept_payload.get("units", {})
        for unit in preferred_units:
            if unit in units:
                return concept, unit, units[unit]
    return "", "", []


def _keep_latest_row(target: dict, key: tuple, row: tuple, filed_index: int) -> None:
    existing = target.get(key)
    if existing is None or row[filed_index] > existing[filed_index]:
        target[key] = row


def _is_annual_form(form: str) -> bool:
    return form.startswith(("10-K", "20-F", "40-F"))


def _is_quarterly_form(form: str) -> bool:
    return form.startswith("10-Q")


def _to_billions(value: float, unit: str) -> float | None:
    if unit != "USD":
        return None
    return value / 1_000_000_000


if __name__ == "__main__":
    main()
