# models/supplier.py
# Schema definition for the Supplier entity.

supplier_schema = {
    "supplier_id":        "string  — UUID4 primary key (e.g., 'a1b2c3d4-...')",
    "name":               "string  — Legal entity name (e.g., 'RajTech Components Pvt. Ltd.')",
    "category":           "string  — Procurement category (e.g., 'Raw Materials', 'IT Services', 'Logistics')",
    "tier":               "int     — Supplier tier: 1=Strategic, 2=Preferred, 3=Transactional",
    "registered_on":      "string  — ISO 8601 date of onboarding (e.g., '2022-03-15')",
    "contact_details": {
        "primary_contact": "string — Contact person name",
        "email":           "string — Business email",
        "phone":           "string — Contact number with country code",
        "region":          "string — Operational region (e.g., 'Maharashtra', 'Karnataka')",
    },
    "compliance_status":  "string  — Enum: APPROVED | PROBATION | SUSPENDED | BLACKLISTED",
    "credit_term_days":   "int     — Payment terms in days (e.g., 30, 45, 60)",
    "risk_score":         "float   — Composite risk 0.0–1.0 (lower = safer)",
    "tags":               "list    — Free labels (e.g., ['preferred', 'monsoon-risk'])",
}

# ── Example document ────────────────────────────────────────────────────────
supplier_example = {
    "supplier_id":        "sup-a1b2c3d4-0001",
    "name":               "RajTech Components Pvt. Ltd.",
    "category":           "Raw Materials",
    "tier":               2,
    "registered_on":      "2022-03-15",
    "contact_details": {
        "primary_contact": "Rajesh Sharma",
        "email":           "rajesh@rajtech.in",
        "phone":           "+91-9876543210",
        "region":          "Maharashtra",
    },
    "compliance_status":  "APPROVED",
    "credit_term_days":   45,
    "risk_score":         0.22,
    "tags":               ["preferred", "tier2-reviewed"],
}
