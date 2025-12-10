from ..engine.graph import GraphEngine
from ..tools.registry import TOOLS, register_tool

# Node implementations (pure Python functions)

def extract_functions(state: dict, tools: dict):
    # crude extraction: split by 'def ' and return list of functions
    code = state.get("code", "")
    funcs = []
    lines = code.splitlines()
    cur = []
    inside = False
    for ln in lines:
        if ln.strip().startswith("def "):
            if inside:
                funcs.append("\n".join(cur))
                cur = []
            inside = True
            cur.append(ln)
        elif inside:
            cur.append(ln)
    if inside and cur:
        funcs.append("\n".join(cur))
    state["functions"] = funcs
    return {"_next": "complexity"}

def check_complexity(state: dict, tools: dict):
    funcs = state.get("functions", [])
    cs = []
    complexity_fn = tools.get("complexity_score")
    for f in funcs:
        score = complexity_fn(f) if complexity_fn else 0
        cs.append(score)
    state["complexity_scores"] = cs
    state["avg_complexity"] = int(sum(cs)/len(cs)) if cs else 0
    return {}

def detect_issues(state: dict, tools: dict):
    issues = []
    code = state.get("code", "")
    # simple heuristics
    if "print(" in code and "#debug" not in code:
        issues.append("debug_prints")
    if "TODO" in code:
        issues.append("todo_marker")
    if len(code.splitlines()) > 200:
        issues.append("too_long")
    state["issues"] = issues
    state["issue_count"] = len(issues)
    return {}

def suggest_improvements(state: dict, tools: dict):
    suggestions = []
    if state.get("avg_complexity", 0) > 20:
        suggestions.append("Refactor large functions")
    if "debug_prints" in state.get("issues", []):
        suggestions.append("Remove debug prints or mark them with #debug")
    if "todo_marker" in state.get("issues", []):
        suggestions.append("Resolve TODOs before merge")
    state["suggestions"] = suggestions
    # create a quality score heuristic
    base = 100
    base -= state.get("avg_complexity", 0)
    base -= state.get("issue_count", 0) * 10
    state["quality_score"] = max(0, base)
    return {}

def score_check(state: dict, tools: dict):
    # if quality_score < threshold, loop
    threshold = state.get("threshold", 80)
    qs = state.get("quality_score", 0)
    if qs < threshold:
        # simulate a simple auto-fix to demonstrate loop: reduce complexity by 10
        state["auto_fix_applied"] = state.get("auto_fix_applied", 0) + 1
        state["quality_score"] = min(100, qs + 10)
        return {"_next": "extract"}
    return {"_next": None}

def register_code_review_workflow(engine: GraphEngine):
    # Register nodes
    engine.register_node("extract", extract_functions)
    engine.register_node("complexity", check_complexity)
    engine.register_node("issues", detect_issues)
    engine.register_node("suggest", suggest_improvements)
    engine.register_node("score_check", score_check)

    # register tools into engine
    from ..tools.registry import TOOLS
    for name, fn in TOOLS.items():
        engine.register_tool(name, fn)
