"""LangGraph ReAct agent — TravelBuddy.

Graph: START → agent → should_continue? → tools/END → agent (loop)
"""

import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from react_agent.prompts import SYSTEM_PROMPT
from react_agent.tools import TOOLS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class State(TypedDict):
    """Graph state — chỉ cần messages."""

    messages: Annotated[list, add_messages]


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def _get_model():
    """Lazy init model qua OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    ).bind_tools(TOOLS)


def agent_node(state: State) -> dict:
    """Gọi LLM, tự động prepend system prompt nếu chưa có."""
    messages = list(state["messages"])

    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    model_with_tools = _get_model()
    response: AIMessage = model_with_tools.invoke(messages)  # type: ignore[assignment]

    if response.tool_calls:
        tool_names = [tc["name"] for tc in response.tool_calls]
        logger.info("🔧 Agent gọi tools: %s", ", ".join(tool_names))
    else:
        logger.info("💬 Agent trả lời trực tiếp.")

    return {"messages": [response]}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def should_continue(state: State) -> Literal["tools", "__end__"]:
    """Nếu message cuối có tool_calls → chạy tools, không → kết thúc."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"


# ---------------------------------------------------------------------------
# Build Graph
# ---------------------------------------------------------------------------

graph_builder = StateGraph(State)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", ToolNode(TOOLS))

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()
