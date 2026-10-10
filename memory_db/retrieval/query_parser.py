# retrieval/query_parser.py
# Parses a raw business query string into a structured dict using regex only.

import re
from datetime import datetime, timezone


# ── Regex patterns ────────────────────────────────────────────────────────────

# Supplier name: capitalized words following "from" or "by" or "for"
_SUPPLIER_PATTERN = re.compile(
    r'(?:from|by|for)\s+([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,4})',
    re.IGNORECASE,
)

# Amount: ₹ or Rs. or INR followed by digits (with optional commas/dots)
_AMOUNT_PATTERN = re.compile(
    r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)',
    re.IGNORECASE,
)

# Event type keywords
_EVENT_KEYWORDS = {
    "invoice":   ["invoice", "invoiced", "billing", "bill"],
    "payment":   ["payment", "pay", "paid", "disburse", "disbursement", "transfer"],
    "delivery":  ["delivery", "deliver", "shipment", "shipped", "logistics", "dispatch"],
    "complaint": ["complaint", "defect", "defective", "issue", "problem", "quality", "rejection"],
    "ticket":    ["ticket", "support", "incident", "request"],
}

# Month name to number
_MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Seasonal hints
_SEASON_KEYWORDS = ["monsoon", "flood", "rain", "seasonal", "summer", "winter"]


def _extract_supplier_name(text: str) -> str | None:
    """Extract supplier name from text after 'from', 'by', or 'for'."""
    matches = _SUPPLIER_PATTERN.findall(text)
    if not matches:
        return None
    # Take the longest match (most descriptive)
    best = max(matches, key=len).strip()
    # Strip trailing noise words
    noise = {"for", "to", "the", "a", "an", "with", "in", "on", "at"}
    words = [w for w in best.split() if w.lower() not in noise]
    return " ".join(words) if words else None


def _extract_amount(text: str) -> float | None:
    """Extract INR amount from text, stripping commas."""
    match = _AMOUNT_PATTERN.search(text)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


def _extract_event_type(text: str) -> str | None:
    """Identify the primary business event type from keywords."""
    lower = text.lower()
    for event_type, keywords in _EVENT_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return event_type
    return None


def _extract_month_year(text: str) -> tuple[int | None, int | None]:
    """Extract month and year from text. Falls back to current month/year."""
    now = datetime.now(timezone.utc)
    month, year = None, None

    # Try month name
    for name, num in _MONTH_NAMES.items():
        if name in text.lower():
            month = num
            break

    # Try 4-digit year
    year_match = re.search(r'\b(202[0-9]|203[0-9])\b', text)
    if year_match:
        year = int(year_match.group(1))

    return month or now.month, year or now.year


def _extract_season_hint(text: str) -> str | None:
    """Detect seasonal context keywords."""
    lower = text.lower()
    for kw in _SEASON_KEYWORDS:
        if kw in lower:
            return kw
    return None


def parse_query(raw: str) -> dict:
    """
    Parse a raw business query string into a structured dict.

    Extracts:
        supplier_name   — Capitalized words after 'from' / 'by' / 'for'
        supplier_id     — Always None here; filled by DB lookup in fetcher
        amount          — Numeric INR value (₹ / Rs. prefix)
        event_type      — One of: invoice | payment | delivery | complaint | ticket
        month           — Numeric month (1–12), defaults to current
        year            — 4-digit year, defaults to current
        season_hint     — Seasonal keyword if detected (e.g., "monsoon")
        raw_query       — Original input string

    Args:
        raw: Raw natural language business query.

    Returns:
        dict: Structured query fields.
    """
    supplier_name = _extract_supplier_name(raw)
    amount        = _extract_amount(raw)
    event_type    = _extract_event_type(raw)
    month, year   = _extract_month_year(raw)
    season_hint   = _extract_season_hint(raw)

    return {
        "supplier_name": supplier_name,
        "supplier_id":   None,          # Resolved by memory_fetcher via DB lookup
        "amount":        amount,
        "event_type":    event_type,
        "month":         month,
        "year":          year,
        "season_hint":   season_hint,
        "raw_query":     raw.strip(),
    }
