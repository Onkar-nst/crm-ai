# app/main.py
# FastAPI backend for Context & Memory Management System

import time
import uuid
import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from retrieval.pipeline import run_pipeline
from app.edge_cases import apply_edge_cases
from app.memory_updater import update_memory
from db.connection import get_database

app = FastAPI(title="Context & Memory API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

class QueryRequest(BaseModel):
    query: str

class MemoryEventRequest(BaseModel):
    supplier_id: str
    event_type: str
    severity: int = 0
    description: str

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"[{request.method}] {request.url.path} - {process_time*1000:.1f}ms")
    return response

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    """Serves the demo UI homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query")
async def process_query(req: QueryRequest):
    """Accepts raw query string, runs full pipeline, returns context bundle"""
    bundle = run_pipeline(req.query, top_n=5)
    
    # Apply Edge Cases
    active = bundle.get("key_memories", [])
    stale = bundle.get("stale_pool", [])
    bundle = apply_edge_cases(bundle, active, stale)
    
    return bundle

@app.get("/suppliers")
async def list_suppliers():
    """Returns list of all suppliers with trust scores"""
    db = get_database()
    suppliers = list(db.suppliers.find({}, {"_id": 0}))
    for sup in suppliers:
        # Trust score = 1.0 - risk_score
        sup["trust_score"] = round(1.0 - float(sup.get("risk_score", 0.5)), 2)
    return {"suppliers": suppliers}

@app.get("/memories/{supplier_id}")
async def get_memories(supplier_id: str):
    """Returns all memories for a supplier"""
    db = get_database()
    nodes = list(db.memory_nodes.find({"supplier_id": supplier_id}, {"_id": 0}))
    return {"memories": nodes}

@app.post("/memory/add")
async def add_memory(req: MemoryEventRequest):
    """Adds a new event to memory and updates supplier profile"""
    event_data = {
        "supplier_id": req.supplier_id,
        "severity": req.severity,
    }
    
    # Map descriptions based on type
    if req.event_type == "QualityEvent":
        event_data["root_cause_summary"] = req.description
        event_data["reported_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        event_data["resolution_status"] = "OPEN"
    elif req.event_type == "PaymentEvent":
        event_data["deduction_reason"] = req.description
        event_data["invoice_date"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    elif req.event_type == "LogisticsNote":
        event_data["notes"] = req.description
        event_data["scheduled_date"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
    result = update_memory(req.event_type, event_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # Return updated trust score
    trust_score = round(1.0 - float(result.get("risk_score", 0.5)), 2)
    return {"status": "success", "trust_score": trust_score, "supplier": result.get("name")}
