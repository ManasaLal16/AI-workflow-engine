# SRM — AI Engineering Assignment: Code Review Mini-Agent

Minimal workflow engine + FastAPI implementation for the coding assignment.

## What's included

- A tiny workflow engine that supports nodes (Python functions), shared state (dict), edges, conditional branching, and looping.
- Tool registry — small dictionary of helper functions nodes can call.
- FastAPI endpoints:
  - `POST /graph/create` — create a graph, returns `graph_id`.
  - `POST /graph/run` — run a graph synchronously, returns final state + execution log.
  - `GET /graph/state/{run_id}` — get current state and status of a run.
- Example workflow: **Code Review Mini-Agent** (Option A)

## How to run (local)

1. Create a virtualenv and activate it

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

2. Start the API

```bash
uvicorn app.main:app --reload
```

3. Use `curl` or Postman to create a graph and run it. See examples below.

## Example usage (curl)

1. Create graph

```bash
curl -s -X POST http://127.0.0.1:8000/graph/create \\
  -H "Content-Type: application/json" \\
  -d '{"graph": {"nodes": ["extract","complexity","issues","suggest","score_check"], "edges": {"extract":"complexity","complexity":"issues","issues":"suggest","suggest":"score_check","score_check":{"loop_if": "quality_score < threshold","true":"extract","false":null}}, "start":"extract"}}'
```

Response: `{ "graph_id": "graph_..." }`

2. Run graph

```bash
curl -s -X POST http://127.0.0.1:8000/graph/run -H "Content-Type: application/json" -d '{"graph_id": "graph_...", "initial_state": {"code": "def f():\n  pass\n", "threshold": 80}}'
```

Response: final state + execution log.

## What I'd improve with more time

- Add persistent storage (SQLite) for graphs and run history.
- Add WebSocket streaming for step-by-step logs.
- Better DSL for branching/conditions and richer node metadata.
- Add tests and CI pipeline.

## License

MIT — feel free to adapt for your submission.
