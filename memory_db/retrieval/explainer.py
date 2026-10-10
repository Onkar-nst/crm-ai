# retrieval/explainer.py
# Adds a plain-English 'why_retrieved' explanation to each memory in a context bundle.

from engine.staleness import get_freshness_label


def _explain_memory(mem_entry: dict) -> str:
    """
    Build a plain-English explanation for why a memory was retrieved.

    Rules (all applicable rules are combined into one sentence):
        - Mention recency score if > 0.7 (very recent)
        - Mention severity if raw severity > 6
        - Mention financial loss if > 0
        - Always mention staleness/freshness label
        - Mention entity type and its role

    Args:
        mem_entry: A dict from context bundle's key_memories list.
                   Must contain 'type', 'freshness', '_raw', and scores.

    Returns:
        str: Human-readable explanation of retrieval reasoning.
    """
    raw       = mem_entry.get("_raw", {})
    scores    = raw.get("_scores", {})
    entity    = mem_entry.get("type", "Unknown")
    freshness = mem_entry.get("freshness", "unknown")
    final     = scores.get("final", 0.0)
    recency   = scores.get("recency", 0.0)
    severity_score = scores.get("severity", 0.0)

    # Raw values
    raw_sev  = int(raw.get("severity", 0) or 0)
    loss     = float(raw.get("penalty_amount_inr") or raw.get("loss_amount") or 0)
    ts_field = raw.get("_ts_field", "")
    date_val = raw.get(ts_field) or raw.get("reported_at") or raw.get("invoice_date") or ""
    date_str = str(date_val)[:10] if date_val else "unknown date"

    parts = []

    # Entity type context
    entity_context = {
        "QualityEvent":    "quality incident",
        "PaymentEvent":    "payment record",
        "LogisticsNote":   "logistics record",
        "SemanticPattern": "behavioral pattern derived from historical data",
        "Supplier":        "supplier profile record",
        "MemoryNode":      "memory node",
    }
    parts.append(f"{entity_context.get(entity, entity)} from {date_str}")

    # Recency
    if recency > 0.7:
        parts.append(f"retrieved due to high recency (score {recency:.2f} — event is very recent)")
    elif recency > 0.3:
        parts.append(f"recency score {recency:.2f} — within active relevance window")
    else:
        parts.append(f"low recency (score {recency:.2f}) but included for historical context")

    # Severity
    if raw_sev > 6:
        parts.append(f"high severity {raw_sev}/10 (score {severity_score:.2f})")
    elif raw_sev > 0:
        parts.append(f"severity {raw_sev}/10 (score {severity_score:.2f})")

    # Financial loss
    if loss > 0:
        parts.append(f"financial impact ₹{loss:,.0f} applied severity multiplier")

    # Staleness label — always included
    freshness_desc = {
        "fresh":     "memory is FRESH — within primary relevance window",
        "aging":     "memory is AGING — approaching staleness threshold",
        "stale":     "memory is STALE — included as fallback historical reference",
        "evergreen": "memory is EVERGREEN — never expires (high-confidence pattern)",
    }
    parts.append(freshness_desc.get(freshness, f"freshness: {freshness}"))

    # Final score
    parts.append(f"final relevance score: {final:.4f}")

    return ". ".join(parts) + "."


def explain_context(context_bundle: dict) -> dict:
    """
    Enriches each memory in key_memories with a 'why_retrieved' field.

    This function mutates the context_bundle in-place and also returns it,
    allowing chaining in the pipeline.

    Args:
        context_bundle: Dict returned by context_packager.package_context().

    Returns:
        dict: Same bundle with 'why_retrieved' added to each key_memory entry.
    """
    for mem_entry in context_bundle.get("key_memories", []):
        mem_entry["why_retrieved"] = _explain_memory(mem_entry)

    return context_bundle
