# engine/severity.py
# Normalizes event severity (1–10) and applies a financial impact multiplier.


def get_severity_score(severity: int, loss_amount: float = 0.0) -> float:
    """
    Returns a severity score in [0.0, 1.0].

    Steps:
        1. Normalize severity (1–10) to [0.0, 1.0]:
               normalized = (severity - 1) / 9
        2. Apply financial impact multiplier if loss_amount > 0:
               multiplier = min(1.5, 1 + loss_amount / 100_000)
        3. Final = min(1.0, normalized × multiplier)

    Financial multiplier examples:
        loss = ₹0        → multiplier 1.0  (no boost)
        loss = ₹50,000   → multiplier 1.5  (max boost, since 1 + 0.5 = 1.5)
        loss = ₹100,000+ → multiplier 1.5  (capped at 1.5)

    Args:
        severity:    Integer from 1 (trivial) to 10 (critical).
        loss_amount: Financial loss in INR. Default 0.

    Returns:
        float: Final severity score in [0.0, 1.0].
    """
    # Clamp severity to valid range
    severity = max(1, min(10, int(severity)))

    # Step 1: Normalize to [0, 1]
    normalized = (severity - 1) / 9.0

    # Step 2: Financial multiplier
    if loss_amount and loss_amount > 0:
        multiplier = min(1.5, 1.0 + loss_amount / 100_000.0)
    else:
        multiplier = 1.0

    # Step 3: Cap at 1.0
    final = min(1.0, normalized * multiplier)
    return round(final, 4)
