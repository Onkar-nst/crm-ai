# models/memory_node.py
# Schema definition for MemoryNode — the universal wrapper for all memory entries.

memory_node_schema = {
    "node_id":            "string  — UUID4 primary key for this memory node",
    "memory_type":        "string  — Enum: WORKING | EPISODIC | SEMANTIC",
    "entity_type":        "string  — Enum: SUPPLIER | QUALITY_EVENT | PAYMENT_EVENT | LOGISTICS_NOTE | SEMANTIC_PATTERN",
    "entity_id":          "string  — Foreign key referencing the wrapped entity's primary ID",
    "supplier_id":        "string  — Denormalized supplier FK for fast retrieval without joins",
    "content_summary":    "string  — One-line human-readable summary of what this node represents",
    "created_at":         "string  — ISO 8601 datetime when this node was first recorded",
    "last_accessed_at":   "string  — ISO 8601 datetime of last retrieval by the agent",
    "access_count":       "int     — Number of times this node has been retrieved",
    "relevance_score":    "float   — Current computed relevance 0.0–1.0",
    "freshness_state":    "string  — Enum: FRESH | AGING | STALE | EVERGREEN",
    "decay_rate":         "float   — Per-day decay constant (0.0 for EVERGREEN nodes)",
    "source_session_id":  "string  — Session ID that created this node (null for seeded data)",
    "linked_node_ids":    "list    — List of related node_id strings (graph edges)",
    "confidence_score":   "float   — Data reliability 0.0–1.0 (1.0 = verified/audited fact)",
}

# ── Example document ────────────────────────────────────────────────────────
memory_node_example = {
    "node_id":            "mn-f9e8d7c6-0001",
    "memory_type":        "EPISODIC",
    "entity_type":        "QUALITY_EVENT",
    "entity_id":          "qe-11223344-0001",
    "supplier_id":        "sup-a1b2c3d4-0001",
    "content_summary":    "Supplier A: Minor cosmetic defect (2%) in Batch B-0021, Aug 2024. Resolved.",
    "created_at":         "2024-08-20T10:30:00Z",
    "last_accessed_at":   "2025-01-10T09:00:00Z",
    "access_count":       4,
    "relevance_score":    0.62,
    "freshness_state":    "AGING",
    "decay_rate":         0.003,
    "source_session_id":  None,
    "linked_node_ids":    ["mn-aabbccdd-0002"],
    "confidence_score":   0.95,
}
