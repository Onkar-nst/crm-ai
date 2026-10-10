# engine/test_engine.py
# End-to-end test: fetches Supplier B's memories from MongoDB, runs all
# scoring functions, prints a ranked table, and shows conflict resolution.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_database
from engine.relevance import rank_memories
from engine.staleness import get_freshness_label, is_stale
from engine.conflict_resolver import resolve_conflicts

# ── Config ────────────────────────────────────────────────────────────────────
TARGET_SUPPLIER_NAME = "Delta Forge Industries"   # Supplier B from Phase 2

# Collections to query and their entity_type label + timestamp field
COLLECTIONS = [
    ("quality_events",    "QualityEvent",    "reported_at"),
    ("payment_events",    "PaymentEvent",    "invoice_date"),
    ("logistics_notes",   "LogisticsNote",   "scheduled_date"),
    ("semantic_patterns", "SemanticPattern", "first_observed_at"),
]


def fetch_supplier(db, name: str) -> dict:
    """Fetch supplier document by name (case-insensitive substring)."""
    supplier = db.suppliers.find_one(
        {"name": {"$regex": name, "$options": "i"}}
    )
    if not supplier:
        print(f"[ERROR] Supplier '{name}' not found in database.")
        sys.exit(1)
    return supplier


def fetch_all_events(db, supplier_id: str, supplier: dict) -> list:
    """
    Fetch all events across 4 collections for a given supplier_id.
    Enriches each document with entity_type, supplier_name, and category
    so the scoring engine has full context.
    """
    all_memories = []
    for col_name, entity_type, ts_field in COLLECTIONS:
        docs = list(db[col_name].find({"supplier_id": supplier_id}))
        for doc in docs:
            doc["entity_type"]   = entity_type
            doc["supplier_name"] = supplier.get("name", "")
            doc["category"]      = supplier.get("category", "")
            doc["_ts_field"]     = ts_field     # track which field is the timestamp
        all_memories.extend(docs)
    return all_memories


def print_ranked_table(ranked: list, supplier_name: str):
    """Print a formatted ranking table for all scored memories."""
    col_widths = {
        "rank":      4,
        "type":      16,
        "date":      12,
        "recency":   8,
        "severity":  9,
        "entity":    8,
        "final":     7,
        "freshness": 10,
        "stale":     6,
    }

    header = (
        f"{'Rank':<{col_widths['rank']}} "
        f"{'Type':<{col_widths['type']}} "
        f"{'Date':<{col_widths['date']}} "
        f"{'Recency':>{col_widths['recency']}} "
        f"{'Severity':>{col_widths['severity']}} "
        f"{'Entity':>{col_widths['entity']}} "
        f"{'Final':>{col_widths['final']}} "
        f"{'Freshness':<{col_widths['freshness']}} "
        f"{'Stale?':<{col_widths['stale']}}"
    )
    sep = "─" * len(header)

    print(f"\n{'═' * len(header)}")
    print(f"  MEMORY RANKING FOR: {supplier_name.upper()}")
    print(f"{'═' * len(header)}")
    print(header)
    print(sep)

    for rank, mem in enumerate(ranked, start=1):
        sc = mem.get("_scores", {})
        entity_type = mem.get("entity_type", "Unknown")

        # Resolve timestamp display
        ts_field = mem.get("_ts_field", "")
        date_str = (
            mem.get(ts_field)
            or mem.get("reported_at")
            or mem.get("invoice_date")
            or mem.get("scheduled_date")
            or mem.get("created_at", "—")
        )
        # Truncate to date-only for display
        date_display = str(date_str)[:10] if date_str else "—"

        freshness = get_freshness_label(mem)
        stale     = "YES ⚠" if is_stale(mem) else "no"

        print(
            f"{rank:<{col_widths['rank']}} "
            f"{entity_type:<{col_widths['type']}} "
            f"{date_display:<{col_widths['date']}} "
            f"{sc.get('recency', 0.0):>{col_widths['recency']}.4f} "
            f"{sc.get('severity', 0.0):>{col_widths['severity']}.4f} "
            f"{sc.get('entity_match', 0.0):>{col_widths['entity']}.4f} "
            f"{sc.get('final', 0.0):>{col_widths['final']}.4f} "
            f"{freshness:<{col_widths['freshness']}} "
            f"{stale:<{col_widths['stale']}}"
        )

    print(sep)
    print(f"  Total memories ranked: {len(ranked)}")
    print(f"{'═' * len(header)}\n")


def print_conflict_report(result: dict):
    """Print the conflict resolution output."""
    print(f"{'═' * 60}")
    print("  CONFLICT RESOLUTION REPORT")
    print(f"{'═' * 60}")
    print(f"  Flag              : {result['flag'].upper()}")
    print(f"  Historical Weight : {result['historical_weight']}")
    print(f"  Recent memories   : {result['recent_count']}")
    print(f"  Historical memories: {result['historical_count']}")
    print(f"  Recent avg severity   : {result['recent_avg_severity']}")
    print(f"  Historical max severity: {result['historical_max_severity']}")
    print(f"\n  Summary:")
    print(f"  {result['summary']}")
    print(f"{'═' * 60}\n")


def main():
    print("\n── Connecting to MongoDB ───────────────────────────────")
    db = get_database()

    print(f"\n── Fetching supplier: '{TARGET_SUPPLIER_NAME}' ──────────")
    supplier    = fetch_supplier(db, TARGET_SUPPLIER_NAME)
    supplier_id = supplier["supplier_id"]
    print(f"  Found: {supplier['name']} | ID: {supplier_id}")
    print(f"  Status: {supplier['compliance_status']} | Risk Score: {supplier['risk_score']}")

    print(f"\n── Fetching all events across 4 collections ────────────")
    memories = fetch_all_events(db, supplier_id, supplier)
    print(f"  Total memories fetched: {len(memories)}")

    if not memories:
        print("[WARN] No memories found. Run seed.py first.")
        sys.exit(0)

    # Build query context for entity matching
    query = {
        "supplier_id":   supplier_id,
        "supplier_name": supplier["name"],
        "category":      supplier.get("category", ""),
    }

    print(f"\n── Running scoring engine ──────────────────────────────")
    ranked = rank_memories(query, memories)

    print_ranked_table(ranked, supplier["name"])

    print(f"── Running conflict resolver ───────────────────────────")
    conflict = resolve_conflicts(memories)
    print_conflict_report(conflict)


if __name__ == "__main__":
    main()
