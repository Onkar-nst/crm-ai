# Context and Memory Management System - Final Report

## 1. Project Overview
The Context and Memory Management System is a comprehensive, deterministic intelligence layer designed for AI agents operating in business environments. Instead of relying purely on expensive and hallucination-prone Large Language Models (LLMs) to retrieve relevant historical data, this system utilizes a mathematical scoring engine (evaluating recency, severity, and semantic staleness) running on top of MongoDB Atlas. It processes natural language queries, fetches related supplier memories concurrently, resolves behavioral conflicts, and returns a clean, highly explainable context bundle that an AI agent can use to make safe, reliable, and auditable business decisions.

## 2. Architecture Diagram

```text
[ Business Query ]  e.g., "Invoice from Delta Forge..."
        │
        ▼
┌──────────────────────────────────────────────┐
│ Phase 4: Retrieval Pipeline (Python)         │
│                                              │
│ 1. query_parser      (Regex extraction)      │
│ 2. memory_fetcher    (Parallel DB queries)   │
│ 3. rank_and_filter   (Mathematical ranking)  │
│ 4. context_packager  (Bundle construction)   │
│ 5. explainer         (Explainability tags)   │
└───────────────────────┬──────────────────────┘
                        │
                  ┌─────┴─────┐
                  ▼           ▼
   ┌─────────────────┐     ┌─────────────────┐
   │ Phase 3: Engine │     │ Phase 5: Web UI │
   │ - Recency Decay │     │ - FastAPI server│
   │ - Severity Mult │◄────┤ - Memory Updater│
   │ - Staleness     │     │ - Trust Scoring │
   └───────┬─────────┘     └─────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ Phase 2: MongoDB Atlas (Data Layer)          │
│ Collections: Suppliers, QualityEvents,       │
│ PaymentEvents, LogisticsNotes, Semantic,     │
│ MemoryNodes (Universal Wrapper)              │
└──────────────────────────────────────────────┘
```

## 3. Phase-wise Summary
* **Phase 1 (Architecture & Schema):** Designed a three-tier memory structure (Working, Episodic, Semantic) and created robust JSON schemas for the six core entities necessary to represent a business supplier ecosystem.
* **Phase 2 (Data Layer):** Connected a Python application to MongoDB Atlas, implementing schemas, creating optimized compound indexes, and seeding the database with hyper-realistic mock transactions.
* **Phase 3 (Scoring Engine):** Developed a pure Python mathematical ranking engine utilizing exponential decay for recency, business-impact multipliers for severity, and dynamic staleness thresholds (including evergreen semantic patterns).
* **Phase 4 (Retrieval Pipeline):** Built the end-to-end processing pipeline that parses a raw query, fetches documents via parallel threads, scores them, resolves historical performance conflicts, and packages an explainable context bundle.
* **Phase 5 (API & Demo):** Wrapped the pipeline in a FastAPI backend, designed a clean Vanilla HTML/JS frontend to visualize results, and implemented a memory update loop that dynamically recalculates supplier trust scores when new events occur.

## 4. Key Design Decisions

1. **Exponential Decay for Recency:**
   *Reasoning:* Business relevance naturally follows an exponential curve rather than a linear one. An invoice delay from 3 days ago is critical, an invoice delay from 45 days ago is relevant context, but a delay from 400 days ago is largely obsolete. The formula `e^(-λ * days)` smoothly deprioritizes old events while ensuring highly severe old events can still mathematically bubble to the top via the severity multiplier.

2. **Weighted Mathematical Scoring vs. LLM Ranking:**
   *Reasoning:* LLMs are non-deterministic, slow, and expensive at scale. By using mathematical formulas (Recency * Severity * Entity Match) to rank the MongoDB documents, we guarantee deterministic, repeatable results in under 2ms for ranking, while simultaneously avoiding token limits and LLM hallucination risks.

