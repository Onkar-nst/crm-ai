import sys
import os
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.pipeline import run_pipeline
from db.connection import get_database
from engine.relevance import rank_memories

def measure_average_retrieval():
    db = get_database()
    sup = db.suppliers.find_one()
    if not sup: return 0
    query = f"Query for {sup['name']}"
    
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        run_pipeline(query)
        times.append(time.perf_counter() - t0)
    
    return (sum(times) / 10) * 1000  # ms

def simulate_100_suppliers():
    db = get_database()
    
    # Insert dummy
    dummies = []
    for i in range(100):
        dummies.append({"supplier_id": f"DUMMY_{uuid.uuid4()}", "name": f"Dummy Supplier {i}", "risk_score": 0.5})
    db.suppliers.insert_many(dummies)
    
    t0 = time.perf_counter()
    run_pipeline("Query for Dummy Supplier 50")
    t1 = time.perf_counter()
    
    # Cleanup
    db.suppliers.delete_many({"supplier_id": {"$regex": "^DUMMY_"}})
    return (t1 - t0) * 1000

def measure_ranking():
    # 50 vs 500
    mems_50 = [{"entity_type": "QualityEvent", "severity": i%10, "reported_at": "2024-01-01T00:00:00Z"} for i in range(50)]
    mems_500 = [{"entity_type": "QualityEvent", "severity": i%10, "reported_at": "2024-01-01T00:00:00Z"} for i in range(500)]
    
    ctx = {"supplier_id": "TEST"}
    t0 = time.perf_counter()
    rank_memories(ctx, mems_50)
    t50 = (time.perf_counter() - t0) * 1000
    
    t0 = time.perf_counter()
    rank_memories(ctx, mems_500)
    t500 = (time.perf_counter() - t0) * 1000
    
    return t50, t500

def measure_mongodb_query():
    db = get_database()
    sup = db.suppliers.find_one()
    sid = sup["supplier_id"] if sup else "N/A"
    
    # Indexed query (supplier_id)
    t0 = time.perf_counter()
    list(db.quality_events.find({"supplier_id": sid}))
    t_indexed = (time.perf_counter() - t0) * 1000
    
    # Unindexed query (resolution_status = OPEN)
    t0 = time.perf_counter()
    list(db.quality_events.find({"resolution_status": "OPEN"}))
    t_unindexed = (time.perf_counter() - t0) * 1000
    
    return t_indexed, t_unindexed

if __name__ == "__main__":
    print("Running Performance Evaluation...")
    avg_1 = measure_average_retrieval()
    time_100 = simulate_100_suppliers()
    rank_50, rank_500 = measure_ranking()
    q_idx, q_no_idx = measure_mongodb_query()
    
    print("\n" + "="*50)
    print(" PERFORMANCE EVALUATION RESULTS")
    print("="*50)
    print(f"| Metric                               | Time (ms) |")
    print(f"|--------------------------------------|-----------|")
    print(f"| Avg Retrieval (1 Supplier, 10 runs)  | {avg_1:8.2f}  |")
    print(f"| Retrieval w/ 100 Suppliers in DB     | {time_100:8.2f}  |")
    print(f"| Memory Ranking (50 items)            | {rank_50:8.2f}  |")
    print(f"| Memory Ranking (500 items)           | {rank_500:8.2f}  |")
    print(f"| MongoDB Query (Indexed field)        | {q_idx:8.2f}  |")
    print(f"| MongoDB Query (Unindexed field)      | {q_no_idx:8.2f}  |")
    print("="*50)
