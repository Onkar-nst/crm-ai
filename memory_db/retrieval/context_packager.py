# retrieval/context_packager.py
# Builds a clean, decision-ready context bundle from the ranker output.

from datetime import datetime, timezone
from engine.staleness import get_freshness_label
from db.connection import get_database


# ── Recommendation rules (pure logic, no LLM) ────────────────────────────────

def _build_recommendation(conflict_flag: str, avg_severity: float) -> str:
    """
    Generate a deterministic recommendation string based on conflict flag
    and average severity of active memories.

    Args:
        conflict_flag: Output of conflict resolver (e.g., "improving").
        avg_severity:  Mean severity score (0.0–1.0) of active memories.

    Returns:
        str: Human-readable action recommendation.
    """
    flag = conflict_flag.lower()

    if flag == "deteriorating":
        return "Halt payment — escalate to procurement team immediately."
    if flag == "improving":
        return "Proceed with caution — quality improving but inspection advised."
    if flag == "inconsistent":
        return "Manual review required before processing."
    if flag in ("stable_good", "stable"):
        if avg_severity < 4 / 10:     # severity stored as 1–10; threshold 4
            return "Fast-track approved — supplier history is clean."
        return "Standard processing with quality check recommended."
    if flag == "stable_bad":
        return "Hold and escalate — persistent poor performance detected."
    if flag == "no_data":
        return "Insufficient history — apply standard onboarding checks."

    return "Standard processing — review context memories before approving."


def _action_hint(memory: dict) -> str:
    """
    Derive a short action hint based on entity type and severity.

    Returns one of: requires_inspection | flag_for_audit | verify_payment
                    check_delivery | review_pattern | standard_check
    """
    entity  = memory.get("entity_type", "")
    sev     = int(memory.get("severity", 0) or 0)
    loss    = float(memory.get("penalty_amount_inr") or memory.get("loss_amount") or 0)

    if entity == "QualityEvent" and sev >= 7:
        return "requires_inspection"
    if entity == "QualityEvent" and loss > 0:
        return "flag_for_audit"
    if entity == "PaymentEvent":
        status = memory.get("payment_status", "")
        if status in ("OVERDUE", "DISPUTED", "PARTIAL"):
            return "verify_payment"
    if entity == "LogisticsNote":
        cond = memory.get("condition", "")
        if cond in ("MINOR_DAMAGE", "MAJOR_DAMAGE", "REJECTED"):
            return "check_delivery"
    if entity == "SemanticPattern":
        return "review_pattern"

    return "standard_check"


def _build_summary(memory: dict) -> str:
    """Build a one-line human-readable summary from a memory document."""
    entity = memory.get("entity_type", "Unknown")

    if entity == "QualityEvent":
        rate   = memory.get("defect_rate", 0)
        cat    = memory.get("defect_category", "")
        sev    = memory.get("severity", 0)
        date   = memory.get("reported_at", "")[:10]
        loss   = memory.get("penalty_amount_inr") or 0
        loss_s = f", loss ₹{loss:,.0f}" if loss else ""
        return f"{rate*100:.0f}% {cat.lower()} defect — severity {sev}/10{loss_s} — reported {date}"

    if entity == "PaymentEvent":
        inv    = memory.get("invoice_id", "")
        amt    = memory.get("invoice_amount_inr", 0)
        status = memory.get("payment_status", "")
        delay  = memory.get("delay_days", 0)
        date   = memory.get("invoice_date", "")[:10]
        delay_s = f", {delay}d late" if delay and delay > 0 else (f", {abs(delay)}d early" if delay and delay < 0 else "")
        return f"{inv} ₹{amt:,.0f} — {status}{delay_s} — {date}"

    if entity == "LogisticsNote":
        shp    = memory.get("shipment_id", "")
        delay  = memory.get("delay_days", 0)
        cond   = memory.get("condition", "")
        date   = memory.get("scheduled_date", "")[:10]
        delay_s = f"{delay}d delay" if delay and delay > 0 else "on time"
        return f"{shp} — {delay_s}, condition: {cond} — scheduled {date}"

    if entity == "SemanticPattern":
        ptype = memory.get("pattern_type", "")
        conf  = memory.get("confidence", 0)
        desc  = memory.get("description", "")[:80]
        return f"[{ptype}] confidence={conf} — {desc}…"

    if entity == "Supplier":
        return (
            f"Supplier profile — status: {memory.get('compliance_status')}, "
            f"risk: {memory.get('risk_score')}, tier: {memory.get('tier')}"
        )

    if entity == "MemoryNode":
        return memory.get("content_summary", "Memory node (no summary)")

    return memory.get("content_summary", f"{entity} record")


