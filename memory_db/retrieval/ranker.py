# retrieval/ranker.py
# Scores, filters, and ranks memories — separates active from stale pool.

from engine.relevance import rank_memories
from engine.staleness import is_stale
from engine.conflict_resolver import resolve_conflicts


def rank_and_filter(parsed_query: dict, memories: list, top_n: int = 5) -> dict:
    """
    Score all memories, separate stale from active, resolve conflicts,
    and return the top N by relevance.

    Steps:
        1. Score every memory using the Phase 3 relevance engine.
        2. Split into active (not stale) and stale_pool (stale).
        3. Run conflict resolver on ALL severity-bearing memories
           (stale included — historical context matters for conflict detection).
        4. Return top N active memories by final score.

    Args:
        parsed_query: Structured query dict (supplier_id, supplier_name, etc.).
        memories:     Flat list of memory dicts from memory_fetcher.
        top_n:        Maximum number of memories to return in top_memories.

    Returns:
        dict: {
            "top_memories":  list — top N scored, active memories,
            "stale_pool":    list — stale memories (kept for audit/reference),
            "conflict_flag": str  — from conflict resolver,
            "total_fetched": int,
            "total_active":  int,
        }
    """
    if not memories:
        return {
            "top_memories":  [],
            "stale_pool":    [],
            "conflict_flag": "no_data",
            "total_fetched": 0,
            "total_active":  0,
        }

    # Build query context for entity matching
    query_ctx = {
        "supplier_id":   parsed_query.get("supplier_id", ""),
        "supplier_name": parsed_query.get("supplier_name", ""),
        "category":      parsed_query.get("category", ""),
    }

    # Step 1: Score all memories (rank_memories adds _scores key in-place)
    # Separate primary events (carry severity/timestamps) from wrapper types
    PRIMARY_TYPES   = {"QualityEvent", "PaymentEvent", "LogisticsNote", "SemanticPattern"}
    SECONDARY_TYPES = {"MemoryNode", "Supplier"}

    primary   = [m for m in memories if m.get("entity_type") in PRIMARY_TYPES]
    secondary = [m for m in memories if m.get("entity_type") in SECONDARY_TYPES]

    # Score primary events first; secondary used only if primary pool is empty
    pool_to_score = primary if primary else memories
    scored = rank_memories(query_ctx, pool_to_score)

    # Also score secondary for conflict resolution completeness
    scored_secondary = rank_memories(query_ctx, secondary) if secondary else []
    all_scored = scored + scored_secondary

    # Step 2: Split active vs stale — only from primary events
    active     = [m for m in scored if not is_stale(m)]
    stale_pool = [m for m in scored if is_stale(m)]

    # Step 3: Conflict resolution uses ALL scored memories (primary + secondary)
    # so historical signals in MemoryNodes also contribute
    conflict_result = resolve_conflicts(all_scored)
    conflict_flag   = conflict_result.get("flag", "no_data")

    # Step 4: Top N from active (already sorted descending by rank_memories)
    top_memories = active[:top_n]

    # If active pool is empty, fall back to top_n from stale (with a note)
    if not top_memories and stale_pool:
        top_memories = stale_pool[:top_n]
        for m in top_memories:
            m["_fallback_from_stale"] = True

    return {
        "top_memories":    top_memories,
        "stale_pool":      stale_pool,
        "conflict_flag":   conflict_flag,
        "conflict_detail": conflict_result,
        "total_fetched":   len(memories),
        "total_active":    len(active),
    }
