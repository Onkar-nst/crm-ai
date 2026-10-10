# retrieval/test_pipeline.py
# Runs 3 business queries through the full retrieval pipeline and prints results.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.pipeline import run_pipeline

# ── Test queries ──────────────────────────────────────────────────────────────
QUERIES = [
    "Invoice received from Delta Forge for ₹2,50,000 — process payment",
    "Delivery expected from Coastal Freight next week — monsoon season",
    "Payment request from RajTech for ₹75,000",
]

QUERY_LABELS = ["Query 1 — Supplier B (Delta Forge)", "Query 2 — Supplier C (Coastal Freight)", "Query 3 — Supplier A (RajTech)"]

# ── Pretty printer ────────────────────────────────────────────────────────────

def print_context_bundle(bundle: dict, label: str):
    """Print a formatted context bundle to stdout."""

    W = 72  # width
    print(f"\n{'═' * W}")
    print(f"  {label}")
    print(f"{'═' * W}")

    # Error check
    if "error" in bundle:
        print(f"  ❌ Pipeline error: {bundle['error']}")
        if "suggestion" in bundle:
            print(f"  💡 {bundle['suggestion']}")
        return

    # Supplier
    sup = bundle.get("supplier", {})
    print(f"\n  SUPPLIER")
    print(f"  {'─'*40}")
    print(f"  Name        : {sup.get('name')}")
    print(f"  Status      : {sup.get('status')}   Tier: {sup.get('tier')}")
    print(f"  Risk Score  : {sup.get('risk_score')}   Trust Score: {sup.get('trust_score')}")
    print(f"  Category    : {sup.get('category')}")

    # Stats
    stats = bundle.get("stats", {})
    print(f"\n  RETRIEVAL STATS")
    print(f"  {'─'*40}")
    print(f"  Fetched: {stats.get('total_fetched')}   Active: {stats.get('total_active')}   Stale: {stats.get('total_stale')}")
    print(f"  Conflict Flag: {bundle.get('conflict_flag', '—').upper()}")

    # Recommendation
    print(f"\n  RECOMMENDATION")
    print(f"  {'─'*40}")
    print(f"  ➤ {bundle.get('recommendation')}")

    # Key Memories
    key_mems = bundle.get("key_memories", [])
    print(f"\n  KEY MEMORIES  ({len(key_mems)} shown)")
    print(f"  {'─'*40}")

    for i, mem in enumerate(key_mems, 1):
        fallback = mem.get("_raw", {}).get("_fallback_from_stale", False)
        fb_note = " [stale fallback]" if fallback else ""
        print(f"\n  [{i}] {mem.get('type')}{fb_note}")
        print(f"      Summary   : {mem.get('summary')}")
        print(f"      Relevance : {mem.get('relevance_score'):.4f}   Freshness: {mem.get('freshness')}")
        print(f"      Action    : {mem.get('action_hint')}")
        print(f"      Why       : {mem.get('why_retrieved', '—')}")

    # Pipeline meta
    meta = bundle.get("_pipeline", {})
    elapsed = meta.get("total_elapsed_ms", 0)
    print(f"\n  ⏱  Pipeline completed in {elapsed:.1f} ms")
    print(f"{'═' * W}")


def print_summary_table(results: list):
    """Print a final cross-query summary table."""
    print(f"\n\n{'═' * 72}")
    print("  PIPELINE SUMMARY — ALL 3 QUERIES")
    print(f"{'═' * 72}")
    header = f"{'Query':<10} {'Fetched':>8} {'Active':>7} {'Stale':>6} {'Conflict':<14} {'Time(ms)':>9}"
    print(f"  {header}")
    print(f"  {'─'*68}")
    for i, (bundle, label) in enumerate(results, 1):
        if "error" in bundle:
            print(f"  Q{i:<9} {'ERROR':>8}")
            continue
        stats   = bundle.get("stats", {})
        flag    = bundle.get("conflict_flag", "—").upper()
        elapsed = bundle.get("_pipeline", {}).get("total_elapsed_ms", 0)
        print(
            f"  Q{i:<9} "
            f"{stats.get('total_fetched', 0):>8} "
            f"{stats.get('total_active', 0):>7} "
            f"{stats.get('total_stale', 0):>6} "
            f"{flag:<14} "
            f"{elapsed:>9.1f}"
        )
    print(f"  {'─'*68}")
    print(f"{'═' * 72}\n")


def main():
    print("\n" + "═" * 72)
    print("  CONTEXT & MEMORY MANAGEMENT SYSTEM — RETRIEVAL PIPELINE TEST")
    print("  Phase 4 — Full Pipeline (Parse → Fetch → Rank → Package → Explain)")
    print("═" * 72)

    results = []
    for raw_query, label in zip(QUERIES, QUERY_LABELS):
        print(f"\n  ▶ Running: {label}")
        print(f"    Query: \"{raw_query}\"")
        bundle = run_pipeline(raw_query, top_n=5, verbose=True)
        print_context_bundle(bundle, label)
        results.append((bundle, label))

    print_summary_table(results)


if __name__ == "__main__":
    main()
