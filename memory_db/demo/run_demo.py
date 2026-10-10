# demo/run_demo.py
# Simulates a full business day with end-to-end memory retrieval and updates.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.pipeline import run_pipeline
from app.edge_cases import apply_edge_cases
from app.memory_updater import update_memory
from db.connection import get_database

def print_bundle(title: str, bundle: dict):
    print(f"\n{'═'*60}\n{title}\n{'═'*60}")
    supplier = bundle.get("supplier", {})
    print(f"Supplier   : {supplier.get('name')}")
    print(f"Trust Score: {supplier.get('trust_score')}")
    print(f"Conflict   : {bundle.get('conflict_flag')}")
    print(f"Recommend  : {bundle.get('recommendation')}")
    print(f"\nKey Memories ({len(bundle.get('key_memories', []))} shown):")
    for i, mem in enumerate(bundle.get('key_memories', [])[:3], 1):
        print(f"  [{i}] {mem.get('type')} - {mem.get('summary')}")
        print(f"      Relevance: {mem.get('relevance_score'):.2f}")
    print("\n")

def run_query(query: str):
    bundle = run_pipeline(query, top_n=5)
    return apply_edge_cases(bundle, bundle.get("key_memories", []), bundle.get("stale_pool", []))

def simulate_day():
    db = get_database()
    sup = db.suppliers.find_one({"name": {"$regex": "Delta Forge", "$options": "i"}})
    if not sup:
        print("Delta Forge not found. Run seed.py first.")
        return
        
    sup_id = sup["supplier_id"]
    query = "Invoice received from Delta Forge for ₹2,50,000 — process payment"
    
    # MORNING
    print("\n[MORNING] Invoice arrives. Pipeline runs.")
    bundle_morning = run_query(query)
    print_bundle("MORNING CONTEXT", bundle_morning)
    
    # AFTERNOON
    print(f"[AFTERNOON] Quality inspection passed. Adding new QualityEvent with low severity (2).")
    event_data = {
        "supplier_id": sup_id,
        "severity": 2,
        "root_cause_summary": "Passed spot check, minor scratch (acceptable).",
        "resolution_status": "RESOLVED"
    }
    updated_sup = update_memory("QualityEvent", event_data)
    print(f"  -> Memory updated. New Trust Score: {round(1.0 - updated_sup.get('risk_score', 0.5), 2)}")
    
    # EVENING
    print("\n[EVENING] Processing same invoice again. Pipeline runs.")
    bundle_evening = run_query(query)
    print_bundle("EVENING CONTEXT (Updated)", bundle_evening)

if __name__ == "__main__":
    simulate_day()
