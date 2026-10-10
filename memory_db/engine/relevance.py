# engine/relevance.py
# Combines recency, severity, and entity match into a single relevance score.
# Also provides rank_memories() to sort a list of memories by final score.

from engine.recency import get_recency_score
from engine.severity import get_severity_score
from engine.entity_match import get_entity_match_score

# Scoring weights — must sum to 1.0
WEIGHT_RECENCY      = 0.40
WEIGHT_SEVERITY     = 0.35
WEIGHT_ENTITY_MATCH = 0.25


def get_relevance_score(query: dict, memory: dict) -> float:
    """
    Returns a composite relevance score in [0.0, 1.0].

    Formula:
        relevance = (0.40 × recency) + (0.35 × severity) + (0.25 × entity_match)

    Timestamp resolution order (first found wins):
        memory["reported_at"] → memory["invoice_date"] → memory["scheduled_date"]
        → memory["created_at"] → memory["first_observed_at"]

    Severity and loss_amount are read from the memory dict directly.
    Entity match uses query["supplier_id"] / ["supplier_name"] / ["category"].

    Args:
        query:  Dict with at least one of: supplier_id, supplier_name, category.
        memory: MemoryNode or enriched event dict.

    Returns:
        float: Weighted relevance score rounded to 4 decimal places.
    """
    # ── Recency ──────────────────────────────────────────────────────────────
    timestamp = (
        memory.get("reported_at")
        or memory.get("invoice_date")
        or memory.get("scheduled_date")
        or memory.get("created_at")
        or memory.get("first_observed_at")
    )
    recency = get_recency_score(timestamp) if timestamp else 0.1

    # ── Severity ─────────────────────────────────────────────────────────────
    raw_severity = memory.get("severity", 0)
    loss = memory.get("penalty_amount_inr") or memory.get("loss_amount") or 0.0
    severity = get_severity_score(raw_severity, loss) if raw_severity else 0.0

    # ── Entity Match ─────────────────────────────────────────────────────────
    entity = get_entity_match_score(query, memory)

    # ── Composite Score ───────────────────────────────────────────────────────
    score = (
        WEIGHT_RECENCY      * recency
        + WEIGHT_SEVERITY   * severity
        + WEIGHT_ENTITY_MATCH * entity
    )
    return round(min(1.0, max(0.0, score)), 4)


def rank_memories(query: dict, memories: list) -> list:
    """
    Sorts a list of memory dicts by their relevance score (descending).

    Each memory dict in the returned list is enriched with a "_scores" key:
        {
            "recency":      float,
            "severity":     float,
            "entity_match": float,
            "final":        float,
        }

    Args:
        query:    Dict with supplier context for entity matching.
        memories: List of memory / event dicts to rank.

    Returns:
        list: Memories sorted by final relevance score, highest first.
    """
    scored = []
    for mem in memories:
        # Re-compute individual components for reporting
        timestamp = (
            mem.get("reported_at")
            or mem.get("invoice_date")
            or mem.get("scheduled_date")
            or mem.get("created_at")
            or mem.get("first_observed_at")
        )
        recency  = get_recency_score(timestamp) if timestamp else 0.1
        raw_sev  = mem.get("severity", 0)
        loss     = mem.get("penalty_amount_inr") or mem.get("loss_amount") or 0.0
        severity = get_severity_score(raw_sev, loss) if raw_sev else 0.0
        entity   = get_entity_match_score(query, mem)
        final    = get_relevance_score(query, mem)

        mem["_scores"] = {
            "recency":      recency,
            "severity":     severity,
            "entity_match": entity,
            "final":        final,
        }
        scored.append(mem)

    scored.sort(key=lambda m: m["_scores"]["final"], reverse=True)
    return scored
