# models/payment_event.py
# Schema definition for PaymentEvent entity.

payment_event_schema = {
    "payment_id":         "string  — UUID4 primary key",
    "supplier_id":        "string  — FK to Supplier.supplier_id",
    "invoice_id":         "string  — Business invoice reference number",
    "invoice_amount_inr": "float   — Billed amount in INR",
    "paid_amount_inr":    "float   — Actual disbursed amount (may differ due to deductions)",
    "invoice_date":       "string  — ISO 8601 date invoice was received",
    "due_date":           "string  — ISO 8601 payment due date",
    "paid_date":          "string  — ISO 8601 actual payment date (null if pending)",
    "payment_status":     "string  — Enum: PENDING | APPROVED | PAID | OVERDUE | DISPUTED | PARTIAL",
    "delay_days":         "int     — Days late (0 = on time, negative = early, positive = late)",
    "deduction_reason":   "string  — Reason if paid_amount < invoice_amount (null if none)",
    "approved_by":        "string  — User ID or name of approving authority",
    "payment_channel":    "string  — e.g., 'NEFT', 'RTGS', 'Cheque'",
}

# ── Example document ────────────────────────────────────────────────────────
payment_event_example = {
    "payment_id":         "pe-55667788-0001",
    "supplier_id":        "sup-a1b2c3d4-0001",
    "invoice_id":         "INV-2024-0342",
    "invoice_amount_inr": 180000.0,
    "paid_amount_inr":    180000.0,
    "invoice_date":       "2024-07-01",
    "due_date":           "2024-08-15",
    "paid_date":          "2024-08-14",
    "payment_status":     "PAID",
    "delay_days":         -1,
    "deduction_reason":   None,
    "approved_by":        "mgr-priya-nair",
    "payment_channel":    "NEFT",
}
