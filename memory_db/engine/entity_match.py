# engine/entity_match.py
# Scores how well a query's supplier reference matches a memory node's supplier context.


def get_entity_match_score(query: dict, memory: dict) -> float:
    """
    Returns an entity match score in [0.0, 1.0] based on how well the query
    references the supplier associated with a given memory.

    Match priority (highest wins, no additive stacking):
        1.0 → Exact supplier_id match
        0.7 → Supplier name is a substring of query text (case-insensitive)
        0.3 → Supplier category matches query category hint
        0.0 → No recognizable match

    Query dict keys used:
        "supplier_id"    (str) — exact ID to match
        "supplier_name"  (str) — name to do substring search on
        "category"       (str) — category hint (e.g., "Raw Materials")

    Memory dict keys used:
        "supplier_id"    (str) — ID on the memory node (denormalized FK)
        "supplier_name"  (str) — optional supplier name if enriched
        "category"       (str) — optional category if enriched

    Args:
        query:  Dict containing the incoming business query context.
        memory: Dict representing a MemoryNode or enriched event document.

    Returns:
        float: Match score — 1.0, 0.7, 0.3, or 0.0.
    """
    # ── Level 1: Exact supplier_id match ────────────────────────────────────
    q_id = (query.get("supplier_id") or "").strip()
    m_id = (memory.get("supplier_id") or "").strip()
    if q_id and m_id and q_id == m_id:
        return 1.0

    # ── Level 2: Supplier name substring match ───────────────────────────────
    q_name = (query.get("supplier_name") or "").strip().lower()
    m_name = (memory.get("supplier_name") or "").strip().lower()
    if q_name and m_name and (q_name in m_name or m_name in q_name):
        return 0.7

    # ── Level 3: Category match ──────────────────────────────────────────────
    q_cat = (query.get("category") or "").strip().lower()
    m_cat = (memory.get("category") or "").strip().lower()
    if q_cat and m_cat and q_cat == m_cat:
        return 0.3

    return 0.0
