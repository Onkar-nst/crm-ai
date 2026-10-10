# app/edge_cases.py
# Handles edge cases in retrieval pipeline output

def apply_edge_cases(bundle: dict, active_memories: list, stale_pool: list) -> dict:
    """
    Apply edge case logic to the context bundle.
    
    1. Unknown supplier -> Error (handled upstream usually, but checked here)
    2. No memories found -> Special recommendation
    3. All memories stale -> Stale pool returned with warning
    4. Conflicting recent data -> "too_recent_to_judge" flag
    """
    if bundle.get("error") == "no_memories_found" or not bundle.get("supplier"):
        return {
            "error": "supplier_not_found",
            "suggestion": "Add this supplier first"
        }

    # 4. Conflicting recent data
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    recent_events = []
    
    for mem in active_memories:
        ts_field = mem.get("_ts_field") or "reported_at"
        ts_val = mem.get(ts_field)
        if not ts_val: continue
        try:
            ts_str = ts_val.replace("Z", "+00:00")
            if "T" in ts_str:
                dt = datetime.datetime.fromisoformat(ts_str)
            else:
                dt = datetime.datetime.fromisoformat(ts_str).replace(tzinfo=datetime.timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            days_old = (now - dt).total_seconds() / 86400
            if days_old <= 30:
                recent_events.append(mem)
        except:
            pass

    # Check contradiction in recent events (one high severity, one low severity)
    if len(recent_events) >= 2:
        high_sev = [m for m in recent_events if float(m.get("severity", 0)) > 6]
        low_sev = [m for m in recent_events if float(m.get("severity", 0)) > 0 and float(m.get("severity", 0)) <= 3]
        if high_sev and low_sev:
            bundle["conflict_flag"] = "too_recent_to_judge"
            bundle["recommendation"] = "Conflicting events in last 30 days — too recent to judge. Review raw events without automated recommendation."
            return bundle

    # 2. No memories found
    if not active_memories and not stale_pool:
        bundle["recommendation"] = "No history found — treat as new supplier, apply standard checks"
        return bundle

    # 3. All memories stale
    if not active_memories and stale_pool:
        bundle["recommendation"] = "All context is older than relevance window — verify manually"
        # Move stale pool to key memories to show them
        bundle["key_memories"] = []
        for stale in stale_pool[:5]:
            bundle["key_memories"].append({
                "type": stale.get("entity_type", "Unknown"),
                "summary": stale.get("content_summary", "Stale memory"),
                "relevance_score": stale.get("_scores", {}).get("final", 0.0),
                "freshness": "stale",
                "action_hint": "manual_verification_required",
                "why_retrieved": "Included from stale pool because no active memories exist."
            })
        return bundle

    return bundle
