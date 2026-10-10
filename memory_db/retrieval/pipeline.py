# retrieval/pipeline.py
# Single entry point that chains all retrieval stages end-to-end.

import time
from retrieval.query_parser    import parse_query
from retrieval.memory_fetcher  import fetch_memories
from retrieval.ranker          import rank_and_filter
from retrieval.context_packager import package_context
from retrieval.explainer       import explain_context


def run_pipeline(raw_query: str, top_n: int = 5, verbose: bool = False) -> dict:
    """
    Full retrieval pipeline: raw query → structured context bundle.

    Stages:
        1. parse_query       — extract structured fields from raw string
        2. fetch_memories    — pull all relevant docs from MongoDB (parallel)
        3. rank_and_filter   — score, separate stale, resolve conflicts
        4. package_context   — build clean context bundle with recommendation
        5. explain_context   — annotate each memory with why_retrieved

    Args:
        raw_query: Natural language business query string.
        top_n:     Max number of memories to include in key_memories.
        verbose:   If True, print timing for each stage.

    Returns:
        dict: Final context bundle with all stages applied.
              Contains 'error' key if pipeline fails at any stage.
    """
    t_start = time.perf_counter()

    try:
        # ── Stage 1: Parse ───────────────────────────────────────────────────
        t0 = time.perf_counter()
        parsed = parse_query(raw_query)
        if verbose:
            print(f"  [parse]   {(time.perf_counter()-t0)*1000:.1f}ms → {parsed}")

        # ── Stage 2: Fetch ───────────────────────────────────────────────────
        t0 = time.perf_counter()
        memories = fetch_memories(parsed)
        if verbose:
            print(f"  [fetch]   {(time.perf_counter()-t0)*1000:.1f}ms → {len(memories)} docs")

        if not memories:
            return {
                "error":      "no_memories_found",
                "query":      raw_query,
                "parsed":     parsed,
                "suggestion": "Check supplier name spelling or run seed.py to populate data.",
            }

        # ── Stage 3: Rank + Filter ───────────────────────────────────────────
        t0 = time.perf_counter()
        ranker_output = rank_and_filter(parsed, memories, top_n=top_n)
        if verbose:
            print(f"  [rank]    {(time.perf_counter()-t0)*1000:.1f}ms "
                  f"→ active={ranker_output['total_active']}, "
                  f"stale={len(ranker_output['stale_pool'])}, "
                  f"flag={ranker_output['conflict_flag']}")

        # ── Stage 4: Package ─────────────────────────────────────────────────
        t0 = time.perf_counter()
        supplier_id = parsed.get("supplier_id", "")
        bundle = package_context(supplier_id, ranker_output)
        if verbose:
            print(f"  [package] {(time.perf_counter()-t0)*1000:.1f}ms → bundle ready")

        # ── Stage 5: Explain ─────────────────────────────────────────────────
        t0 = time.perf_counter()
        bundle = explain_context(bundle)
        if verbose:
            print(f"  [explain] {(time.perf_counter()-t0)*1000:.1f}ms → why_retrieved added")

        # Attach pipeline metadata
        bundle["_pipeline"] = {
            "raw_query":        raw_query,
            "parsed_query":     parsed,
            "total_elapsed_ms": round((time.perf_counter() - t_start) * 1000, 1),
        }
        return bundle

    except Exception as exc:
        return {
            "error":     str(exc),
            "query":     raw_query,
            "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 1),
        }
