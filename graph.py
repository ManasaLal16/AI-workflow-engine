from .node import Node
from typing import Dict, Any, Tuple, List, Callable
import asyncio

class GraphEngine:
    def __init__(self):
        # node registry for all graphs
        self.node_registry: Dict[str, Node] = {}
        self.tools = {}

    def register_node(self, name: str, func: Callable):
        self.node_registry[name] = Node(name, func)

    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func

    async def run(self, graph_spec: Dict[str, Any], initial_state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        graph_spec expected format (simple):
        {
          "nodes": ["extract","complexity",...],
          "edges": {"extract":"complexity", "score_check": {"loop_if": "quality_score < threshold", "true":"extract","false":null}},
          "start": "extract"
        }
        Node functions can modify state and optionally return a control dict:
        - return {"_next": "node_name"}
        - return {"_loop": True} (goes to same node)
        - or return None to follow default edges
        """
        state = initial_state
        log: List[Dict[str, Any]] = []
        nodes = graph_spec.get("nodes", [])
        edges = graph_spec.get("edges", {})
        current = graph_spec.get("start")

        steps = 0
        max_steps = 1000
        while current is not None and steps < max_steps:
            steps += 1
            node = self.node_registry.get(current)
            if not node:
                # skip unknown node, break
                log.append({"node": current, "error": "node not registered"})
                break
            log.append({"node": current, "state_before": dict(state)})
            try:
                out = await node.run(state, self.tools)
            except Exception as e:
                log.append({"node": current, "error": str(e)})
                break

            # If node returned a dict with updates, merge
            if isinstance(out, dict):
                # If function returns a control dict, allow special keys
                control = {}
                updates = {}
                for k, v in out.items():
                    if k.startswith("_") or k in ("_next", "_loop"): 
                        control[k] = v
                    else:
                        updates[k] = v
                state.update(updates)
                # next control
                if "_next" in control and control["_next"] is not None:
                    next_node = control["_next"]
                elif control.get("_loop"):
                    next_node = current
                else:
                    # fall back to edges
                    next_node = self._resolve_edge(current, edges, state)
            else:
                # no return, fall back to edges
                next_node = self._resolve_edge(current, edges, state)

            log.append({"node": current, "state_after": dict(state), "next": next_node})
            current = next_node

        if steps >= max_steps:
            log.append({"error": "max_steps_reached"})
        return state, log

    def _resolve_edge(self, current: str, edges: Dict[str, Any], state: Dict[str, Any]):
        edge = edges.get(current)
        if edge is None:
            return None
        # If simple string
        if isinstance(edge, str):
            return edge
        # If dict has branching logic
        if isinstance(edge, dict):
            # supported pattern: {"loop_if": "quality_score < threshold", "true":"extract","false":null}
            if "loop_if" in edge:
                expr = edge["loop_if"]
                try:
                    # evaluate expression in a safe-ish way using state only
                    cond = eval(expr, {}, state)
                except Exception:
                    cond = False
                return edge.get("true") if cond else edge.get("false")
            # or keyed conditions: {"if_expr":"node_name", ...}
            for k, v in edge.items():
                if k.startswith("if_"):
                    expr = k[3:]
                    try:
                        if eval(expr, {}, state):
                            return v
                    except Exception:
                        continue
        return None
