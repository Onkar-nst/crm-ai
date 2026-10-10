# Context and Memory System - Interview Cheatsheet

## The One-Liner Pitch
"A deterministic, purely mathematical Python engine running on MongoDB that instantly retrieves, ranks, and resolves business memories for AI agents, bypassing the latency and hallucination risks of LLMs."

---

## 15 Quick-Fire Questions & Answers

**Q1. Why not just use a Vector Database (like Pinecone)?**  
Vectors are great for fuzzy text similarity, but terrible at hard business logic. A vector search doesn't understand that a 30% defect rate 2 days ago is mathematically more critical than a 1% defect rate 200 days ago; our deterministic engine does.

**Q2. How do you rank memories?**  
We use a composite score based on three factors: Recency (exponential decay curve), Severity (1-10 normalized score with financial multipliers), and Entity Match (exact ID vs name similarity). 

**Q3. Why use exponential decay for recency instead of a linear cut-off?**  
Business events lose relevance on a curve. A 5-day-old event is significantly more relevant than a 10-day-old event, but a 300-day-old event and a 305-day-old event are equally irrelevant. Exponential decay `e^(-λ * t)` perfectly models this.

**Q4. What is the `MemoryNode` collection for?**  
It acts as a universal wrapper. A PaymentEvent and a QualityEvent have completely different schemas. The MemoryNode wraps them into a standard structure so any agent can fetch and score them universally.

**Q5. Why MongoDB instead of PostgreSQL?**  
Memory events are polymorphous (different structures for different events). MongoDB's document model allows us to store these varying schemas natively, while still enforcing relational integrity via `supplier_id` indexes.

**Q6. What happens if an LLM isn't used for retrieval?**  
We save money, reduce latency from seconds to milliseconds, and completely eliminate the risk of hallucination during the critical data-gathering phase.

**Q7. How do you handle "stale" memory?**  
Different events have different shelf lives (e.g., invoices 180 days, quality 365 days). If an event passes its threshold, it is filtered into a "stale pool" and excluded from active decision making unless no other data exists.

**Q8. What are "Evergreen" memories?**  
Evergreen memories are semantic patterns (like a supplier's tendency to invoice early) that have reached a confidence score above 0.9. They are mathematically exempted from staleness decay.

**Q9. How do you handle conflicting data?**  
The `conflict_resolver` module splits memories into temporal windows (recent vs historical). If history is terrible but recent data is clean, it flags the supplier as "IMPROVING" rather than just averaging the score.

**Q10. How fast is the retrieval?**  
Averaging ~1.5 seconds end-to-end (including parsing, DB fetch, ranking, and packaging). The actual ranking math takes less than 1 millisecond.

**Q11. How do you avoid API bottlenecks?**  
The `memory_fetcher` module uses Python's `ThreadPoolExecutor` to fan out requests to all 6 MongoDB collections in parallel, collapsing DB latency.

**Q12. What language/frameworks did you use?**  
Pure Python 3.12, PyMongo for the database layer, FastAPI for the REST endpoints, and Vanilla HTML/JS for the UI. No external ML libraries.

**Q13. How does the system handle seasonality?**  
If a `LogisticsNote` contains tags like "monsoon", the system dynamically extends its staleness threshold to 365 days, ensuring the memory survives until the next monsoon season.

**Q14. How does the system recalculate trust?**  
Trust is recalculated dynamically on every write operation. If a severe QualityEvent is added, the `memory_updater` instantly calculates a new score based on the 6-month severity average and resolution ratios.

**Q15. How do you handle explainability?**  
The `explainer` module attaches a plain-English `why_retrieved` sentence to every memory, detailing the exact recency score, severity multiplier, and staleness label that caused it to be surfaced.

---

## 5 "Explain with Example" Questions (Supplier B Story)

**Q16. Explain how Severity can override Recency.**  
*Example:* Supplier B (Delta Forge) had a catastrophic 30% defect incident (severity 9) in December 2024, but a minor documentation error (severity 3) in March 2025. Even though the documentation error is more recent, the massive severity multiplier on the December incident forces it to rank higher in the context bundle.

**Q17. Explain how the Conflict Resolver works.**  
*Example:* Supplier B has terrible historical context (a severe defect), but zero recent issues. A simple average would label them "bad". Our conflict resolver splits the timeline, sees the high severity is old, and assigns an "IMPROVING" flag, changing the agent's recommendation to "Proceed with caution".

**Q18. Explain how the trust score updates dynamically.**  
*Example:* Supplier B's trust score sits at 0.39 due to past issues. If we use the UI to add a new QualityEvent stating they passed a recent inspection perfectly, the `memory_updater` triggers, calculates the improved average, and instantly bumps their trust score up to 1.0.

**Q19. Explain what the Explainer module outputs.**  
*Example:* For Supplier B's December defect, the explainer outputs: *"low recency (score 0.01) but included for historical context. high severity 9/10. financial impact ₹50,000 applied multiplier."* It tells the agent exactly why an old memory was surfaced.

**Q20. Explain the fallback mechanism for stale data.**  
*Example:* If an agent queries Supplier C, and all their logistics notes are from 2024 (stale), the system won't just return blank. It pulls from the `stale_pool`, but tags them with `_fallback_from_stale`, warning the agent: *"All context is older than relevance window."*

---

## 3 "What If" Scenarios

**Q21. What if a supplier has absolutely no history in the database?**  
The edge case handler kicks in. It returns an empty context bundle with a specific recommendation: *"No history found — treat as new supplier, apply standard checks"*, preventing the agent from hallucinating past data.

**Q22. What if two completely contradictory events happen in the same week?**  
The edge case handler scans the active pool for events within the last 30 days. If it finds a severity > 6 and a severity < 3 concurrently, it overrides the system recommendation with a `"too_recent_to_judge"` flag, forcing manual human review.

**Q23. What if two agents query and update the same supplier simultaneously?**  
Because trust score updates and event insertions are handled synchronously by the `memory_updater` interacting with MongoDB's atomic document updates, Agent B will always fetch the updated state the exact millisecond after Agent A's write operation completes.
