"""SEC ticker directory provider - fetches and normalizes official SEC securities list."""

import time
from typing import Any, Dict, List
from logging import getLogger

import requests

from shared.config import settings

logger = getLogger(__name__)


class SecProviderError(Exception):
    """Raised when SEC data fetch/parse fails."""

    pass


def fetch_sec_symbols() -> Dict[str, Any]:
    """
    Fetch official SEC company tickers JSON file.

    Returns raw parsed JSON data with structure:
    {
        "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
        "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft Corp"},
        ...
    }

    Raises SecProviderError if fetch fails after retries.
    """
    sec_url = "https://www.sec.gov/files/company_tickers.json"
    logger.info("Starting SEC ticker directory fetch from %s", sec_url)

    last_error = None
    for attempt in range(1, settings.nasdaq_retries + 1):
        try:
            return _fetch_and_parse(attempt, sec_url)
        except Exception as e:
            last_error = e
            if attempt < settings.nasdaq_retries:
                wait_time = 2 ** (attempt - 1)  # 1s, 2s, 4s for 3 retries
                logger.warning(
                    "SEC fetch attempt %d/%d failed: %s. Retrying in %ds...",
                    attempt,
                    settings.nasdaq_retries,
                    str(e),
                    wait_time,
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    "SEC fetch failed after %d attempts. Last error: %s",
                    settings.nasdaq_retries,
                    str(e),
                )

    raise SecProviderError(
        f"Failed to fetch SEC ticker directory after {settings.nasdaq_retries} retries: {last_error}"
    )


def _fetch_and_parse(attempt: int, sec_url: str) -> Dict[str, Any]:
    """Fetch and parse SEC ticker JSON (internal; called with retry logic)."""
    logger.debug("SEC fetch attempt %d: connecting to %s", attempt, sec_url)

    # SEC EDGAR requires a specific User-Agent format: "Name Contact@email"
    # Using a browser UA returns 403 Forbidden
    headers = {
        "User-Agent": settings.sec_user_agent,
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
    }

    response = requests.get(sec_url, timeout=settings.nasdaq_timeout, headers=headers)
    response.raise_for_status()

    logger.debug("SEC fetch successful (%d bytes). Parsing...", len(response.text))

    # Parse JSON
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("SEC file is not a JSON object")

    logger.debug("SEC file contains %d entries", len(data))

    return data


def parse_sec_symbols(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse SEC JSON data and extract ticker information.

    Args:
        raw_data: JSON object from SEC with numeric string keys

    Returns:
        List of normalized symbol dicts with keys: {ticker, title, cik_str}
    """
    logger.info("Parsing SEC ticker data")

    symbols = []
    skipped = 0

    for key, entry in raw_data.items():
        try:
            # Extract fields from SEC entry
            if not isinstance(entry, dict):
                logger.debug("Skipping non-dict entry at key %s", key)
                skipped += 1
                continue

            ticker = entry.get("ticker", "").strip().upper()
            title = entry.get("title", "").strip()
            cik_str = entry.get("cik_str")

            # Skip invalid entries
            if not ticker or not title:
                logger.debug("Skipping entry with missing ticker or title at key %s", key)
                skipped += 1
                continue

            symbols.append(
                {
                    "ticker": ticker,
                    "title": title,
                    "cik_str": cik_str,
                }
            )
        except (ValueError, KeyError, AttributeError) as e:
            logger.warning("Error parsing SEC entry at key %s: %s. Skipping.", key, e)
            skipped += 1
            continue

    logger.info("SEC parser: found %d valid symbols, skipped %d", len(symbols), skipped)
    return symbols


def filter_sec_symbols(parsed_symbols: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter and normalize SEC symbols for database import.

    All SEC symbols are considered valid for inclusion. Returns normalized
    format ready for database import.

    Returns: List of dicts with keys: {symbol, company_name, yahoo_symbol}
    """
    logger.info("Normalizing %d SEC symbols for import", len(parsed_symbols))

    filtered = []

    for parsed in parsed_symbols:
        try:
            ticker = parsed.get("ticker", "").upper()
            title = parsed.get("title", "")

            # Skip entries without required fields
            if not ticker or not title:
                logger.debug("Skipping symbol with missing required fields")
                continue

            filtered.append(
                {
                    "symbol": ticker,
                    "company_name": title,
                    "yahoo_symbol": ticker,  # Same as ticker for SEC-listed equities
                }
            )
        except (ValueError, KeyError) as e:
            logger.warning("Error normalizing SEC symbol: %s. Skipping.", e)
            continue

    logger.info(
        "SEC normalization complete: %d symbols ready for import",
        len(filtered),
    )
    return filtered


def get_sec_symbols() -> List[Dict[str, Any]]:
    """
    Fetch SEC ticker directory and return normalized symbol list.

    Returns: List of dicts with keys: {symbol, company_name, yahoo_symbol}
    Raises: SecProviderError if fetch fails
    """
    raw_data = fetch_sec_symbols()
    parsed_symbols = parse_sec_symbols(raw_data)
    filtered_symbols = filter_sec_symbols(parsed_symbols)
    return filtered_symbols
