from typing import Callable, Dict, Any
import asyncio

class Node:
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

    async def run(self, state: Dict[str, Any], tools: Dict[str, Callable]):
        # allow both sync and async functions
        result = self.func(state, tools)
        if asyncio.iscoroutine(result):
            result = await result
        return result
