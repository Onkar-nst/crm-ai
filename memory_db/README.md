# Context & Memory Management System

A purely deterministic Python-based scoring engine and retrieval pipeline for AI agents. 
Features a complete FastAPI backend and visual UI for context retrieval and memory updates.

## 🛠 Prerequisites
- Python 3.12+
- MongoDB Atlas cluster

## 🚀 Setup Instructions

1. **Navigate to project directory**
   ```bash
   cd /Users/onkardange/Documents/crmaai/memory_db
   ```

2. **Setup virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Ensure `.env` exists in the root directory:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0...
   DB_NAME=memory_db
   ```

5. **Seed the database**
   *(If not already done in previous phases)*
   ```bash
   python main.py --seed
   ```

---

## 🏃‍♂️ Running the Web UI & API (Phase 5)

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

Open your browser and navigate to: **[http://localhost:8000](http://localhost:8000)**

### 🧪 Example Queries to Try in UI
1. `Invoice received from Delta Forge for ₹2,50,000` *(Shows deteriorating/improving conflict resolution)*
2. `Delivery expected from Coastal Freight next week — monsoon season` *(Shows seasonal logic matching)*
3. `Payment request from RajTech for ₹75,000` *(Shows clean fast-track record)*

### 📝 Updating Memory
Use the **"Add New Event"** panel on the right side of the UI to insert a new `QualityEvent` for Delta Forge. Watch how the Trust Score and recommendations dynamically change when you re-query!

---

## 🤖 Running the End-to-End Simulation Script
To see the system programmatically ingest a new event and alter its recommendation for a supplier throughout a simulated "business day", run:
```bash
python demo/run_demo.py
```

---

## 📁 Project Structure

- **`app/`**: FastAPI backend, Memory Update logic, Edge Cases, and HTML UI template.
- **`db/`**: MongoDB connection and collections setup.
- **`models/`**: Entity schema definitions.
- **`data/`**: Mock data seeder.
- **`engine/`**: Core deterministic scoring systems (Recency, Severity, Relevance, Staleness).
- **`retrieval/`**: Full processing pipeline (Parse → Fetch → Rank → Package → Explain).
- **`demo/`**: End-to-end scenario simulator.
