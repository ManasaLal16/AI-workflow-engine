from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import asyncio
from .engine.graph import GraphEngine

app = FastAPI(title="SRM AI Agent - Code Review")

# in-memory storage
GRAPHS = {}
RUNS = {}
ENGINE = GraphEngine()

class CreateGraphRequest(BaseModel):
    graph: dict

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: dict

@app.post("/graph/create")
async def create_graph(req: CreateGraphRequest):
    graph_id = f"graph_{uuid4().hex[:8]}"
    GRAPHS[graph_id] = req.graph
    return {"graph_id": graph_id}

@app.post("/graph/run")
async def run_graph(req: RunGraphRequest):
    graph = GRAPHS.get(req.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    run_id = f"run_{uuid4().hex[:8]}"
    RUNS[run_id] = {"state": req.initial_state.copy(), "status": "running", "log": []}

    # Synchronous execution for evaluation clarity
    final_state, log = await ENGINE.run(graph, req.initial_state.copy())

    RUNS[run_id]["state"] = final_state
    RUNS[run_id]["status"] = "completed"
    RUNS[run_id]["log"] = log

    return {"run_id": run_id, "final_state": final_state, "log": log}

@app.get("/graph/state/{run_id}")
async def get_run_state(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.on_event("startup")
async def startup_event():
    # register the example workflow & tools at startup
    from .tools.registry import register_tool
    from .workflows.code_review import register_code_review_workflow
    register_code_review_workflow(ENGINE)
