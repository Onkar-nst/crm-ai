# engine/conflict_resolver.py
# Detects and classifies conflicting quality signals for the same supplier.

from engine.recency import get_recency_score


RECENT_WINDOW_DAYS   = 90    # memories within this window = "recent"
SEVERITY_HIGH        = 7     # above this = bad signal
SEVERITY_LOW         = 4     # below this = good signal


def _days_old(memory: dict) -> float:
    """Return age in days using the most relevant timestamp field."""
    from datetime import datetime, timezone
    timestamp = (
        memory.get("reported_at")
        or memory.get("invoice_date")
        or memory.get("scheduled_date")
        or memory.get("created_at")
        or memory.get("first_observed_at")
    )
    if not timestamp:
        return 9999.0
    try:
        ts = str(timestamp).replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts) if "T" in ts else datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)
    except (ValueError, AttributeError):
        return 9999.0


def resolve_conflicts(memories: list) -> dict:
    """
    Analyzes quality-relevant memories for a single supplier and returns
    a conflict assessment dict.

    Logic:
        1. Split memories into recent (< 90 days) and historical (>= 90 days)
           based on their timestamp.
        2. Only memories with a severity field are considered.
        3. Classify:
            - "improving"    → recent avg severity < 4 AND historical max severity > 7
                               historical_weight = 0.3 (down-weighted)
            - "deteriorating"→ recent avg severity > 7
                               historical_weight = 1.0 (full weight to all history)
            - "inconsistent" → mixed signals (some recent high, some low)
                               historical_weight = 0.6
            - "stable_good"  → all severities low, no conflict
                               historical_weight = 0.2
            - "stable_bad"   → consistently high severity
                               historical_weight = 1.0
            - "no_data"      → no severity-bearing memories found

    Args:
        memories: List of event dicts (any mix of QualityEvent, PaymentEvent, etc.)
                  All should be for the SAME supplier.

    Returns:
        dict: {
            "flag":               str,   one of the labels above
            "historical_weight":  float, how much to trust historical memories
            "recent_count":       int,
            "historical_count":   int,
            "recent_avg_severity":    float,
            "historical_max_severity": float,
            "summary":            str,   human-readable explanation
        }
    """
    # Filter to only memories with a usable severity score
    severity_memories = [m for m in memories if m.get("severity") and int(m["severity"]) > 0]

    if not severity_memories:
        return {
            "flag":                    "no_data",
            "historical_weight":       0.5,
            "recent_count":            0,
            "historical_count":        0,
            "recent_avg_severity":     0.0,
            "historical_max_severity": 0.0,
            "summary":                 "No severity-bearing memories found. Cannot assess conflict.",
        }

    # Split by recency window
    recent     = [m for m in severity_memories if _days_old(m) < RECENT_WINDOW_DAYS]
    historical = [m for m in severity_memories if _days_old(m) >= RECENT_WINDOW_DAYS]

    recent_severities     = [int(m["severity"]) for m in recent]
    historical_severities = [int(m["severity"]) for m in historical]

    recent_avg  = sum(recent_severities) / len(recent_severities) if recent_severities else 0.0
    hist_max    = max(historical_severities) if historical_severities else 0.0
    recent_max  = max(recent_severities) if recent_severities else 0.0
    recent_min  = min(recent_severities) if recent_severities else 0.0

    # ── Classification logic ─────────────────────────────────────────────────

    # Case: Improving — was bad historically, good recently
    if recent_avg < SEVERITY_LOW and hist_max > SEVERITY_HIGH:
        flag               = "improving"
        historical_weight  = 0.3
        summary = (
            f"Supplier showed high historical severity (max={hist_max:.0f}) "
            f"but recent performance is good (avg severity={recent_avg:.1f} over last {RECENT_WINDOW_DAYS} days). "
            f"Historical memories are down-weighted to {historical_weight}."
        )

    # Case: Deteriorating — recent signals are bad
    elif recent_avg > SEVERITY_HIGH:
        flag               = "deteriorating"
        historical_weight  = 1.0
        summary = (
            f"Recent supplier performance is poor (avg severity={recent_avg:.1f}). "
            f"Historical memories retain full weight ({historical_weight}). "
            f"Escalation or review recommended."
        )

    # Case: Inconsistent — recent signals are mixed
    elif recent_severities and (recent_max > SEVERITY_HIGH or recent_min < SEVERITY_LOW):
        flag               = "inconsistent"
        historical_weight  = 0.6
        summary = (
            f"Mixed recent signals detected (severity range {recent_min}–{recent_max}). "
            f"Historical weight set to {historical_weight}. Monitor closely."
        )

    # Case: Stable good — everything low
    elif recent_avg < SEVERITY_LOW and hist_max <= SEVERITY_HIGH:
        flag               = "stable_good"
        historical_weight  = 0.2
        summary = (
            f"Consistently good performance. Recent avg severity={recent_avg:.1f}, "
            f"historical max={hist_max:.0f}. Historical memories minimally weighted."
        )

    # Case: Stable bad — consistently high everywhere
    elif recent_avg > SEVERITY_HIGH and hist_max > SEVERITY_HIGH:
        flag               = "stable_bad"
        historical_weight  = 1.0
        summary = (
            f"Persistently poor performance. Recent avg={recent_avg:.1f}, "
            f"historical max={hist_max:.0f}. All history carries full weight."
        )

    # Fallback
    else:
        flag               = "inconsistent"
        historical_weight  = 0.6
        summary = (
            f"Signals are ambiguous. Recent avg={recent_avg:.1f}, "
            f"historical max={hist_max:.0f}. Using default weight {historical_weight}."
        )

    return {
        "flag":                    flag,
        "historical_weight":       historical_weight,
        "recent_count":            len(recent),
        "historical_count":        len(historical),
        "recent_avg_severity":     round(recent_avg, 2),
        "historical_max_severity": round(hist_max, 2),
        "summary":                 summary,
    }
