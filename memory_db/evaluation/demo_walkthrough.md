# Context and Memory System - Demo Walkthrough

**Total Demo Time:** ~4 Minutes

---

### Step 1: UI Overview (30 seconds)
*Action:* Open browser to `http://localhost:8000`.

**Talking points:**
* "What you're seeing is the interactive dashboard for our Context and Memory Management System."
* "On the left, we have the interface where an AI agent (or human) would submit a natural language business query."
* "On the right, we have the Memory Ingestion panel where new business events are logged into the database in real-time."
* "This entire UI is served by a FastAPI backend connecting to a live MongoDB Atlas cluster."

---

### Step 2: The Initial Query (1 minute)
*Action:* In the left search box, type: 
`Invoice received from Delta Forge for ₹2,50,000` 
*Action:* Click **Analyze Context**.

**Talking points:**
* "Watch how fast that was. Under 2 seconds. The system used Regex to extract the supplier name, fetched data from 6 MongoDB collections in parallel, and ran a mathematical ranking algorithm."
* *Point to Supplier Block:* "Notice the Trust Score is incredibly low (0.39). This is because of their historical data."
* *Point to Key Memories:* "Look at the memory it retrieved. It pulled up a severe quality trend pattern. The Explainer module explicitly tells us *why* it was retrieved: high severity and financial impact."
* *Point to Conflict Banner:* "However, look at the blue banner. The conflict resolver noticed that while history is bad, recent data is actually fine. So it labeled the supplier as **IMPROVING** and issued a cautious recommendation rather than a flat rejection."

---

### Step 3: Real-Time Memory Update (1 minute)
*Action:* Move to the right-hand panel ("Add New Event").
* Select **Supplier:** `Delta Forge Industries`
* Select **Event Type:** `Quality Event`
* Set **Severity:** `2` (Low)
* Type **Description:** `Passed secondary spot-inspection. Very minor cosmetic issues, fully acceptable.`
* Click **Submit Event**.

**Talking points:**
* "Let's say our quality assurance agent just finished inspecting a new batch from Delta Forge and it passed with flying colors."
* "When we submit this, the system does two things: It creates a new `QualityEvent` in MongoDB, and it wraps it in a universal `MemoryNode`."
* *Point to success message:* "Look at the bottom. It instantly recalculated the Trust Score based on our new 6-month average severity. The score shot up to 1.0!"

---

### Step 4: The Re-Query (30 seconds)
*Action:* Go back to the left search box. Do not change the text.
* Click **Analyze Context** again.

**Talking points:**
* "Now, imagine a Procurement agent receives an invoice from Delta Forge five minutes later. They run the exact same query."
* *Point to Supplier Block:* "Boom. The Trust Score is now perfectly updated to 1.0."
* "Our deterministic pipeline updated the context bundle instantly without requiring any LLM to re-read or re-summarize a giant database dump. Multi-agent state is perfectly synchronized."

---

### Step 5: Test Suite & Performance Validation (30 seconds)
*Action:* Open terminal and run `python evaluation/test_suite.py` followed by `python evaluation/performance.py`.

**Talking points:**
* "To prove this isn't just a UI trick, we built a comprehensive test suite."
* *Show passing tests:* "As you can see, 10/10 edge cases pass natively. Staleness logic, recency decay, and conflict resolution are all mathematically verified."
* *Show performance table:* "And looking at performance, our MongoDB queries take under 60 milliseconds, and the Python ranking algorithm takes less than 3 milliseconds. This scales perfectly to thousands of suppliers."

**Closing statement:** "We built a deterministic memory engine that is fast, safe, and highly explainable."
