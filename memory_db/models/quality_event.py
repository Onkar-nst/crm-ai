# models/quality_event.py
# Schema definition for QualityEvent entity.

quality_event_schema = {
    "event_id":           "string  — UUID4 primary key",
    "supplier_id":        "string  — FK to Supplier.supplier_id",
    "reported_at":        "string  — ISO 8601 date when issue was filed",
    "batch_id":           "string  — Shipment or production batch identifier",
    "defect_rate":        "float   — Fraction of defective units (0.12 = 12%)",
    "defect_category":    "string  — Enum: DIMENSIONAL | FUNCTIONAL | COSMETIC | SAFETY | DOCUMENTATION",
    "severity":           "int     — 1–10 (10 = most severe / critical)",
    "root_cause_summary": "string  — Brief diagnosis of failure cause",
    "resolution_status":  "string  — Enum: OPEN | IN_PROGRESS | RESOLVED | WAIVED",
    "penalty_applied":    "bool    — Whether a financial penalty was levied",
    "penalty_amount_inr": "float   — Penalty amount in INR (0 if none)",
    "correction_plan":    "string  — Supplier's agreed corrective action description",
    "resolved_at":        "string  — ISO 8601 date of full resolution (null if open)",
}

# ── Example document ────────────────────────────────────────────────────────
quality_event_example = {
    "event_id":           "qe-11223344-0001",
    "supplier_id":        "sup-a1b2c3d4-0001",
    "reported_at":        "2024-08-20",
    "batch_id":           "BATCH-B0021",
    "defect_rate":        0.02,
    "defect_category":    "COSMETIC",
    "severity":           2,
    "root_cause_summary": "Minor surface scratches due to inadequate packaging foam.",
    "resolution_status":  "RESOLVED",
    "penalty_applied":    False,
    "penalty_amount_inr": 0.0,
    "correction_plan":    "Supplier switched to bubble-wrap lining from Batch B-0022 onwards.",
    "resolved_at":        "2024-08-30",
}
