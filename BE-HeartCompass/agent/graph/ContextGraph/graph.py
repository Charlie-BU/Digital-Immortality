from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

import asyncio
import logging

from .state import ContextGraphState
from .nodes import node

logger = logging.getLogger(__name__)


# 全局单例
_context_graph_instance: CompiledStateGraph | None = None
_context_graph_lock = asyncio.Lock()


async def getContextGraph() -> CompiledStateGraph:
    global _context_graph_instance
    if _context_graph_instance is not None:
        return _context_graph_instance
    async with _context_graph_lock:
        if _context_graph_instance is not None:
            return _context_graph_instance

        graph = StateGraph(
            state_schema=ContextGraphState,
            input_schema=ContextGraphState,
            output_schema=ContextGraphState,
        )
        graph.add_node("node", node)

        graph.set_entry_point("node")
        graph.add_edge("node", END)

        # ContextGraph无需短期记忆
        _context_graph_instance = graph.compile()
        return _context_graph_instance
