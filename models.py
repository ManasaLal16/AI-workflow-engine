from pydantic import BaseModel
from typing import Any, Dict

class GraphModel(BaseModel):
    nodes: Dict[str, Any]
    edges: Dict[str, Any]
    start: str
