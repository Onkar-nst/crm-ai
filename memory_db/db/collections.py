# db/collections.py
# Creates all 6 collections and their indexes in MongoDB.

from pymongo import ASCENDING, DESCENDING


COLLECTIONS = [
    "suppliers",
    "memory_nodes",
    "quality_events",
    "payment_events",
    "logistics_notes",
    "semantic_patterns",
]


def setup_collections(db):
    """
    Ensures all 6 collections exist and have the correct indexes.
    Safe to run multiple times — MongoDB skips indexes that already exist.
    """
    existing = db.list_collection_names()

    for name in COLLECTIONS:
        if name not in existing:
            db.create_collection(name)
            print(f"  [CREATED] Collection: {name}")
        else:
            print(f"  [EXISTS]  Collection: {name}")

    _create_indexes(db)
    print("[OK] All collections and indexes are ready.")


def _create_indexes(db):
    """Define indexes per collection for fast retrieval."""

    # ── suppliers ───────────────────────────────────────────────────────────
    db.suppliers.create_index(
        [("supplier_id", ASCENDING)], unique=True, name="idx_supplier_id"
    )
    db.suppliers.create_index(
        [("compliance_status", ASCENDING)], name="idx_compliance_status"
    )
    db.suppliers.create_index(
        [("risk_score", ASCENDING)], name="idx_risk_score"
    )

    # ── memory_nodes ────────────────────────────────────────────────────────
    db.memory_nodes.create_index(
        [("node_id", ASCENDING)], unique=True, name="idx_node_id"
    )
    db.memory_nodes.create_index(
        [("supplier_id", ASCENDING)], name="idx_mn_supplier_id"
    )
    db.memory_nodes.create_index(
        [("memory_type", ASCENDING)], name="idx_memory_type"
    )
    db.memory_nodes.create_index(
        [("freshness_state", ASCENDING)], name="idx_freshness_state"
    )
    db.memory_nodes.create_index(
        [("created_at", DESCENDING)], name="idx_mn_created_at"
    )
    # Compound: supplier + type + recency — the primary retrieval pattern
    db.memory_nodes.create_index(
        [("supplier_id", ASCENDING), ("memory_type", ASCENDING), ("created_at", DESCENDING)],
        name="idx_mn_supplier_type_time",
    )

    # ── quality_events ──────────────────────────────────────────────────────
    db.quality_events.create_index(
        [("event_id", ASCENDING)], unique=True, name="idx_qe_event_id"
    )
    db.quality_events.create_index(
        [("supplier_id", ASCENDING)], name="idx_qe_supplier_id"
    )
    db.quality_events.create_index(
        [("severity", DESCENDING)], name="idx_qe_severity"
    )
    db.quality_events.create_index(
        [("reported_at", DESCENDING)], name="idx_qe_reported_at"
    )
    # Compound: supplier + severity + time — used in conflict resolution scoring
    db.quality_events.create_index(
        [("supplier_id", ASCENDING), ("severity", DESCENDING), ("reported_at", DESCENDING)],
        name="idx_qe_supplier_severity_time",
    )

    # ── payment_events ──────────────────────────────────────────────────────
    db.payment_events.create_index(
        [("payment_id", ASCENDING)], unique=True, name="idx_pe_payment_id"
    )
    db.payment_events.create_index(
        [("supplier_id", ASCENDING)], name="idx_pe_supplier_id"
    )
    db.payment_events.create_index(
        [("payment_status", ASCENDING)], name="idx_pe_status"
    )
    db.payment_events.create_index(
        [("invoice_date", DESCENDING)], name="idx_pe_invoice_date"
    )

    # ── logistics_notes ─────────────────────────────────────────────────────
    db.logistics_notes.create_index(
        [("note_id", ASCENDING)], unique=True, name="idx_ln_note_id"
    )
    db.logistics_notes.create_index(
        [("supplier_id", ASCENDING)], name="idx_ln_supplier_id"
    )
    db.logistics_notes.create_index(
        [("scheduled_date", DESCENDING)], name="idx_ln_scheduled_date"
    )
    db.logistics_notes.create_index(
        [("condition", ASCENDING)], name="idx_ln_condition"
    )

    # ── semantic_patterns ───────────────────────────────────────────────────
    db.semantic_patterns.create_index(
        [("pattern_id", ASCENDING)], unique=True, name="idx_sp_pattern_id"
    )
    db.semantic_patterns.create_index(
        [("supplier_id", ASCENDING)], name="idx_sp_supplier_id"
    )
    db.semantic_patterns.create_index(
        [("pattern_type", ASCENDING)], name="idx_sp_pattern_type"
    )
    db.semantic_patterns.create_index(
        [("is_evergreen", ASCENDING)], name="idx_sp_evergreen"
    )

    print("  [OK] All indexes created/verified.")
