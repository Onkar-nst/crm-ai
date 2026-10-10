# models/logistics_note.py
# Schema definition for LogisticsNote entity.

logistics_note_schema = {
    "note_id":            "string  — UUID4 primary key",
    "supplier_id":        "string  — FK to Supplier.supplier_id",
    "shipment_id":        "string  — Shipment or PO reference number",
    "scheduled_date":     "string  — ISO 8601 originally promised delivery date",
    "actual_date":        "string  — ISO 8601 actual delivery date",
    "delay_days":         "int     — Variance: negative=early, 0=on-time, positive=late",
    "delay_reason":       "string  — Stated cause of delay (null if on time)",
    "carrier_name":       "string  — Logistics/courier partner name",
    "delivery_location":  "string  — Warehouse or plant name received at",
    "condition":          "string  — Enum: INTACT | MINOR_DAMAGE | MAJOR_DAMAGE | REJECTED",
    "received_by":        "string  — User ID or name of receiving officer",
    "notes":              "string  — Free-text field observations",
}

# ── Example document ────────────────────────────────────────────────────────
logistics_note_example = {
    "note_id":            "ln-99aabbcc-0001",
    "supplier_id":        "sup-a1b2c3d4-0001",
    "shipment_id":        "SHP-20240901-001",
    "scheduled_date":     "2024-09-01",
    "actual_date":        "2024-09-01",
    "delay_days":         0,
    "delay_reason":       None,
    "carrier_name":       "BlueDart Express",
    "delivery_location":  "Pune Warehouse - Gate 3",
    "condition":          "INTACT",
    "received_by":        "store-keeper-ravi",
    "notes":              "All 50 units received. Packaging intact. Signed off.",
}
