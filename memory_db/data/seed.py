# data/seed.py
# Seeds MongoDB with realistic mock data for 3 suppliers.
# Run: python -m data.seed  (from memory_db/ directory)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uuid import uuid4
from datetime import datetime, timezone
from db.connection import get_database
from db.collections import setup_collections

# ── Helpers ──────────────────────────────────────────────────────────────────

def uid():
    return str(uuid4())

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def date(s):
    """Return ISO 8601 date string as-is (for readability in seed data)."""
    return s

# ── Fixed supplier IDs (reused for FK linking) ───────────────────────────────
SUP_A = "sup-" + "aaaa-1111-aaaa-111111111111"
SUP_B = "sup-" + "bbbb-2222-bbbb-222222222222"
SUP_C = "sup-" + "cccc-3333-cccc-333333333333"

# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIERS
# ─────────────────────────────────────────────────────────────────────────────
suppliers = [
    {
        "supplier_id":       SUP_A,
        "name":              "RajTech Components Pvt. Ltd.",
        "category":          "Raw Materials",
        "tier":              2,
        "registered_on":     date("2021-06-01"),
        "contact_details": {
            "primary_contact": "Rajesh Sharma",
            "email":           "rajesh@rajtech.in",
            "phone":           "+91-9876543210",
            "region":          "Maharashtra",
        },
        "compliance_status": "APPROVED",
        "credit_term_days":  45,
        "risk_score":        0.18,
        "tags":              ["preferred", "long-term"],
    },
    {
        "supplier_id":       SUP_B,
        "name":              "Delta Forge Industries",
        "category":          "Metal Fabrication",
        "tier":              2,
        "registered_on":     date("2022-01-15"),
        "contact_details": {
            "primary_contact": "Sunita Mehta",
            "email":           "sunita@deltaforge.in",
            "phone":           "+91-9123456780",
            "region":          "Gujarat",
        },
        "compliance_status": "PROBATION",
        "credit_term_days":  30,
        "risk_score":        0.61,
        "tags":              ["probation", "quality-watch"],
    },
    {
        "supplier_id":       SUP_C,
        "name":              "Coastal Freight Solutions",
        "category":          "Logistics",
        "tier":              3,
        "registered_on":     date("2020-09-10"),
        "contact_details": {
            "primary_contact": "Arun Pillai",
            "email":           "arun@coastalfreight.in",
            "phone":           "+91-9988776655",
            "region":          "Kerala",
        },
        "compliance_status": "APPROVED",
        "credit_term_days":  60,
        "risk_score":        0.35,
        "tags":              ["monsoon-risk", "reliable-offseason"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# QUALITY EVENTS
# ─────────────────────────────────────────────────────────────────────────────

# IDs — fixed so MemoryNodes can reference them
QE_A1 = uid(); QE_A2 = uid()
QE_B1 = uid(); QE_B2 = uid()
QE_C1 = uid(); QE_C2 = uid()

quality_events = [
    # ── Supplier A: Good overall, one minor cosmetic issue 8 months ago ──────
    {
        "event_id":           QE_A1,
        "supplier_id":        SUP_A,
        "reported_at":        date("2024-08-12"),
        "batch_id":           "BATCH-RA-0089",
        "defect_rate":        0.02,
        "defect_category":    "COSMETIC",
        "severity":           2,
        "root_cause_summary": "Surface scratches on 4 of 200 units due to loose packaging inserts.",
        "resolution_status":  "RESOLVED",
        "penalty_applied":    False,
        "penalty_amount_inr": 0.0,
        "correction_plan":    "Supplier upgraded to foam-padded inner trays from Batch RA-0090.",
        "resolved_at":        date("2024-08-22"),
    },
    {
        "event_id":           QE_A2,
        "supplier_id":        SUP_A,
        "reported_at":        date("2025-01-05"),
        "batch_id":           "BATCH-RA-0112",
        "defect_rate":        0.005,
        "defect_category":    "DOCUMENTATION",
        "severity":           1,
        "root_cause_summary": "2 units missing CE certification stickers — admin oversight.",
        "resolution_status":  "RESOLVED",
        "penalty_applied":    False,
        "penalty_amount_inr": 0.0,
        "correction_plan":    "Certification checklist added to pre-dispatch QC process.",
        "resolved_at":        date("2025-01-08"),
    },
    # ── Supplier B: 30% defect rate 4 months ago, improving now ─────────────
    {
        "event_id":           QE_B1,
        "supplier_id":        SUP_B,
        "reported_at":        date("2024-12-10"),
        "batch_id":           "BATCH-DF-0047",
        "defect_rate":        0.30,
        "defect_category":    "FUNCTIONAL",
        "severity":           9,
        "root_cause_summary": "Incorrect alloy mix in production run. 60 of 200 brackets failed load test.",
        "resolution_status":  "RESOLVED",
        "penalty_applied":    True,
        "penalty_amount_inr": 50000.0,
        "correction_plan":    "Third-party metallurgy audit completed. New alloy verification protocol implemented.",
        "resolved_at":        date("2025-01-20"),
    },
    {
        "event_id":           QE_B2,
        "supplier_id":        SUP_B,
        "reported_at":        date("2025-03-18"),
        "batch_id":           "BATCH-DF-0055",
        "defect_rate":        0.01,
        "defect_category":    "DIMENSIONAL",
        "severity":           3,
        "root_cause_summary": "Minor tolerance deviation (±0.3mm) in 2 units. Within acceptable range for most use-cases.",
        "resolution_status":  "WAIVED",
        "penalty_applied":    False,
        "penalty_amount_inr": 0.0,
        "correction_plan":    "Tolerance re-confirmed at ±0.2mm for next batch.",
        "resolved_at":        date("2025-03-20"),
    },
    # ── Supplier C: Monsoon delay impact on one batch, otherwise clean ───────
    {
        "event_id":           QE_C1,
        "supplier_id":        SUP_C,
        "reported_at":        date("2024-07-22"),
        "batch_id":           "BATCH-CF-0031",
        "defect_rate":        0.08,
        "defect_category":    "COSMETIC",
        "severity":           4,
        "root_cause_summary": "Water seepage during monsoon transit damaged outer packaging on 16 of 200 units.",
        "resolution_status":  "RESOLVED",
        "penalty_applied":    False,
        "penalty_amount_inr": 0.0,
        "correction_plan":    "Waterproof poly-shrink wrapping mandatory during June–September shipments.",
        "resolved_at":        date("2024-08-05"),
    },
    {
        "event_id":           QE_C2,
        "supplier_id":        SUP_C,
        "reported_at":        date("2025-02-14"),
        "batch_id":           "BATCH-CF-0044",
        "defect_rate":        0.0,
        "defect_category":    "DOCUMENTATION",
        "severity":           1,
        "root_cause_summary": "E-way bill timestamp mismatch by 2 hours — resolved at checkpoint.",
        "resolution_status":  "RESOLVED",
        "penalty_applied":    False,
        "penalty_amount_inr": 0.0,
        "correction_plan":    "Auto-generated e-way bills now verified 30 min before dispatch.",
        "resolved_at":        date("2025-02-14"),
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT EVENTS
# ─────────────────────────────────────────────────────────────────────────────

PE_A1 = uid(); PE_A2 = uid()
PE_B1 = uid(); PE_B2 = uid()
PE_C1 = uid(); PE_C2 = uid()

payment_events = [
    # ── Supplier A: One disputed invoice 8 months ago (minor), all else clean
    {
        "payment_id":         PE_A1,
        "supplier_id":        SUP_A,
        "invoice_id":         "INV-RA-2024-0331",
        "invoice_amount_inr": 185000.0,
        "paid_amount_inr":    175000.0,
        "invoice_date":       date("2024-08-01"),
        "due_date":           date("2024-09-15"),
        "paid_date":          date("2024-09-18"),
        "payment_status":     "PAID",
        "delay_days":         3,
        "deduction_reason":   "₹10,000 deducted as quality penalty for Batch RA-0089 cosmetic defects.",
        "approved_by":        "mgr-priya-nair",
        "payment_channel":    "NEFT",
    },
    {
        "payment_id":         PE_A2,
        "supplier_id":        SUP_A,
        "invoice_id":         "INV-RA-2025-0102",
        "invoice_amount_inr": 192000.0,
        "paid_amount_inr":    192000.0,
        "invoice_date":       date("2025-02-03"),
        "due_date":           date("2025-03-20"),
        "paid_date":          date("2025-03-17"),
        "payment_status":     "PAID",
        "delay_days":         -3,
        "deduction_reason":   None,
        "approved_by":        "mgr-priya-nair",
        "payment_channel":    "RTGS",
    },
    # ── Supplier B: Overdue payment dispute, then partial recovery
    {
        "payment_id":         PE_B1,
        "supplier_id":        SUP_B,
        "invoice_id":         "INV-DF-2024-0519",
        "invoice_amount_inr": 320000.0,
        "paid_amount_inr":    270000.0,
        "invoice_date":       date("2024-12-01"),
        "due_date":           date("2024-12-31"),
        "paid_date":          date("2025-01-25"),
        "payment_status":     "PARTIAL",
        "delay_days":         25,
        "deduction_reason":   "₹50,000 penalty withheld for Batch DF-0047 functional defects (30% defect rate).",
        "approved_by":        "mgr-vikram-joshi",
        "payment_channel":    "NEFT",
    },
    {
        "payment_id":         PE_B2,
        "supplier_id":        SUP_B,
        "invoice_id":         "INV-DF-2025-0088",
        "invoice_amount_inr": 290000.0,
        "paid_amount_inr":    290000.0,
        "invoice_date":       date("2025-03-05"),
        "due_date":           date("2025-04-04"),
        "paid_date":          date("2025-04-01"),
        "payment_status":     "PAID",
        "delay_days":         -3,
        "deduction_reason":   None,
        "approved_by":        "mgr-vikram-joshi",
        "payment_channel":    "RTGS",
    },
    # ── Supplier C: Reliable payments, slight delay once during monsoon season
    {
        "payment_id":         PE_C1,
        "supplier_id":        SUP_C,
        "invoice_id":         "INV-CF-2024-0278",
        "invoice_amount_inr": 95000.0,
        "paid_amount_inr":    95000.0,
        "invoice_date":       date("2024-07-05"),
        "due_date":           date("2024-09-03"),
        "paid_date":          date("2024-09-10"),
        "payment_status":     "PAID",
        "delay_days":         7,
        "deduction_reason":   None,
        "approved_by":        "mgr-divya-krishnan",
        "payment_channel":    "NEFT",
    },
    {
        "payment_id":         PE_C2,
        "supplier_id":        SUP_C,
        "invoice_id":         "INV-CF-2025-0044",
        "invoice_amount_inr": 102000.0,
        "paid_amount_inr":    102000.0,
        "invoice_date":       date("2025-02-01"),
        "due_date":           date("2025-04-02"),
        "paid_date":          date("2025-03-30"),
        "payment_status":     "PAID",
        "delay_days":         -3,
        "deduction_reason":   None,
        "approved_by":        "mgr-divya-krishnan",
        "payment_channel":    "NEFT",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# LOGISTICS NOTES
# ─────────────────────────────────────────────────────────────────────────────

LN_A1 = uid()
LN_B1 = uid()
LN_C1 = uid()

logistics_notes = [
    {
        "note_id":           LN_A1,
        "supplier_id":       SUP_A,
        "shipment_id":       "SHP-RA-20250301-001",
        "scheduled_date":    date("2025-03-01"),
        "actual_date":       date("2025-03-01"),
        "delay_days":        0,
        "delay_reason":      None,
        "carrier_name":      "BlueDart Express",
        "delivery_location": "Pune Warehouse – Gate 3",
        "condition":         "INTACT",
        "received_by":       "storekeeper-ravi-kulkarni",
        "notes":             "200 units received. All seals intact. QC spot-check passed.",
    },
    {
        "note_id":           LN_B1,
        "supplier_id":       SUP_B,
        "shipment_id":       "SHP-DF-20250318-001",
        "scheduled_date":    date("2025-03-15"),
        "actual_date":       date("2025-03-18"),
        "delay_days":        3,
        "delay_reason":      "Truck breakdown on NH-48. Replacement arranged by carrier.",
        "carrier_name":      "Mahindra Logistics",
        "delivery_location": "Surat Plant – Loading Bay 2",
        "condition":         "INTACT",
        "received_by":       "storekeeper-anand-patel",
        "notes":             "3-day delay due to transport issue. Goods undamaged. Supplier notified in advance.",
    },
    {
        "note_id":           LN_C1,
        "supplier_id":       SUP_C,
        "shipment_id":       "SHP-CF-20240720-001",
        "scheduled_date":    date("2024-07-18"),
        "actual_date":       date("2024-07-22"),
        "delay_days":        4,
        "delay_reason":      "Route blocked due to Kerala flood alerts. State highway closed for 3 days.",
        "carrier_name":      "Coastal Freight Solutions (self)",
        "delivery_location": "Kochi Distribution Hub",
        "condition":         "MINOR_DAMAGE",
        "received_by":       "hub-manager-sreekumar",
        "notes":             "Outer packaging of 16 units water-damaged. Inner goods intact. Claim waived.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# SEMANTIC PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

SP_A1 = uid()
SP_B1 = uid()
SP_C1 = uid()

semantic_patterns = [
    {
        "pattern_id":         SP_A1,
        "supplier_id":        SUP_A,
        "pattern_type":       "PAYMENT_BEHAVIOR",
        "description":        (
            "RajTech invoices consistently between the 1st–5th of each month. "
            "Avg invoice value ₹1,85,000 ± ₹20,000. 11 of 12 invoices paid on time. "
            "One minor 3-day delay linked to a quality dispute — not a systemic issue."
        ),
        "derived_from_count": 12,
        "confidence":         0.91,
        "first_observed_at":  date("2022-06-01"),
        "last_validated_at":  date("2025-03-17"),
        "applicable_range":   {"start_date": date("2022-06-01"), "end_date": None},
        "metrics": {
            "avg_invoice_amount_inr": 185000,
            "std_dev_inr":            20000,
            "on_time_payment_rate":   0.92,
            "avg_delay_days":         0.25,
        },
        "trigger_condition":  "Invoice received from RajTech — flag if amount exceeds ₹2,25,000.",
        "is_evergreen":       False,
    },
    {
        "pattern_id":         SP_B1,
        "supplier_id":        SUP_B,
        "pattern_type":       "QUALITY_TREND",
        "description":        (
            "Delta Forge had a severe quality failure (30% defect rate, ₹50,000 loss) in Dec 2024. "
            "Post corrective action, last 2 batches show <2% defect rate. "
            "Supplier is in RECOVERING state — confidence improving but not yet rehabilitated."
        ),
        "derived_from_count": 6,
        "confidence":         0.74,
        "first_observed_at":  date("2024-12-10"),
        "last_validated_at":  date("2025-03-20"),
        "applicable_range":   {"start_date": date("2024-06-01"), "end_date": None},
        "metrics": {
            "legacy_defect_rate":     0.30,
            "recent_defect_rate":     0.01,
            "penalty_paid_inr":       50000,
            "recovery_streak_days":   100,
            "reconciled_risk_score":  0.38,
        },
        "trigger_condition":  "Any invoice or quality check for Delta Forge — surface conflict history.",
        "is_evergreen":       False,
    },
    {
        "pattern_id":         SP_C1,
        "supplier_id":        SUP_C,
        "pattern_type":       "DELIVERY_TREND",
        "description":        (
            "Coastal Freight shows a consistent pattern of 3–6 day delivery delays "
            "during the monsoon season (June–September) every year for 4 consecutive years. "
            "Off-season delivery record is excellent: 98% on-time. "
            "Delays are route-driven (Kerala flooding), not operational negligence."
        ),
        "derived_from_count": 18,
        "confidence":         0.88,
        "first_observed_at":  date("2021-07-01"),
        "last_validated_at":  date("2024-07-22"),
        "applicable_range":   {"start_date": date("2021-07-01"), "end_date": None},
        "metrics": {
            "monsoon_avg_delay_days":    4.2,
            "offseason_on_time_rate":    0.98,
            "affected_months":           ["June", "July", "August", "September"],
            "years_observed":            4,
        },
        "trigger_condition":  "Any shipment from Coastal Freight between June–September — warn proactively.",
        "is_evergreen":       False,
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# MEMORY NODES — one per entity (universal wrapper)
# ─────────────────────────────────────────────────────────────────────────────

def make_memory_node(memory_type, entity_type, entity_id, supplier_id, summary, freshness="FRESH", confidence=0.9):
    return {
        "node_id":           uid(),
        "memory_type":       memory_type,
        "entity_type":       entity_type,
        "entity_id":         entity_id,
        "supplier_id":       supplier_id,
        "content_summary":   summary,
        "created_at":        now_iso(),
        "last_accessed_at":  now_iso(),
        "access_count":      0,
        "relevance_score":   0.80,
        "freshness_state":   freshness,
        "decay_rate":        0.003 if freshness != "EVERGREEN" else 0.0,
        "source_session_id": None,
        "linked_node_ids":   [],
        "confidence_score":  confidence,
    }

memory_nodes = [
    # Supplier A nodes
    make_memory_node("EPISODIC", "QUALITY_EVENT",    QE_A1, SUP_A, "Supplier A: Minor cosmetic defect 2% — Aug 2024. Resolved.",              freshness="AGING",  confidence=0.98),
    make_memory_node("EPISODIC", "QUALITY_EVENT",    QE_A2, SUP_A, "Supplier A: Doc sticker missing — Jan 2025. Resolved instantly.",          freshness="FRESH",  confidence=0.99),
    make_memory_node("EPISODIC", "PAYMENT_EVENT",    PE_A1, SUP_A, "Supplier A: INV-RA-2024-0331 — ₹1,85,000, 3-day delay, ₹10k deducted.",   freshness="AGING",  confidence=0.97),
    make_memory_node("EPISODIC", "PAYMENT_EVENT",    PE_A2, SUP_A, "Supplier A: INV-RA-2025-0102 — ₹1,92,000, paid 3 days early.",            freshness="FRESH",  confidence=0.99),
    make_memory_node("EPISODIC", "LOGISTICS_NOTE",   LN_A1, SUP_A, "Supplier A: SHP-RA-20250301 — On time, intact, 200 units.",               freshness="FRESH",  confidence=1.0),
    make_memory_node("SEMANTIC", "SEMANTIC_PATTERN", SP_A1, SUP_A, "RajTech payment behavior: reliable, avg ₹1,85,000, 92% on-time.",          freshness="FRESH",  confidence=0.91),
    # Supplier B nodes
    make_memory_node("EPISODIC", "QUALITY_EVENT",    QE_B1, SUP_B, "Supplier B: CRITICAL — 30% defect rate Dec 2024, ₹50k penalty. Resolved.", freshness="AGING",  confidence=0.99),
    make_memory_node("EPISODIC", "QUALITY_EVENT",    QE_B2, SUP_B, "Supplier B: Minor 1% dimensional — Mar 2025. Waived.",                    freshness="FRESH",  confidence=0.97),
    make_memory_node("EPISODIC", "PAYMENT_EVENT",    PE_B1, SUP_B, "Supplier B: INV-DF-2024-0519 — ₹3,20,000, 25-day late, partial pay.",     freshness="AGING",  confidence=0.98),
    make_memory_node("EPISODIC", "PAYMENT_EVENT",    PE_B2, SUP_B, "Supplier B: INV-DF-2025-0088 — ₹2,90,000, paid 3 days early.",            freshness="FRESH",  confidence=0.99),
    make_memory_node("EPISODIC", "LOGISTICS_NOTE",   LN_B1, SUP_B, "Supplier B: SHP-DF-20250318 — 3-day delay, truck breakdown. Intact.",      freshness="FRESH",  confidence=0.96),
    make_memory_node("SEMANTIC", "SEMANTIC_PATTERN", SP_B1, SUP_B, "Delta Forge RECOVERING: past 30% defect, recent <2%. Risk=0.38.",          freshness="FRESH",  confidence=0.74),
    # Supplier C nodes
    make_memory_node("EPISODIC", "QUALITY_EVENT",    QE_C1, SUP_C, "Supplier C: Monsoon packaging damage 8% — Jul 2024. Resolved.",            freshness="AGING",  confidence=0.97),
    make_memory_node("EPISODIC", "QUALITY_EVENT",    QE_C2, SUP_C, "Supplier C: E-way bill mismatch — Feb 2025. Resolved same day.",           freshness="FRESH",  confidence=0.99),
    make_memory_node("EPISODIC", "PAYMENT_EVENT",    PE_C1, SUP_C, "Supplier C: INV-CF-2024-0278 — ₹95,000, 7-day late (monsoon).",            freshness="AGING",  confidence=0.97),
    make_memory_node("EPISODIC", "PAYMENT_EVENT",    PE_C2, SUP_C, "Supplier C: INV-CF-2025-0044 — ₹1,02,000, paid 3 days early.",            freshness="FRESH",  confidence=0.99),
    make_memory_node("EPISODIC", "LOGISTICS_NOTE",   LN_C1, SUP_C, "Supplier C: SHP-CF-20240720 — 4-day monsoon delay, minor damage.",         freshness="AGING",  confidence=0.95),
    make_memory_node("SEMANTIC", "SEMANTIC_PATTERN", SP_C1, SUP_C, "Coastal Freight: monsoon delays 3–6d every year, 98% on-time offseason.",  freshness="FRESH",  confidence=0.88),
]

# ─────────────────────────────────────────────────────────────────────────────
# SEEDER MAIN
# ─────────────────────────────────────────────────────────────────────────────

def seed():
    db = get_database()
    print("\n── Setting up collections and indexes ──")
    setup_collections(db)

    collections_data = {
        "suppliers":         suppliers,
        "quality_events":    quality_events,
        "payment_events":    payment_events,
        "logistics_notes":   logistics_notes,
        "semantic_patterns": semantic_patterns,
        "memory_nodes":      memory_nodes,
    }

    print("\n── Inserting seed data ──")
    for col_name, docs in collections_data.items():
        col = db[col_name]
        col.delete_many({})           # wipe before re-seeding (idempotent)
        result = col.insert_many(docs)
        print(f"  [OK] {col_name}: inserted {len(result.inserted_ids)} documents")

    print("\n✅ Seeding complete!\n")


if __name__ == "__main__":
    seed()
