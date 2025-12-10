# Simple tool registry
from typing import Dict, Callable

TOOLS = {}

def register_tool(name: str, func: Callable):
    TOOLS[name] = func

def get_tool(name: str):
    return TOOLS.get(name)

# example tools

def complexity_score(code: str) -> int:
    # naive heuristic: count branching keywords and length
    score = 0
    for token in ["if ", "for ", "while ", "try:", "except", "def "]:
        score += code.count(token) * 5
    score += max(0, len(code.splitlines()) - 10)
    return score

def count_lines(code: str) -> int:
    return len(code.splitlines())

register_tool("complexity_score", complexity_score)
register_tool("count_lines", count_lines)
