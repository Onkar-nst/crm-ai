# models/semantic_pattern.py
# Schema definition for SemanticPattern entity.

semantic_pattern_schema = {
    "pattern_id":         "string  — UUID4 primary key",
    "supplier_id":        "string  — FK to Supplier (null = global/cross-supplier pattern)",
    "pattern_type":       "string  — Enum: PAYMENT_BEHAVIOR | QUALITY_TREND | DELIVERY_TREND | INVOICE_ANOMALY | RISK_SIGNAL",
    "description":        "string  — Human-readable pattern statement for agent display",
    "derived_from_count": "int     — Number of episodes used to derive this pattern",
    "confidence":         "float   — Statistical confidence 0.0–1.0",
    "first_observed_at":  "string  — ISO 8601 date pattern was first detected",
    "last_validated_at":  "string  — ISO 8601 date last confirmed by incoming data",
    "applicable_range": {
        "start_date":     "string  — ISO 8601 start of validity window",
        "end_date":       "string  — ISO 8601 end of validity window (null = ongoing)",
    },
    "metrics":            "dict    — Key numeric indicators relevant to this pattern",
    "trigger_condition":  "string  — Situation description that should activate retrieval of this pattern",
    "is_evergreen":       "bool    — True = never expires, requires explicit override to invalidate",
}

# ── Example document ────────────────────────────────────────────────────────
semantic_pattern_example = {
    "pattern_id":         "sp-ddeeff00-0001",
    "supplier_id":        "sup-a1b2c3d4-0001",
    "pattern_type":       "PAYMENT_BEHAVIOR",
    "description":        "Supplier A consistently invoices between the 1st–5th of each month. Average invoice value ₹1,80,000 ± ₹25,000. All 12 invoices paid within credit terms.",
    "derived_from_count": 12,
    "confidence":         0.92,
    "first_observed_at":  "2023-06-01",
    "last_validated_at":  "2025-02-01",
    "applicable_range": {
        "start_date":     "2023-06-01",
        "end_date":       None,
    },
    "metrics": {
        "avg_invoice_amount_inr": 180000,
        "std_dev_inr":            25000,
        "on_time_payment_rate":   1.0,
        "avg_delay_days":         -0.5,
    },
    "trigger_condition":  "Invoice received from this supplier — use to flag amount anomalies.",
    "is_evergreen":       False,
}
