# Data Provenance

Date verified: March 14, 2026

This document records where each experiment dataset came from, how it was loaded into the local SQLite files, what local artifacts were produced, and the validation state used before running experiments.

## Experiment-Ready Snapshot

- Local validation command: `python3 scripts/validate_datasets.py`
- Validation result on March 14, 2026: all 1,400 ground-truth session turns executed successfully with 0 SQL failures and 0 empty/null results.
- Session inventory:
  - 300 sessions total
  - 100 Northwind sessions
  - 120 SEC EDGAR sessions
  - 80 BIRD sessions
  - Tier mix: T1 = 90, T2 = 120, T3 = 90
- Session artifacts:
  - `data/sessions/all_sessions.json`
  - `data/sessions/semantic_memory.json`

## Northwind

- Purpose: canonical enterprise sales schema used for Northwind experiment sessions.
- Upstream source:
  - `https://codeload.github.com/jpwhite3/northwind-SQLite3/zip/refs/heads/main`
  - Fallback: `https://codeload.github.com/jpwhite3/northwind-SQLite3/zip/refs/heads/master`
- Loader:
  - `data/northwind/load_northwind.py`
- Repro command:
  - `python3 data/northwind/load_northwind.py`
- Extraction behavior:
  - downloads the GitHub zip archive
  - extracts `dist/northwind.db`
  - writes the local SQLite to `data/northwind/northwind.db`
  - writes metadata to `data/northwind/manifest.json`
- Local artifact:
  - `data/northwind/northwind.db`
- Observed snapshot:
  - `Customers`: 93
  - `Orders`: 16,282
  - `Order Details`: 609,283
  - `Products`: 77
  - `Categories`: 8
  - `Orders.OrderDate` range: `2012-07-10 15:40:46` to `2023-10-28 00:09:48`
- Session design notes:
  - Northwind sessions use the real schema.
  - Sales totals are computed from `[Order Details]` using `UnitPrice * Quantity * (1 - Discount)`.

## SEC EDGAR

- Purpose: public-company financial analytics dataset used for real financial experiment sessions.
- Upstream sources:
  - ticker index: `https://www.sec.gov/files/company_tickers.json`
  - company facts: `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
- Loader:
  - `data/sec_edgar/load_sec_edgar.py`
- Repro command:
  - `python3 data/sec_edgar/load_sec_edgar.py`
- Load requirements:
  - `SEC_USER_AGENT` must be set in the environment or `.env`
- Load behavior:
  - fetches the SEC ticker index
  - selects 20 target companies
  - downloads companyfacts JSON for each company
  - normalizes facts into `companies`, `annual_financials`, and `quarterly_financials`
  - writes the local SQLite to `data/sec_edgar/sec_edgar.db`
  - writes metadata to `data/sec_edgar/manifest.json`
- Local artifact:
  - `data/sec_edgar/sec_edgar.db`
- Loaded ticker set:
  - `AAPL`, `MSFT`, `JPM`, `NVDA`, `GOOGL`, `AMZN`, `META`, `TSLA`, `V`, `XOM`, `UNH`, `WMT`, `JNJ`, `PG`, `MA`, `HD`, `BAC`, `KO`, `PFE`, `CSCO`
- Observed snapshot:
  - `companies`: 20
  - `annual_financials`: 1,897
  - `quarterly_financials`: 5,599
  - fiscal year range in annual data: `2009` to `2026`
- Session design notes:
  - session SQL uses `annual_financials.value_billions`
  - revenue rows are filtered with `metric = 'revenue'`

## BIRD Financial

- Purpose: published Text-to-SQL benchmark domain used for experiment sessions on real financial-relational data.
- Upstream source:
  - Google Drive archive id: `13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG`
  - archive corresponds to the BIRD mini-dev package
- Loader:
  - `data/bird/load_bird.py`
- Repro command:
  - `python3 data/bird/load_bird.py`
- Extraction behavior:
  - downloads the BIRD mini-dev archive
  - extracts only the members required for the financial benchmark subset:
    - `minidev/MINIDEV/dev_databases/financial/financial.sqlite`
    - `minidev/MINIDEV/mini_dev_sqlite.json`
    - `minidev/MINIDEV/dev_tables.json`
  - copies `financial.sqlite` to `data/bird/bird.db`
  - filters `mini_dev_sqlite.json` down to `db_id == 'financial'`
  - writes question metadata to `data/bird/bird_questions.json`
  - writes dataset metadata to `data/bird/manifest.json`
- Local artifacts:
  - `data/bird/bird.db`
  - `data/bird/bird_questions.json`
  - `data/bird/raw/mini_dev/minidev/MINIDEV/dev_databases/financial/financial.sqlite`
- Observed snapshot:
  - `account`: 4,500
  - `card`: 892
  - `client`: 5,369
  - `disp`: 5,369
  - `district`: 77
  - `loan`: 682
  - `order`: 6,471
  - `trans`: 1,056,320
  - `loan.date` range: `1993-07-05` to `1998-12-08`
  - financial question count in filtered mini-dev file: 32
- Session design notes:
  - sessions use the real ownership path `loan -> account -> disp(type='OWNER') -> client -> district`
  - region filtering uses `district.A3`
  - loan status uses raw BIRD codes `A`, `B`, `C`, `D`

## Local Validation Trail

- Session generator:
  - `python3 data/sessions/build_sessions.py`
- Dataset validation:
  - `python3 scripts/validate_datasets.py`
- Supporting manifests:
  - `data/northwind/manifest.json`
  - `data/sec_edgar/manifest.json`
  - `data/bird/manifest.json`

## Notes For Paper / Review

- Northwind and BIRD sessions were rewritten against the actual loaded SQLite schemas rather than assumed proxy schemas.
- SEC EDGAR was loaded from live SEC companyfacts data and normalized into a reproducible local SQLite snapshot.
- The BIRD loader was intentionally changed to extract only the financial subset needed for experiments. This reduces local disk pressure while preserving provenance and reproducibility.
