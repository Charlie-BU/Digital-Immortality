from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
import asyncio
import logging

from src.agents.graphs.ConversationGraph.state import (
    ConversationGraphInput,
    ConversationGraphOutput,
    ConversationGraphState,
)
from src.agents.graphs.ConversationGraph.nodes import (
    nodeBuildMessage,
    nodeCallLLM,
    nodeLoadFRAndPersona,
    nodeRecallInteractionStylesFromDB,
    nodeRecallMemoriesFromDB,
    nodeRecallPersonalitiesFromDB,
    nodeRecallProceduralInfosFromDB,
)
from src.agents.graphs.checkpointer import agetCheckpointer

logger = logging.getLogger(__name__)
_conversation_graph_instance: CompiledStateGraph | None = None
_conversation_graph_lock = asyncio.Lock()


def buildBaseConversationGraph() -> StateGraph:
    graph = StateGraph(
        state_schema=ConversationGraphState,
        input_schema=ConversationGraphInput,
        output_schema=ConversationGraphOutput,
    )

    graph.add_node("nodeLoadFRAndPersona", nodeLoadFRAndPersona)
    graph.add_node("nodeRecallPersonalitiesFromDB", nodeRecallPersonalitiesFromDB)
    graph.add_node(
        "nodeRecallInteractionStylesFromDB", nodeRecallInteractionStylesFromDB
    )
    graph.add_node("nodeRecallProceduralInfosFromDB", nodeRecallProceduralInfosFromDB)
    graph.add_node("nodeRecallMemoriesFromDB", nodeRecallMemoriesFromDB)
    graph.add_node("nodeBuildMessage", nodeBuildMessage)
    graph.add_node("nodeCallLLM", nodeCallLLM)

    graph.add_edge(START, "nodeLoadFRAndPersona")

    # 四个维度召回并行执行
    graph.add_edge("nodeLoadFRAndPersona", "nodeRecallPersonalitiesFromDB")
    graph.add_edge("nodeLoadFRAndPersona", "nodeRecallInteractionStylesFromDB")
    graph.add_edge("nodeLoadFRAndPersona", "nodeRecallProceduralInfosFromDB")
    graph.add_edge("nodeLoadFRAndPersona", "nodeRecallMemoriesFromDB")

    # 汇合到下游，确保四个召回都完成后再继续
    graph.add_edge("nodeRecallPersonalitiesFromDB", "nodeBuildMessage")
    graph.add_edge("nodeRecallInteractionStylesFromDB", "nodeBuildMessage")
    graph.add_edge("nodeRecallProceduralInfosFromDB", "nodeBuildMessage")
    graph.add_edge("nodeRecallMemoriesFromDB", "nodeBuildMessage")

    graph.add_edge("nodeBuildMessage", "nodeCallLLM")
    graph.add_edge("nodeCallLLM", END)

    return graph


def buildConversationGraph() -> CompiledStateGraph:
    """
    构建无短期记忆的 ConversationGraph
    """
    graph = buildBaseConversationGraph()
    return graph.compile()


async def buildConversationGraphWithMemory() -> CompiledStateGraph:
    """
    构建有短期记忆的 ConversationGraph
    【注意】graph 中存在大量异步节点，必须使用异步 checkpointer，必须用 ainvoke 调用图
    """
    graph = buildBaseConversationGraph()
    checkpointer = await agetCheckpointer()
    return graph.compile(checkpointer=checkpointer)


async def getConversationGraph() -> CompiledStateGraph:
    global _conversation_graph_instance
    if _conversation_graph_instance is not None:
        return _conversation_graph_instance
    async with _conversation_graph_lock:
        if _conversation_graph_instance is None:
            _conversation_graph_instance = await buildConversationGraphWithMemory()
    return _conversation_graph_instance
