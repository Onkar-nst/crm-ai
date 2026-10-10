# retrieval/memory_fetcher.py
# Fetches relevant memories from all 6 MongoDB collections in parallel threads.

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.connection import get_database


# Map collection → (entity_type label, primary timestamp field)
COLLECTION_MAP = {
    "suppliers":         ("Supplier",        "registered_on"),
    "quality_events":    ("QualityEvent",    "reported_at"),
    "payment_events":    ("PaymentEvent",    "invoice_date"),
    "logistics_notes":   ("LogisticsNote",   "scheduled_date"),
    "semantic_patterns": ("SemanticPattern", "first_observed_at"),
    "memory_nodes":      ("MemoryNode",      "created_at"),
}


def _resolve_supplier(db, parsed_query: dict) -> dict | None:
    """
    Resolve supplier from DB using supplier_id (exact) or name (regex).
    Mutates parsed_query to fill in supplier_id if found.

    Returns:
        Supplier document dict, or None if not found.
    """
    # Try exact ID first
    sid = parsed_query.get("supplier_id")
    if sid:
        sup = db.suppliers.find_one({"supplier_id": sid})
        if sup:
            return sup

    # Fall back to name regex
    name = parsed_query.get("supplier_name")
    if name:
        # Build a regex that matches any word from the name
        # e.g. "Supplier B" → matches "Delta Forge" if seeded with alias
        words = [re.escape(w) for w in name.split() if len(w) > 1]
        pattern = "|".join(words)
        sup = db.suppliers.find_one(
            {"name": {"$regex": pattern, "$options": "i"}}
        )
        if sup:
            parsed_query["supplier_id"] = sup["supplier_id"]
            return sup

    return None


def _fetch_from_collection(db, col_name: str, supplier_id: str,
                            supplier_name: str, supplier_doc: dict) -> list:
    """
    Fetch documents from a single collection matching the supplier.

    Enriches each document with:
        entity_type, supplier_name, category, _ts_field (primary timestamp key)

    Args:
        db:            MongoDB database object.
        col_name:      Collection name to query.
        supplier_id:   Exact supplier ID (primary match).
        supplier_name: Supplier name for regex fallback.
        supplier_doc:  Full supplier document for enrichment.

    Returns:
        list: Matched and enriched documents.
    """
    entity_type, ts_field = COLLECTION_MAP[col_name]

    # Suppliers collection — return the supplier doc itself as context
    if col_name == "suppliers":
        if supplier_doc:
            doc = dict(supplier_doc)
            doc["entity_type"]   = "Supplier"
            doc["supplier_name"] = supplier_doc.get("name", "")
            doc["category"]      = supplier_doc.get("category", "")
            doc["_ts_field"]     = ts_field
            doc.pop("_id", None)
            return [doc]
        return []

    # All other collections: filter by supplier_id
    query_filter = {"supplier_id": supplier_id} if supplier_id else {}
    if not query_filter:
        return []

    docs = list(db[col_name].find(query_filter, {"_id": 0}))
    for doc in docs:
        doc["entity_type"]   = entity_type
        doc["supplier_name"] = supplier_doc.get("name", "") if supplier_doc else supplier_name
        doc["category"]      = supplier_doc.get("category", "") if supplier_doc else ""
        doc["_ts_field"]     = ts_field
    return docs


def fetch_memories(parsed_query: dict) -> list:
    """
    Fetch all relevant memories for the supplier identified in parsed_query.

    Steps:
        1. Resolve supplier from DB (by ID or name regex).
        2. Fan out to all 6 collections in parallel using ThreadPoolExecutor.
        3. Flatten results into a single list.

    Args:
        parsed_query: Structured dict from query_parser.parse_query().
                      supplier_id is mutated in-place if found via name lookup.

    Returns:
        list: Flat list of all matched memory dicts, enriched with entity_type.
              Empty list if supplier not found.
    """
    db = get_database()

    # Step 1: Resolve supplier
    supplier_doc  = _resolve_supplier(db, parsed_query)
    supplier_id   = parsed_query.get("supplier_id") or ""
    supplier_name = parsed_query.get("supplier_name") or ""

    if not supplier_doc:
        print(f"  [WARN] No supplier matched for name='{supplier_name}' id='{supplier_id}'")
        return []

    # Step 2: Parallel fetch across all 6 collections
    all_memories = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(
                _fetch_from_collection,
                db, col_name, supplier_id, supplier_name, supplier_doc
            ): col_name
            for col_name in COLLECTION_MAP
        }
        for future in as_completed(futures):
            col_name = futures[future]
            try:
                docs = future.result()
                all_memories.extend(docs)
            except Exception as e:
                print(f"  [ERROR] Failed fetching {col_name}: {e}")

    return all_memories