def _compute_trust_score(supplier_doc: dict, conflict_flag: str) -> float:
    """
    Derive a simple trust score [0.0–1.0] from risk_score + conflict flag.
    trust_score = (1 - risk_score) adjusted by conflict flag.
    """
    base = 1.0 - float(supplier_doc.get("risk_score", 0.5))
    adjustments = {
        "improving":     0.0,
        "stable_good":   +0.05,
        "stable_bad":    -0.15,
        "deteriorating": -0.20,
        "inconsistent":  -0.05,
        "no_data":        0.0,
    }
    adjusted = base + adjustments.get(conflict_flag, 0.0)
    return round(max(0.0, min(1.0, adjusted)), 3)


def package_context(supplier_id: str, ranker_output: dict) -> dict:
    """
    Build a clean context bundle for agent decision-making from ranker output.

    Args:
        supplier_id:    Supplier's primary ID string.
        ranker_output:  Dict returned by ranker.rank_and_filter().

    Returns:
        dict: Complete context bundle with supplier profile, key memories,
              conflict flag, recommendation, and metadata.
    """
    db = get_database()

    # Fetch supplier doc (may already be in top_memories as enrichment)
    supplier_doc = db.suppliers.find_one({"supplier_id": supplier_id}, {"_id": 0})
    if not supplier_doc:
        supplier_doc = {}

    conflict_flag = ranker_output.get("conflict_flag", "no_data")
    top_memories  = ranker_output.get("top_memories", [])

    # Average severity of active memories (raw int 1–10)
    severities = [int(m.get("severity", 0) or 0) for m in top_memories if m.get("severity")]
    avg_sev    = sum(severities) / len(severities) if severities else 0.0

    # Build key_memories list
    key_memories = []
    for mem in top_memories:
        scores    = mem.get("_scores", {})
        freshness = get_freshness_label(mem)
        key_memories.append({
            "type":            mem.get("entity_type", "Unknown"),
            "summary":         _build_summary(mem),
            "relevance_score": scores.get("final", 0.0),
            "freshness":       freshness,
            "action_hint":     _action_hint(mem),
            "_raw":            mem,     # retained for explainer layer
        })

    # Supplier profile block
    supplier_block = {
        "name":        supplier_doc.get("name", "Unknown"),
        "trust_score": _compute_trust_score(supplier_doc, conflict_flag),
        "status":      supplier_doc.get("compliance_status", "UNKNOWN"),
        "tier":        supplier_doc.get("tier"),
        "risk_score":  supplier_doc.get("risk_score"),
        "category":    supplier_doc.get("category"),
    }

    return {
        "supplier":               supplier_block,
        "key_memories":           key_memories,
        "conflict_flag":          conflict_flag,
        "conflict_detail":        ranker_output.get("conflict_detail", {}),
        "recommendation":         _build_recommendation(conflict_flag, avg_sev),
        "stats": {
            "total_fetched": ranker_output.get("total_fetched", 0),
            "total_active":  ranker_output.get("total_active", 0),
            "total_stale":   len(ranker_output.get("stale_pool", [])),
        },
        "context_generated_at":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }
