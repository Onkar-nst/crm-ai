# engine/recency.py
# Computes a time-decay recency score for a memory node using exponential decay.

import math
from datetime import datetime, timezone


def get_recency_score(timestamp_iso: str, decay_rate: float = 0.01) -> float:
    """
    Returns a recency score in [0.0, 1.0] using exponential decay.

    Formula:
        recency_score = e^(-λ × days_elapsed)

    Where:
        λ (decay_rate) = 0.01 by default
        days_elapsed   = calendar days between timestamp and today

    Examples:
        Today           → 1.0
        100 days ago    → e^(-1.0)  ≈ 0.37
        365 days ago    → e^(-3.65) ≈ 0.03

    Args:
        timestamp_iso: ISO 8601 datetime or date string (e.g., "2024-08-15T10:30:00Z"
                       or "2024-08-15")
        decay_rate:    λ — higher value = faster decay. Default 0.01.

    Returns:
        float: Recency score between 0.0 and 1.0 (inclusive).
    """
    try:
        # Handle both "2024-08-15" and "2024-08-15T10:30:00Z" formats
        ts = timestamp_iso.replace("Z", "+00:00")
        if "T" in ts:
            memory_dt = datetime.fromisoformat(ts)
        else:
            memory_dt = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)

        # Ensure timezone-aware comparison
        if memory_dt.tzinfo is None:
            memory_dt = memory_dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        days_elapsed = max(0.0, (now - memory_dt).total_seconds() / 86400)
        score = math.exp(-decay_rate * days_elapsed)
        return round(min(1.0, max(0.0, score)), 4)

    except (ValueError, AttributeError) as e:
        # If timestamp is unparseable, return neutral-low score
        return 0.1
