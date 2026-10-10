# engine/staleness.py
# Determines whether a memory is stale and returns its freshness label.

from datetime import datetime, timezone

# Staleness thresholds in days per entity type
STALE_THRESHOLDS = {
    "QualityEvent":    365,
    "PaymentEvent":    180,
    "LogisticsNote":   90,   # 365 if "seasonal" tag present
    "SemanticPattern": 730,  # evergreen if confidence > 0.9
}

# Aging begins at 50% of the stale threshold
AGING_FRACTION = 0.50


def _days_old(memory: dict) -> float:
    """Return how many days old a memory is based on its most relevant timestamp."""
    timestamp = (
        memory.get("reported_at")
        or memory.get("invoice_date")
        or memory.get("scheduled_date")
        or memory.get("created_at")
        or memory.get("first_observed_at")
    )
    if not timestamp:
        return 9999.0  # Unknown age → treat as very old

    try:
        ts = str(timestamp).replace("Z", "+00:00")
        if "T" in ts:
            dt = datetime.fromisoformat(ts)
        else:
            dt = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)
    except (ValueError, AttributeError):
        return 9999.0


def _get_entity_type(memory: dict) -> str:
    """
    Resolve entity type from memory dict.
    Checks 'entity_type' key first, then attempts inference from field presence.
    """
    et = memory.get("entity_type") or ""
    # Normalize common variations
    mapping = {
        "QUALITY_EVENT":    "QualityEvent",
        "PAYMENT_EVENT":    "PaymentEvent",
        "LOGISTICS_NOTE":   "LogisticsNote",
        "SEMANTIC_PATTERN": "SemanticPattern",
    }
    return mapping.get(et.upper().replace(" ", "_"), et) or "Unknown"


def is_stale(memory: dict) -> bool:
    """
    Returns True if the memory should be deprioritized due to staleness.

    Rules:
        QualityEvent    → stale after 365 days
        PaymentEvent    → stale after 180 days
        LogisticsNote   → stale after 90 days
                          (365 days if memory has tag "seasonal" or "monsoon-risk")
        SemanticPattern → stale after 730 days
                          (NEVER stale if confidence > 0.9 → evergreen)

    Args:
        memory: Dict with entity_type, timestamp fields, and optional tags/confidence.

    Returns:
        bool: True if stale, False otherwise.
    """
    entity_type = _get_entity_type(memory)
    days = _days_old(memory)

    if entity_type == "SemanticPattern":
        confidence = float(memory.get("confidence", 0.0))
        if confidence > 0.9:
            return False  # Evergreen — never stale
        return days > STALE_THRESHOLDS["SemanticPattern"]

    if entity_type == "LogisticsNote":
        tags = memory.get("tags") or []
        seasonal_tags = {"seasonal", "monsoon-risk", "monsoon"}
        threshold = 365 if any(t in seasonal_tags for t in tags) else 90
        return days > threshold

    threshold = STALE_THRESHOLDS.get(entity_type)
    if threshold is None:
        return days > 365  # Default fallback
    return days > threshold


def get_freshness_label(memory: dict) -> str:
    """
    Returns one of: "fresh", "aging", "stale", "evergreen".

    Evergreen: SemanticPattern with confidence > 0.9
    Fresh:     Age < 50% of stale threshold
    Aging:     50%–100% of stale threshold
    Stale:     Age > stale threshold

    Args:
        memory: Dict with entity_type, timestamp, and optional confidence.

    Returns:
        str: One of ["fresh", "aging", "stale", "evergreen"]
    """
    entity_type = _get_entity_type(memory)
    days = _days_old(memory)

    # ── Evergreen check ───────────────────────────────────────────────────────
    if entity_type == "SemanticPattern":
        if float(memory.get("confidence", 0.0)) > 0.9:
            return "evergreen"

    # ── Resolve effective threshold ───────────────────────────────────────────
    if entity_type == "LogisticsNote":
        tags = memory.get("tags") or []
        seasonal_tags = {"seasonal", "monsoon-risk", "monsoon"}
        threshold = 365 if any(t in seasonal_tags for t in tags) else 90
    else:
        threshold = STALE_THRESHOLDS.get(entity_type, 365)

    if days > threshold:
        return "stale"
    if days > threshold * AGING_FRACTION:
        return "aging"
    return "fresh"
