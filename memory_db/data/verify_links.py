# data/verify_links.py
# Verifies data integrity after seeding.
# Run: python -m data.verify_links  (from memory_db/ directory)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_database


def print_section(title):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def verify():
    db = get_database()

    # ── 1. Document counts per collection ────────────────────────────────────
    print_section("1. DOCUMENT COUNTS PER COLLECTION")
    collections = [
        "suppliers", "memory_nodes", "quality_events",
        "payment_events", "logistics_notes", "semantic_patterns",
    ]
    for name in collections:
        count = db[name].count_documents({})
        status = "✅" if count > 0 else "❌ EMPTY"
        print(f"  {status}  {name:<22} → {count} documents")

    # ── 2. All events for Supplier B via supplier_id ──────────────────────────
    print_section("2. ALL EVENTS FOR SUPPLIER B (Delta Forge Industries)")

    supplier_b = db.suppliers.find_one({"name": "Delta Forge Industries"})
    if not supplier_b:
        print("  ❌ Supplier B not found!")
        return

    sup_b_id = supplier_b["supplier_id"]
    print(f"  Supplier ID : {sup_b_id}")
    print(f"  Status      : {supplier_b['compliance_status']}")
    print(f"  Risk Score  : {supplier_b['risk_score']}")

    checks = {
        "quality_events":    ("event_id",   "reported_at",   "severity"),
        "payment_events":    ("payment_id", "invoice_id",    "payment_status"),
        "logistics_notes":   ("note_id",    "shipment_id",   "condition"),
        "semantic_patterns": ("pattern_id", "pattern_type",  "confidence"),
        "memory_nodes":      ("node_id",    "memory_type",   "freshness_state"),
    }

    for col_name, (id_field, label_field, extra_field) in checks.items():
        docs = list(db[col_name].find({"supplier_id": sup_b_id}))
        print(f"\n  [{col_name}] — {len(docs)} record(s)")
        for d in docs:
            print(f"    • {d.get(id_field, 'N/A')[:30]}")
            print(f"      {label_field}: {d.get(label_field, 'N/A')}  |  {extra_field}: {d.get(extra_field, 'N/A')}")

    # ── 3. MemoryNode entity_id referential integrity check ──────────────────
    print_section("3. MEMORYNODE → ENTITY REFERENTIAL INTEGRITY CHECK")

    entity_collections = {
        "QUALITY_EVENT":    ("quality_events",    "event_id"),
        "PAYMENT_EVENT":    ("payment_events",    "payment_id"),
        "LOGISTICS_NOTE":   ("logistics_notes",   "note_id"),
        "SEMANTIC_PATTERN": ("semantic_patterns", "pattern_id"),
    }

    all_nodes = list(db.memory_nodes.find({}))
    total = len(all_nodes)
    valid = 0
    broken = []

    for node in all_nodes:
        entity_type = node.get("entity_type")
        entity_id   = node.get("entity_id")

        if entity_type not in entity_collections:
            # SUPPLIER type or unknown — skip strict check
            valid += 1
            continue

        col_name, pk_field = entity_collections[entity_type]
        ref = db[col_name].find_one({pk_field: entity_id})
        if ref:
            valid += 1
        else:
            broken.append((node["node_id"], entity_type, entity_id))

    print(f"\n  Total MemoryNodes : {total}")
    print(f"  Valid links       : {valid}")
    print(f"  Broken links      : {len(broken)}")

    if broken:
        print("\n  ❌ BROKEN REFERENCES:")
        for node_id, etype, eid in broken:
            print(f"    node_id={node_id}  →  {etype} / {eid} NOT FOUND")
    else:
        print("\n  ✅ All MemoryNodes have valid entity references.")

    print(f"\n{'═' * 60}")
    print("  Verification complete.")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    verify()
