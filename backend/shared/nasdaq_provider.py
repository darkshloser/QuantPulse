"""NASDAQ symbol directory provider - fetches and normalizes official NASDAQ securities list."""

import csv
import time
from io import StringIO
from typing import Any, Dict, List
from logging import getLogger

import requests

from shared.config import settings

logger = getLogger(__name__)


class NasdaqProviderError(Exception):
    """Raised when NASDAQ data fetch/parse fails."""

    pass


def fetch_nasdaq_symbols() -> List[Dict[str, Any]]:
    """
    Fetch and parse official NASDAQ symbol directory.

    Returns list of normalized symbol dicts with keys:
    - symbol: NASDAQ ticker symbol (e.g., "AAPL")
    - company_name: Security name from NASDAQ
    - market_category: NASDAQ market segment (Q, G, Z, etc.)
    - financial_status: Financial status code from NASDAQ
    - test_issue: Whether marked as test issue

    Raises NasdaqProviderError if fetch fails after retries.
    """
    logger.info("Starting NASDAQ symbol directory fetch from %s", settings.nasdaq_url)

    last_error = None
    for attempt in range(1, settings.nasdaq_retries + 1):
        try:
            return _fetch_and_parse(attempt)
        except Exception as e:
            last_error = e
            if attempt < settings.nasdaq_retries:
                wait_time = 2 ** (attempt - 1)  # 1s, 2s, 4s for 3 retries
                logger.warning(
                    "NASDAQ fetch attempt %d/%d failed: %s. Retrying in %ds...",
                    attempt,
                    settings.nasdaq_retries,
                    str(e),
                    wait_time,
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    "NASDAQ fetch failed after %d attempts. Last error: %s",
                    settings.nasdaq_retries,
                    str(e),
                )

    raise NasdaqProviderError(
        f"Failed to fetch NASDAQ symbol directory after {settings.nasdaq_retries} retries: {last_error}"
    )


def _fetch_and_parse(attempt: int) -> List[Dict[str, Any]]:
    """Fetch and parse NASDAQ directory (internal; called with retry logic)."""
    logger.debug("NASDAQ fetch attempt %d: connecting to %s", attempt, settings.nasdaq_url)

    response = requests.get(settings.nasdaq_url, timeout=settings.nasdaq_timeout)
    response.raise_for_status()

    logger.debug("NASDAQ fetch successful (%d bytes). Parsing...", len(response.text))

    # Parse pipe-delimited file
    # Expected columns: Symbol | Security Name | Market Category | Test Issue | Financial Status | ...
    symbols = []
    reader = csv.DictReader(StringIO(response.text), delimiter="|")

    if not reader.fieldnames:
        raise ValueError("NASDAQ file has no header row")

    logger.debug("NASDAQ file columns: %s", reader.fieldnames)

    for row in reader:
        # Skip empty rows
        if not row or not row.get("Symbol"):
            continue

        try:
            symbol = row.get("Symbol", "").strip()
            company_name = row.get("Security Name", "").strip()
            market_category = row.get("Market Category", "").strip()
            financial_status = row.get("Financial Status", "").strip()
            test_issue = row.get("Test Issue", "").strip().upper()
            etf_flag = row.get("ETF", "").strip().upper()

            # Skip invalid entries
            if not symbol or not company_name:
                continue

            symbols.append(
                {
                    "symbol": symbol,
                    "company_name": company_name,
                    "market_category": market_category,
                    "financial_status": financial_status,
                    "test_issue": test_issue,
                    "etf_flag": etf_flag,
                }
            )
        except (ValueError, KeyError) as e:
            logger.warning("Error parsing NASDAQ row: %s. Skipping.", e)
            continue

    logger.info("NASDAQ parser: found %d total rows", len(symbols))
    return symbols


def filter_nasdaq_symbols(raw_symbols: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Import all NASDAQ symbols (no filtering by type).

    Includes stocks, ETFs, and other instruments. All symbols are marked is_active=True
    on import, and can be filtered on retrieval based on is_active flag.

    Returns: List of dicts with keys: {symbol, company_name, market_category, financial_status, yahoo_symbol}
    """
    logger.info("Importing all NASDAQ symbols (no type filtering)")

    filtered = []
    skipped = 0

    for raw in raw_symbols:
        symbol = raw.get("symbol", "").upper()
        company_name = raw.get("company_name", "")
        market_category = raw.get("market_category", "")
        financial_status = raw.get("financial_status", "")
        test_issue = raw.get("test_issue", "N").upper()

        # Only skip test symbols marked by NASDAQ
        if test_issue == "Y":
            logger.debug("Skipping test symbol: %s", symbol)
            skipped += 1
            continue

        # Include all other symbols (stocks, ETFs, etc.)
        filtered.append(
            {
                "symbol": symbol,
                "company_name": company_name,
                "market_category": market_category,
                "financial_status": financial_status,
                "yahoo_symbol": symbol,  # Same as symbol for NASDAQ equities
            }
        )

    logger.info(
        "NASDAQ import results: %d included, %d skipped (test symbols only)",
        len(filtered),
        skipped,
    )
    return filtered


def get_nasdaq_symbols() -> List[Dict[str, Any]]:
    """
    Fetch NASDAQ symbol directory and return filtered list.

    Returns: List of dicts with keys: {symbol, company_name, market_category, financial_status, yahoo_symbol}
    Raises: NasdaqProviderError if fetch fails
    """
    raw_symbols = fetch_nasdaq_symbols()
    filtered_symbols = filter_nasdaq_symbols(raw_symbols)
    return filtered_symbols
