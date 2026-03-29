"""Builds the canonical benchmark session file from the local SQLite datasets."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SESSIONS_PATH = ROOT / "data" / "sessions" / "all_sessions.json"
SEMANTIC_MEMORY_PATH = ROOT / "data" / "sessions" / "semantic_memory.json"

NORTHWIND_DB = ROOT / "data" / "northwind" / "northwind.db"
SEC_DB = ROOT / "data" / "sec_edgar" / "sec_edgar.db"
BIRD_DB = ROOT / "data" / "bird" / "bird.db"

SESSION_TARGETS = {
    "northwind": {1: 30, 2: 40, 3: 30},
    "sec_edgar": {1: 30, 2: 50, 3: 40},
    "bird": {1: 30, 2: 30, 3: 20},
}

T3_TEN_TURN_SESSIONS = {
    "northwind": 7,
    "sec_edgar": 9,
    "bird": 4,
}

ORDER_VALUE_EXPR = "od.UnitPrice * od.Quantity * (1 - od.Discount)"
BIRD_OWNER_JOIN = (
    "FROM loan l "
    "JOIN account a ON a.account_id = l.account_id "
    "JOIN disp dp ON dp.account_id = a.account_id AND dp.type = 'OWNER' "
    "JOIN client c ON c.client_id = dp.client_id "
    "JOIN district d ON d.district_id = c.district_id "
)


def build_sessions(target_sessions: int = 300) -> list[dict]:
    sessions = (
        _build_northwind_sessions()
        + _build_sec_sessions()
        + _build_bird_sessions()
    )
    _validate_session_inventory(sessions)
    if target_sessions < len(sessions):
        return sessions[:target_sessions]
    return sessions


def semantic_memory() -> dict[str, list[dict[str, str]]]:
    return {
        "northwind": [
            {"note": "Orders joins to [Order Details] by OrderID and to Customers by CustomerID"},
            {"note": "Sales totals come from UnitPrice * Quantity * (1 - Discount) on [Order Details]"},
        ],
        "sec_edgar": [
            {"note": "annual_financials contains ticker, fiscal_year, metric, and value_billions"},
            {"note": "revenue is stored as metric='revenue' and year comparisons use fiscal_year"},
        ],
        "bird": [
            {"note": "loan joins to account by account_id; account joins client through disp where type='OWNER'"},
            {"note": "district.A3 stores the region name, and loan.status uses the raw BIRD codes A, B, C, D"},
        ],
    }


def _build_northwind_sessions() -> list[dict]:
    profiles = _northwind_profiles()
    sessions: list[dict] = []

    for index in range(SESSION_TARGETS["northwind"][1]):
        profile = profiles[index]
        sessions.append(
            _make_session(
                prefix="NW",
                source="northwind",
                tier=1,
                index=index + 1,
                turns=_northwind_t1_turns(profile),
            )
        )

    for index in range(SESSION_TARGETS["northwind"][2]):
        profile = profiles[index]
        fallback = profiles[(index + 1) % len(profiles)]
        sessions.append(
            _make_session(
                prefix="NW",
                source="northwind",
                tier=2,
                index=index + 1,
                turns=_northwind_t2_turns(profile, fallback),
            )
        )

    for index in range(SESSION_TARGETS["northwind"][3]):
        profile = profiles[index]
        fallback = profiles[(index + 1) % len(profiles)]
        turn_count = 10 if index < T3_TEN_TURN_SESSIONS["northwind"] else 9
        sessions.append(
            _make_session(
                prefix="NW",
                source="northwind",
                tier=3,
                index=index + 1,
                turns=_northwind_t3_turns(profile, fallback, turn_count),
            )
        )

    return sessions


def _build_sec_sessions() -> list[dict]:
    t2_profiles, t3_profiles = _sec_profiles()
    sessions: list[dict] = []

    for index in range(SESSION_TARGETS["sec_edgar"][1]):
        profile = t2_profiles[index % len(t2_profiles)]
        sessions.append(
            _make_session(
                prefix="SEC",
                source="sec_edgar",
                tier=1,
                index=index + 1,
                turns=_sec_t1_turns(profile),
            )
        )

    for index in range(SESSION_TARGETS["sec_edgar"][2]):
        profile = t2_profiles[index % len(t2_profiles)]
        fallback = t2_profiles[(index + 1) % len(t2_profiles)]
        sessions.append(
            _make_session(
                prefix="SEC",
                source="sec_edgar",
                tier=2,
                index=index + 1,
                turns=_sec_t2_turns(profile, fallback),
            )
        )

    for index in range(SESSION_TARGETS["sec_edgar"][3]):
        profile = t3_profiles[index % len(t3_profiles)]
        fallback = t3_profiles[(index + 1) % len(t3_profiles)]
        turn_count = 10 if index < T3_TEN_TURN_SESSIONS["sec_edgar"] else 9
        sessions.append(
            _make_session(
                prefix="SEC",
                source="sec_edgar",
                tier=3,
                index=index + 1,
                turns=_sec_t3_turns(profile, fallback, turn_count),
            )
        )

    return sessions


def _build_bird_sessions() -> list[dict]:
    combos = _bird_profiles()
    sessions: list[dict] = []

    for index in range(SESSION_TARGETS["bird"][1]):
        combo = combos[index % len(combos)]
        sessions.append(
            _make_session(
                prefix="BIRD",
                source="bird",
                tier=1,
                index=index + 1,
                turns=_bird_t1_turns(combo),
            )
        )

    for index in range(SESSION_TARGETS["bird"][2]):
        combo = combos[index % len(combos)]
        fallback = combos[(index + 1) % len(combos)]
        sessions.append(
            _make_session(
                prefix="BIRD",
                source="bird",
                tier=2,
                index=index + 1,
                turns=_bird_t2_turns(combo, fallback),
            )
        )

    for index in range(SESSION_TARGETS["bird"][3]):
        combo = combos[index % len(combos)]
        fallback = combos[(index + 1) % len(combos)]
        turn_count = 10 if index < T3_TEN_TURN_SESSIONS["bird"] else 9
        sessions.append(
            _make_session(
                prefix="BIRD",
                source="bird",
                tier=3,
                index=index + 1,
                turns=_bird_t3_turns(combo, fallback, turn_count),
            )
        )

    return sessions


def _northwind_profiles() -> list[dict[str, str]]:
    with sqlite3.connect(NORTHWIND_DB) as conn:
        rows = conn.execute(
            """
            SELECT
                o.CustomerID,
                c.CompanyName,
                strftime('%Y', o.OrderDate) AS order_year,
                COUNT(DISTINCT o.OrderID) AS order_count
            FROM Orders o
            JOIN Customers c ON c.CustomerID = o.CustomerID
            WHERE o.CustomerID IS NOT NULL
            GROUP BY o.CustomerID, c.CompanyName, order_year
            """
        ).fetchall()

    years_by_customer: dict[str, list[str]] = defaultdict(list)
    company_by_customer: dict[str, str] = {}
    orders_by_customer: Counter[str] = Counter()
    for customer_id, company_name, order_year, order_count in rows:
        company_by_customer[customer_id] = company_name
        years_by_customer[customer_id].append(order_year)
        orders_by_customer[customer_id] += int(order_count)

    profiles: list[dict[str, str]] = []
    for customer_id, total_orders in orders_by_customer.most_common():
        years = sorted(set(years_by_customer[customer_id]))
        if len(years) < 2:
            continue
        profiles.append(
            {
                "customer_id": customer_id,
                "company_name": company_by_customer[customer_id],
                "focus_year": years[-1],
                "previous_year": years[-2],
            }
        )
    if len(profiles) < 40:
        raise RuntimeError("Not enough Northwind customer profiles to build the benchmark.")
    return profiles


def _sec_profiles() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    with sqlite3.connect(SEC_DB) as conn:
        company_rows = conn.execute(
            "SELECT ticker, company_name FROM companies ORDER BY ticker"
        ).fetchall()
        fact_rows = conn.execute(
            """
            SELECT ticker, metric, fiscal_year
            FROM annual_financials
            WHERE metric IN (
                'revenue',
                'net_income',
                'cash',
                'total_assets',
                'total_liabilities'
            )
            AND value_billions IS NOT NULL
            """
        ).fetchall()

    company_names = {ticker: name for ticker, name in company_rows}
    years_by_ticker: dict[str, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
    for ticker, metric, fiscal_year in fact_rows:
        years_by_ticker[ticker][metric].add(int(fiscal_year))

    t2_profiles: list[dict[str, object]] = []
    t3_profiles: list[dict[str, object]] = []
    for ticker in sorted(company_names):
        t2_years = sorted(
            years_by_ticker[ticker]["revenue"] & years_by_ticker[ticker]["net_income"]
        )
        if len(t2_years) >= 2:
            t2_profiles.append(
                {
                    "ticker": ticker,
                    "company_name": company_names[ticker],
                    "older_year": t2_years[-2],
                    "newer_year": t2_years[-1],
                }
            )

        t3_years = sorted(
            years_by_ticker[ticker]["revenue"]
            & years_by_ticker[ticker]["net_income"]
            & years_by_ticker[ticker]["cash"]
            & years_by_ticker[ticker]["total_assets"]
            & years_by_ticker[ticker]["total_liabilities"]
        )
        if len(t3_years) >= 2:
            t3_profiles.append(
                {
                    "ticker": ticker,
                    "company_name": company_names[ticker],
                    "older_year": t3_years[-2],
                    "newer_year": t3_years[-1],
                }
            )

    if len(t2_profiles) < 10 or len(t3_profiles) < 10:
        raise RuntimeError("Not enough SEC profiles to build the benchmark.")
    return t2_profiles, t3_profiles


def _bird_profiles() -> list[dict[str, object]]:
    with sqlite3.connect(BIRD_DB) as conn:
        rows = conn.execute(
            f"""
            SELECT d.A3 AS region, l.status, COUNT(*) AS loan_count
            {BIRD_OWNER_JOIN}
            GROUP BY d.A3, l.status
            HAVING COUNT(*) > 0
            ORDER BY loan_count DESC, region, l.status
            """
        ).fetchall()

    combos = [
        {"region": region, "loan_status": loan_status, "loan_count": loan_count}
        for region, loan_status, loan_count in rows
    ]
    if len(combos) < 20:
        raise RuntimeError("Not enough BIRD region/status combinations to build the benchmark.")
    return combos


def _northwind_t1_turns(profile: dict[str, str]) -> list[dict]:
    return [
        {
            "turn_number": 1,
            "question": f"Show {profile['company_name']} sales for {profile['focus_year']}.",
            "ground_truth_sql": (
                "SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {},
            "source": "northwind",
        }
    ]


def _northwind_t2_turns(profile: dict[str, str], fallback: dict[str, str]) -> list[dict]:
    return [
        {
            "turn_number": 1,
            "question": f"Show {profile['company_name']} sales by year.",
            "ground_truth_sql": (
                "SELECT strftime('%Y', o.OrderDate) AS order_year, "
                f"ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                "GROUP BY order_year ORDER BY order_year"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {
                "customer_id": profile["customer_id"],
                "company_name": profile["company_name"],
            },
            "source": "northwind",
        },
        {
            "turn_number": 2,
            "question": "Which year was highest?",
            "ground_truth_sql": (
                "SELECT strftime('%Y', o.OrderDate) AS order_year "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                "GROUP BY order_year "
                f"ORDER BY SUM({ORDER_VALUE_EXPR}) DESC, order_year DESC LIMIT 1"
            ),
            "sql_template": (
                "SELECT strftime('%Y', o.OrderDate) AS order_year "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                "GROUP BY order_year "
                f"ORDER BY SUM({ORDER_VALUE_EXPR}) DESC, order_year DESC LIMIT 1"
            ),
            "fallback_sql": (
                "SELECT strftime('%Y', o.OrderDate) AS order_year "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                "GROUP BY order_year "
                f"ORDER BY SUM({ORDER_VALUE_EXPR}) DESC, order_year DESC LIMIT 1"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 3,
            "question": f"Now focus on {profile['focus_year']} for that customer and show the sales total.",
            "ground_truth_sql": (
                f"SELECT ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                f"SELECT ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "fallback_sql": (
                f"SELECT ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id"],
            "state_updates": {"focus_year": profile["focus_year"]},
            "source": "northwind",
        },
        {
            "turn_number": 4,
            "question": "How many orders did that customer place in that year?",
            "ground_truth_sql": (
                "SELECT COUNT(DISTINCT o.OrderID) AS order_count "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                "SELECT COUNT(DISTINCT o.OrderID) AS order_count "
                "FROM Orders o "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                "SELECT COUNT(DISTINCT o.OrderID) AS order_count "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
    ]


def _northwind_t3_turns(
    profile: dict[str, str], fallback: dict[str, str], turn_count: int
) -> list[dict]:
    turns = [
        {
            "turn_number": 1,
            "question": f"Show {profile['company_name']} sales by year.",
            "ground_truth_sql": (
                "SELECT strftime('%Y', o.OrderDate) AS order_year, "
                f"ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                "GROUP BY order_year ORDER BY order_year"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {
                "customer_id": profile["customer_id"],
                "company_name": profile["company_name"],
            },
            "source": "northwind",
        },
        {
            "turn_number": 2,
            "question": f"Now focus on {profile['focus_year']} for that customer and show the sales total.",
            "ground_truth_sql": (
                f"SELECT ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                f"SELECT ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "fallback_sql": (
                f"SELECT ROUND(SUM({ORDER_VALUE_EXPR}), 2) AS sales_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id"],
            "state_updates": {"focus_year": profile["focus_year"]},
            "source": "northwind",
        },
        {
            "turn_number": 3,
            "question": "How many orders did that customer place in that year?",
            "ground_truth_sql": (
                "SELECT COUNT(DISTINCT o.OrderID) AS order_count "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                "SELECT COUNT(DISTINCT o.OrderID) AS order_count "
                "FROM Orders o "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                "SELECT COUNT(DISTINCT o.OrderID) AS order_count "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 4,
            "question": "What was total freight for that year?",
            "ground_truth_sql": (
                "SELECT ROUND(SUM(o.Freight), 2) AS freight_total "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                "SELECT ROUND(SUM(o.Freight), 2) AS freight_total "
                "FROM Orders o "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                "SELECT ROUND(SUM(o.Freight), 2) AS freight_total "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 5,
            "question": "What was the average order subtotal for that year?",
            "ground_truth_sql": (
                "SELECT ROUND(AVG(order_total), 2) AS avg_order_total "
                "FROM ("
                "SELECT o.OrderID, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}' "
                "GROUP BY o.OrderID"
                ")"
            ),
            "sql_template": (
                "SELECT ROUND(AVG(order_total), 2) AS avg_order_total "
                "FROM ("
                "SELECT o.OrderID, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}' "
                "GROUP BY o.OrderID"
                ")"
            ),
            "fallback_sql": (
                "SELECT ROUND(AVG(order_total), 2) AS avg_order_total "
                "FROM ("
                "SELECT o.OrderID, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}' "
                "GROUP BY o.OrderID"
                ")"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 6,
            "question": "What was the largest line-item value for that year?",
            "ground_truth_sql": (
                f"SELECT ROUND(MAX({ORDER_VALUE_EXPR}), 2) AS max_line_value "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                f"SELECT ROUND(MAX({ORDER_VALUE_EXPR}), 2) AS max_line_value "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                f"SELECT ROUND(MAX({ORDER_VALUE_EXPR}), 2) AS max_line_value "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 7,
            "question": "What was the smallest line-item value for that year?",
            "ground_truth_sql": (
                f"SELECT ROUND(MIN({ORDER_VALUE_EXPR}), 2) AS min_line_value "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                f"SELECT ROUND(MIN({ORDER_VALUE_EXPR}), 2) AS min_line_value "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                f"SELECT ROUND(MIN({ORDER_VALUE_EXPR}), 2) AS min_line_value "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 8,
            "question": "How many distinct products were ordered that year?",
            "ground_truth_sql": (
                "SELECT COUNT(DISTINCT od.ProductID) AS product_count "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                "SELECT COUNT(DISTINCT od.ProductID) AS product_count "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                "SELECT COUNT(DISTINCT od.ProductID) AS product_count "
                "FROM Orders o "
                "JOIN [Order Details] od ON od.OrderID = o.OrderID "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
        {
            "turn_number": 9,
            "question": "What was the last order date in that year?",
            "ground_truth_sql": (
                "SELECT MAX(o.OrderDate) AS last_order_date "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{profile['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}'"
            ),
            "sql_template": (
                "SELECT MAX(o.OrderDate) AS last_order_date "
                "FROM Orders o "
                "WHERE o.CustomerID = '{customer_id}' "
                "AND strftime('%Y', o.OrderDate) = '{focus_year}'"
            ),
            "fallback_sql": (
                "SELECT MAX(o.OrderDate) AS last_order_date "
                "FROM Orders o "
                f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}'"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["customer_id", "focus_year"],
            "state_updates": {},
            "source": "northwind",
        },
    ]

    if turn_count == 10:
        turns.append(
            {
                "turn_number": 10,
                "question": "Which employee handled the most orders for that customer in that year?",
                "ground_truth_sql": (
                    "SELECT e.LastName, e.FirstName, COUNT(*) AS order_count "
                    "FROM Orders o "
                    "JOIN Employees e ON e.EmployeeID = o.EmployeeID "
                    f"WHERE o.CustomerID = '{profile['customer_id']}' "
                    f"AND strftime('%Y', o.OrderDate) = '{profile['focus_year']}' "
                    "GROUP BY e.EmployeeID, e.LastName, e.FirstName "
                    "ORDER BY order_count DESC, e.LastName, e.FirstName LIMIT 1"
                ),
                "sql_template": (
                    "SELECT e.LastName, e.FirstName, COUNT(*) AS order_count "
                    "FROM Orders o "
                    "JOIN Employees e ON e.EmployeeID = o.EmployeeID "
                    "WHERE o.CustomerID = '{customer_id}' "
                    "AND strftime('%Y', o.OrderDate) = '{focus_year}' "
                    "GROUP BY e.EmployeeID, e.LastName, e.FirstName "
                    "ORDER BY order_count DESC, e.LastName, e.FirstName LIMIT 1"
                ),
                "fallback_sql": (
                    "SELECT e.LastName, e.FirstName, COUNT(*) AS order_count "
                    "FROM Orders o "
                    "JOIN Employees e ON e.EmployeeID = o.EmployeeID "
                    f"WHERE o.CustomerID = '{fallback['customer_id']}' "
                    f"AND strftime('%Y', o.OrderDate) = '{fallback['focus_year']}' "
                    "GROUP BY e.EmployeeID, e.LastName, e.FirstName "
                    "ORDER BY order_count DESC, e.LastName, e.FirstName LIMIT 1"
                ),
                "requires_prior_context": True,
                "memory_benefit_expected": True,
                "referenced_context_keys": ["customer_id", "focus_year"],
                "state_updates": {},
                "source": "northwind",
            }
        )

    return turns


def _sec_t1_turns(profile: dict[str, object]) -> list[dict]:
    return [
        {
            "turn_number": 1,
            "question": (
                f"Show {profile['company_name']} revenue for "
                f"{profile['older_year']} and {profile['newer_year']}."
            ),
            "ground_truth_sql": (
                "SELECT fiscal_year, value_billions FROM annual_financials "
                f"WHERE ticker = '{profile['ticker']}' AND metric = 'revenue' "
                f"AND fiscal_year IN ({profile['older_year']}, {profile['newer_year']}) "
                "ORDER BY fiscal_year"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {},
            "source": "sec_edgar",
        }
    ]


def _sec_metric_value_turn(
    turn_number: int,
    question: str,
    ticker: str,
    older_year: int,
    newer_year: int,
    metric: str,
    fallback_ticker: str,
    fallback_older_year: int,
    fallback_newer_year: int,
    requires_prior_context: bool,
    referenced_keys: list[str],
    state_updates: dict[str, object],
) -> dict:
    return {
        "turn_number": turn_number,
        "question": question,
        "ground_truth_sql": (
            "SELECT fiscal_year, value_billions FROM annual_financials "
            f"WHERE ticker = '{ticker}' AND metric = '{metric}' "
            f"AND fiscal_year IN ({older_year}, {newer_year}) "
            "ORDER BY fiscal_year"
        ),
        "sql_template": (
            "SELECT fiscal_year, value_billions FROM annual_financials "
            f"WHERE ticker = '{{ticker}}' AND metric = '{metric}' "
            "AND fiscal_year IN ({older_year}, {newer_year}) "
            "ORDER BY fiscal_year"
        )
        if requires_prior_context
        else None,
        "fallback_sql": (
            "SELECT fiscal_year, value_billions FROM annual_financials "
            f"WHERE ticker = '{fallback_ticker}' AND metric = '{metric}' "
            f"AND fiscal_year IN ({fallback_older_year}, {fallback_newer_year}) "
            "ORDER BY fiscal_year"
        )
        if requires_prior_context
        else None,
        "requires_prior_context": requires_prior_context,
        "memory_benefit_expected": requires_prior_context,
        "referenced_context_keys": referenced_keys if requires_prior_context else [],
        "state_updates": state_updates,
        "source": "sec_edgar",
    }


def _sec_metric_compare_turn(
    turn_number: int,
    question: str,
    ticker: str,
    older_year: int,
    newer_year: int,
    metric: str,
    fallback_ticker: str,
    fallback_older_year: int,
    fallback_newer_year: int,
) -> dict:
    return {
        "turn_number": turn_number,
        "question": question,
        "ground_truth_sql": (
            "SELECT fiscal_year FROM annual_financials "
            f"WHERE ticker = '{ticker}' AND metric = '{metric}' "
            f"AND fiscal_year IN ({older_year}, {newer_year}) "
            "ORDER BY value_billions DESC, fiscal_year DESC LIMIT 1"
        ),
        "sql_template": (
            "SELECT fiscal_year FROM annual_financials "
            "WHERE ticker = '{ticker}' AND metric = '{metric}' "
            "AND fiscal_year IN ({older_year}, {newer_year}) "
            "ORDER BY value_billions DESC, fiscal_year DESC LIMIT 1"
        ),
        "fallback_sql": (
            "SELECT fiscal_year FROM annual_financials "
            f"WHERE ticker = '{fallback_ticker}' AND metric = '{metric}' "
            f"AND fiscal_year IN ({fallback_older_year}, {fallback_newer_year}) "
            "ORDER BY value_billions DESC, fiscal_year DESC LIMIT 1"
        ),
        "requires_prior_context": True,
        "memory_benefit_expected": True,
        "referenced_context_keys": ["ticker", "metric", "older_year", "newer_year"],
        "state_updates": {},
        "source": "sec_edgar",
    }


def _sec_t2_turns(profile: dict[str, object], fallback: dict[str, object]) -> list[dict]:
    ticker = str(profile["ticker"])
    older_year = int(profile["older_year"])
    newer_year = int(profile["newer_year"])
    fallback_ticker = str(fallback["ticker"])
    fallback_older_year = int(fallback["older_year"])
    fallback_newer_year = int(fallback["newer_year"])

    turns = [
        {
            "turn_number": 1,
            "question": (
                f"Show {profile['company_name']} revenue for "
                f"{older_year} and {newer_year}."
            ),
            "ground_truth_sql": (
                "SELECT fiscal_year, value_billions FROM annual_financials "
                f"WHERE ticker = '{ticker}' AND metric = 'revenue' "
                f"AND fiscal_year IN ({older_year}, {newer_year}) "
                "ORDER BY fiscal_year"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {
                "ticker": ticker,
                "company_name": profile["company_name"],
                "metric": "revenue",
                "older_year": older_year,
                "newer_year": newer_year,
            },
            "source": "sec_edgar",
        },
        _sec_metric_compare_turn(
            turn_number=2,
            question="Which year was higher?",
            ticker=ticker,
            older_year=older_year,
            newer_year=newer_year,
            metric="revenue",
            fallback_ticker=fallback_ticker,
            fallback_older_year=fallback_older_year,
            fallback_newer_year=fallback_newer_year,
        ),
        _sec_metric_value_turn(
            turn_number=3,
            question="Now show net income for those same years.",
            ticker=ticker,
            older_year=older_year,
            newer_year=newer_year,
            metric="net_income",
            fallback_ticker=fallback_ticker,
            fallback_older_year=fallback_older_year,
            fallback_newer_year=fallback_newer_year,
            requires_prior_context=True,
            referenced_keys=["ticker", "older_year", "newer_year"],
            state_updates={"metric": "net_income"},
        ),
        _sec_metric_compare_turn(
            turn_number=4,
            question="Which year was higher there?",
            ticker=ticker,
            older_year=older_year,
            newer_year=newer_year,
            metric="net_income",
            fallback_ticker=fallback_ticker,
            fallback_older_year=fallback_older_year,
            fallback_newer_year=fallback_newer_year,
        ),
    ]
    return turns


def _sec_t3_turns(
    profile: dict[str, object], fallback: dict[str, object], turn_count: int
) -> list[dict]:
    ticker = str(profile["ticker"])
    older_year = int(profile["older_year"])
    newer_year = int(profile["newer_year"])
    fallback_ticker = str(fallback["ticker"])
    fallback_older_year = int(fallback["older_year"])
    fallback_newer_year = int(fallback["newer_year"])

    turns = [
        {
            "turn_number": 1,
            "question": (
                f"Show {profile['company_name']} revenue for "
                f"{older_year} and {newer_year}."
            ),
            "ground_truth_sql": (
                "SELECT fiscal_year, value_billions FROM annual_financials "
                f"WHERE ticker = '{ticker}' AND metric = 'revenue' "
                f"AND fiscal_year IN ({older_year}, {newer_year}) "
                "ORDER BY fiscal_year"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {
                "ticker": ticker,
                "company_name": profile["company_name"],
                "metric": "revenue",
                "older_year": older_year,
                "newer_year": newer_year,
            },
            "source": "sec_edgar",
        },
        _sec_metric_compare_turn(
            2,
            "Which year was higher?",
            ticker,
            older_year,
            newer_year,
            "revenue",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
        ),
        _sec_metric_value_turn(
            3,
            "Now show net income for those same years.",
            ticker,
            older_year,
            newer_year,
            "net_income",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
            True,
            ["ticker", "older_year", "newer_year"],
            {"metric": "net_income"},
        ),
        _sec_metric_compare_turn(
            4,
            "Which year was higher there?",
            ticker,
            older_year,
            newer_year,
            "net_income",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
        ),
        _sec_metric_value_turn(
            5,
            "Now show cash for those same years.",
            ticker,
            older_year,
            newer_year,
            "cash",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
            True,
            ["ticker", "older_year", "newer_year"],
            {"metric": "cash"},
        ),
        _sec_metric_compare_turn(
            6,
            "Which year was higher there?",
            ticker,
            older_year,
            newer_year,
            "cash",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
        ),
        _sec_metric_value_turn(
            7,
            "Now show total assets for those same years.",
            ticker,
            older_year,
            newer_year,
            "total_assets",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
            True,
            ["ticker", "older_year", "newer_year"],
            {"metric": "total_assets"},
        ),
        _sec_metric_compare_turn(
            8,
            "Which year was higher there?",
            ticker,
            older_year,
            newer_year,
            "total_assets",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
        ),
        _sec_metric_value_turn(
            9,
            "Now show total liabilities for those same years.",
            ticker,
            older_year,
            newer_year,
            "total_liabilities",
            fallback_ticker,
            fallback_older_year,
            fallback_newer_year,
            True,
            ["ticker", "older_year", "newer_year"],
            {"metric": "total_liabilities"},
        ),
    ]

    turns = [turn for turn in turns if turn is not None]
    for turn in turns:
        if "sql_template" in turn and turn["sql_template"] is None:
            del turn["sql_template"]
        if "fallback_sql" in turn and turn["fallback_sql"] is None:
            del turn["fallback_sql"]

    if turn_count == 10:
        turns.append(
            _sec_metric_compare_turn(
                10,
                "Which year was higher there?",
                ticker,
                older_year,
                newer_year,
                "total_liabilities",
                fallback_ticker,
                fallback_older_year,
                fallback_newer_year,
            )
        )

    return turns


def _bird_list_query(region: str, loan_status: str | None = None) -> str:
    filters = [f"d.A3 = '{region}'"]
    if loan_status is not None:
        filters.append(f"l.status = '{loan_status}'")
    return (
        "SELECT l.loan_id, l.amount "
        f"{BIRD_OWNER_JOIN}"
        f"WHERE {' AND '.join(filters)} "
        "ORDER BY l.loan_id"
    )


def _bird_aggregate_query(region: str, loan_status: str | None, aggregate_sql: str) -> str:
    filters = [f"d.A3 = '{region}'"]
    if loan_status is not None:
        filters.append(f"l.status = '{loan_status}'")
    return f"SELECT {aggregate_sql} {BIRD_OWNER_JOIN} WHERE {' AND '.join(filters)}"


def _bird_t1_turns(combo: dict[str, object]) -> list[dict]:
    region = str(combo["region"])
    loan_status = str(combo["loan_status"])
    return [
        {
            "turn_number": 1,
            "question": f"Count status {loan_status} loans in {region}.",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "COUNT(*) AS loan_count"
            ),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {},
            "source": "bird",
        }
    ]


def _bird_t2_turns(combo: dict[str, object], fallback: dict[str, object]) -> list[dict]:
    region = str(combo["region"])
    loan_status = str(combo["loan_status"])
    fallback_region = str(fallback["region"])
    fallback_status = str(fallback["loan_status"])
    return [
        {
            "turn_number": 1,
            "question": f"List {region} status {loan_status} loans.",
            "ground_truth_sql": _bird_list_query(region, loan_status),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {"region": region, "loan_status": loan_status},
            "source": "bird",
        },
        {
            "turn_number": 2,
            "question": "Count them.",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "COUNT(*) AS loan_count"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "COUNT(*) AS loan_count"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "COUNT(*) AS loan_count"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 3,
            "question": "What is the total amount there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "SUM(l.amount) AS total_amount"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "SUM(l.amount) AS total_amount"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "SUM(l.amount) AS total_amount"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 4,
            "question": "What is the largest loan there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "MAX(l.amount) AS max_amount"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "MAX(l.amount) AS max_amount"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "MAX(l.amount) AS max_amount"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
    ]


def _bird_t3_turns(
    combo: dict[str, object], fallback: dict[str, object], turn_count: int
) -> list[dict]:
    region = str(combo["region"])
    loan_status = str(combo["loan_status"])
    fallback_region = str(fallback["region"])
    fallback_status = str(fallback["loan_status"])

    turns = [
        {
            "turn_number": 1,
            "question": f"List {region} region loans.",
            "ground_truth_sql": _bird_list_query(region),
            "requires_prior_context": False,
            "memory_benefit_expected": False,
            "state_updates": {"region": region},
            "source": "bird",
        },
        {
            "turn_number": 2,
            "question": f"Now only the status {loan_status} ones.",
            "ground_truth_sql": _bird_list_query(region, loan_status),
            "sql_template": _bird_list_query("{region}", loan_status),
            "fallback_sql": _bird_list_query(fallback_region, fallback_status),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region"],
            "state_updates": {"loan_status": loan_status},
            "source": "bird",
        },
        {
            "turn_number": 3,
            "question": "Count them.",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "COUNT(*) AS loan_count"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "COUNT(*) AS loan_count"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "COUNT(*) AS loan_count"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 4,
            "question": "What is the total amount there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "SUM(l.amount) AS total_amount"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "SUM(l.amount) AS total_amount"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "SUM(l.amount) AS total_amount"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 5,
            "question": "What is the largest loan there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "MAX(l.amount) AS max_amount"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "MAX(l.amount) AS max_amount"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "MAX(l.amount) AS max_amount"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 6,
            "question": "What is the smallest loan there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "MIN(l.amount) AS min_amount"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "MIN(l.amount) AS min_amount"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "MIN(l.amount) AS min_amount"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 7,
            "question": "What is the average loan amount there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "ROUND(AVG(l.amount), 2) AS avg_amount"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "ROUND(AVG(l.amount), 2) AS avg_amount"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "ROUND(AVG(l.amount), 2) AS avg_amount"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 8,
            "question": "What is the most recent loan date there?",
            "ground_truth_sql": _bird_aggregate_query(
                region, loan_status, "MAX(l.date) AS last_loan_date"
            ),
            "sql_template": _bird_aggregate_query(
                "{region}", "{loan_status}", "MAX(l.date) AS last_loan_date"
            ),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, fallback_status, "MAX(l.date) AS last_loan_date"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region", "loan_status"],
            "state_updates": {},
            "source": "bird",
        },
        {
            "turn_number": 9,
            "question": "Go back to the original region and show the full loan count.",
            "ground_truth_sql": _bird_aggregate_query(region, None, "COUNT(*) AS loan_count"),
            "sql_template": _bird_aggregate_query("{region}", None, "COUNT(*) AS loan_count"),
            "fallback_sql": _bird_aggregate_query(
                fallback_region, None, "COUNT(*) AS loan_count"
            ),
            "requires_prior_context": True,
            "memory_benefit_expected": True,
            "referenced_context_keys": ["region"],
            "state_updates": {},
            "source": "bird",
        },
    ]

    if turn_count == 10:
        turns.append(
            {
                "turn_number": 10,
                "question": "Use the loan table and return the number of matching rows for that region.",
                "ground_truth_sql": _bird_aggregate_query(
                    region, loan_status, "COUNT(*) AS loan_count"
                ),
                "sql_template": _bird_aggregate_query(
                    "{region}", "{loan_status}", "COUNT(*) AS loan_count"
                ),
                "fallback_sql": (
                    "SELECT COUNT(*) AS loan_count FROM district "
                    f"WHERE A3 = '{fallback_region}'"
                ),
                "requires_prior_context": True,
                "requires_semantic_memory": True,
                "memory_benefit_expected": True,
                "referenced_context_keys": ["region", "loan_status"],
                "state_updates": {},
                "source": "bird",
            }
        )

    return turns


def _make_session(prefix: str, source: str, tier: int, index: int, turns: list[dict]) -> dict:
    return {
        "session_id": f"{prefix}-{tier}-{index:03d}",
        "source": source,
        "tier": tier,
        "turns": turns,
    }


def _validate_session_inventory(sessions: list[dict]) -> None:
    expected_total = sum(
        tier_count for source_counts in SESSION_TARGETS.values() for tier_count in source_counts.values()
    )
    if len(sessions) != expected_total:
        raise RuntimeError(f"Expected {expected_total} sessions, found {len(sessions)}")

    by_source = Counter(session["source"] for session in sessions)
    by_tier = Counter(session["tier"] for session in sessions)
    turns = sum(len(session["turns"]) for session in sessions)

    if by_source != Counter(
        {source: sum(counts.values()) for source, counts in SESSION_TARGETS.items()}
    ):
        raise RuntimeError(f"Unexpected source distribution: {dict(by_source)}")

    if by_tier != Counter({1: 90, 2: 120, 3: 90}):
        raise RuntimeError(f"Unexpected tier distribution: {dict(by_tier)}")

    if turns != 1400:
        raise RuntimeError(f"Expected 1400 total turns, found {turns}")


def main() -> None:
    SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    sessions = build_sessions()
    SESSIONS_PATH.write_text(json.dumps(sessions, indent=2), encoding="utf-8")
    SEMANTIC_MEMORY_PATH.write_text(json.dumps(semantic_memory(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
