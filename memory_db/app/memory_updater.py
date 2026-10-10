# app/memory_updater.py
# End-to-end memory update flow

import uuid
from datetime import datetime, timezone
from db.connection import get_database

def _get_avg_severity_and_resolved(db, supplier_id: str) -> tuple[float, float]:
    """Calculate avg severity in last 6 months and resolved ratio for QualityEvents."""
    now = datetime.now(timezone.utc)
    events = list(db.quality_events.find({"supplier_id": supplier_id}))
    
    recent_severities = []
    resolved_count = 0
    total_events = len(events)
    
    for event in events:
        if event.get("resolution_status") == "RESOLVED":
            resolved_count += 1
            
        ts_val = event.get("reported_at")
        if not ts_val: continue
        try:
            ts_str = ts_val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts_str) if "T" in ts_str else datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            days_old = (now - dt).total_seconds() / 86400
            if days_old <= 180:
                recent_severities.append(float(event.get("severity", 0)))
        except:
            pass
            
    avg_sev = sum(recent_severities) / len(recent_severities) if recent_severities else 0.0
    resolved_ratio = resolved_count / total_events if total_events > 0 else 1.0
    return avg_sev, resolved_ratio

def update_memory(event_type: str, event_data: dict) -> dict:
    """
    Inserts a new event into MongoDB and updates supplier profile.
    """
    db = get_database()
    supplier_id = event_data.get("supplier_id")
    if not supplier_id:
        return {"error": "Missing supplier_id"}
        
    supplier = db.suppliers.find_one({"supplier_id": supplier_id})
    if not supplier:
        return {"error": "Supplier not found"}

    # Insert event
    event_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # We map collection based on event_type
    col_map = {
        "QualityEvent": "quality_events",
        "PaymentEvent": "payment_events",
        "LogisticsNote": "logistics_notes",
    }
    
    col_name = col_map.get(event_type)
    if not col_name:
        return {"error": f"Unknown event type {event_type}"}
        
    # Standardize ID field based on type
    id_field = {"QualityEvent": "event_id", "PaymentEvent": "payment_id", "LogisticsNote": "note_id"}[event_type]
    event_data[id_field] = event_id
    
    # Insert raw event
    db[col_name].insert_one(event_data)
    
    # Insert MemoryNode wrapper
    db.memory_nodes.insert_one({
        "node_id": str(uuid.uuid4()),
        "memory_type": "EPISODIC",
        "entity_type": event_type,
        "entity_id": event_id,
        "supplier_id": supplier_id,
        "content_summary": event_data.get("root_cause_summary") or event_data.get("deduction_reason") or event_data.get("notes") or f"New {event_type}",
        "created_at": now_iso,
        "last_accessed_at": now_iso,
        "access_count": 0,
        "relevance_score": 1.0,
        "freshness_state": "FRESH",
        "decay_rate": 0.003,
        "source_session_id": None,
        "confidence_score": 0.9,
    })

    # Logic per type
    if event_type == "QualityEvent":
        avg_sev, resolved_ratio = _get_avg_severity_and_resolved(db, supplier_id)
        # trust_score = 1.0 - (avg_severity_last_6_months / 10) + (resolved_ratio * 0.2)
        trust_score = 1.0 - (avg_sev / 10.0) + (resolved_ratio * 0.2)
        trust_score = min(1.0, max(0.0, trust_score))
        risk_score = 1.0 - trust_score
        db.suppliers.update_one({"supplier_id": supplier_id}, {"$set": {"risk_score": risk_score}})
        supplier["risk_score"] = risk_score
        
    elif event_type == "PaymentEvent":
        if event_data.get("payment_status") == "DISPUTED":
            db.suppliers.update_one({"supplier_id": supplier_id}, {"$set": {"compliance_status": "PROBATION"}})
            supplier["compliance_status"] = "PROBATION"
            
    elif event_type == "LogisticsNote":
        tags = supplier.get("tags", [])
        is_seasonal = "monsoon" in event_data.get("notes", "").lower() or "monsoon" in str(tags).lower()
        if is_seasonal:
            # Check if semantic pattern exists
            pattern = db.semantic_patterns.find_one({"supplier_id": supplier_id, "pattern_type": "DELIVERY_TREND"})
            if pattern:
                new_confidence = min(1.0, pattern.get("confidence", 0.0) + 0.05)
                db.semantic_patterns.update_one({"pattern_id": pattern["pattern_id"]}, {"$set": {"confidence": new_confidence}})

    return supplier