3. **MongoDB over SQL for Memory Storage:**
   *Reasoning:* Memory is inherently polymorphous. A `QualityEvent` requires entirely different fields (defect rate) than a `PaymentEvent` (invoice amount). MongoDB's document model allows us to store diverse memory structures flexibly while utilizing a universal `MemoryNode` wrapper and compound indexes for rapid query performance.

## 5. Test Results
```text
Running Evaluation Test Suite...
========================================
✅ PASS: Test 1: Recent high-severity memory scores higher than old low-severity
✅ PASS: Test 2: Stale memory is excluded from top_memories
✅ PASS: Test 3: Conflict resolver flags improvement or stable
✅ PASS: Test 4: Unknown supplier returns proper edge case response
✅ PASS: Test 5: Pipeline completes under 5 seconds for all 3 suppliers
✅ PASS: Test 6: trust_score/risk_score recalculates correctly after new severe QualityEvent
✅ PASS: Test 7: Seasonal LogisticsNote stays fresh longer than normal one
✅ PASS: Test 8: SemanticPattern with confidence > 0.9 is marked evergreen
✅ PASS: Test 9: Query with no amount still parses supplier name correctly
✅ PASS: Test 10: All memories have valid entity links in MongoDB
========================================
Overall Score: 10/10
```

## 6. Performance Results
```text
==================================================
 PERFORMANCE EVALUATION RESULTS
==================================================
| Metric                               | Time (ms) |
|--------------------------------------|-----------|
| Avg Retrieval (1 Supplier, 10 runs)  |  1577.28  |
| Retrieval w/ 100 Suppliers in DB     |  1223.93  |
| Memory Ranking (50 items)            |     0.26  |
| Memory Ranking (500 items)           |     2.06  |
| MongoDB Query (Indexed field)        |    30.70  |
| MongoDB Query (Unindexed field)      |    55.01  |
==================================================
```
*(Tests executed on MongoDB Atlas free-tier cluster via Python 3.12 over standard network connection)*

## 7. Challenges Faced and How Solved

1. **Mac OS SSL/TLS Certificate Errors:** 
   *Challenge:* Initially, connecting `pymongo` to MongoDB Atlas failed due to `[SSL: CERTIFICATE_VERIFY_FAILED]` errors native to some Mac OS environments.
   *Solution:* We solved this by installing the `certifi` package and explicitly injecting `tlsCAFile=certifi.where()` into the `MongoClient` configuration.

2. **Wrapper Abstraction in Ranking:**
   *Challenge:* The `MemoryNode` documents (which act as universal wrappers) were accidentally absorbing the top ranking spots instead of the actual deep event documents (`QualityEvent`, `PaymentEvent`), masking crucial severity data.
   *Solution:* We split the ranking logic in Phase 4 to evaluate primary business events first, reserving wrapper types for secondary fallback and broader conflict resolution calculations.

3. **Conflicting Historical Signals:**
   *Challenge:* A supplier with a terrible track record 8 months ago, but perfect performance in the last 3 months, was still generating negative recommendations.
   *Solution:* We developed a `conflict_resolver` module that splits memories temporally and detects trend vectors. It identifies this exact pattern and overrides the raw score to flag the supplier as "IMPROVING", drastically changing the agent's recommendation.

## 8. What I Would Do Differently

1. **Hybrid Vector Search:** Currently, the system relies on exact ID matching or Regex for supplier names. In a production environment with messy data (e.g., "Delta-Forge" vs "DeltaForge Inc"), I would integrate a small embedding model to perform semantic vector searches for entity resolution.
2. **Graph Database for Links:** While MongoDB handles standard relational referencing fine via `linked_node_ids`, moving complex multi-hop dependencies (e.g., tracking a specific quality defect back through logistics notes to a specific factory shift) would be significantly faster and cleaner in a Graph database like Neo4j.

## 9. Conclusion
This project successfully demonstrates that a robust AI context system does not require throwing massive text payloads at an LLM. By combining classic deterministic mathematical scoring with modern NoSQL architecture, we can give AI agents deep, explainable, and reliable business memory at a fraction of the computational cost.
