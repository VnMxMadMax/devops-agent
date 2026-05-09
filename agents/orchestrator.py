import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated

from langchain_core.messages import BaseMessage, AIMessage

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

from agents.remediation import remediation_node
from agents.monitor import monitor_node
from agents.diagnosis import diagnosis_node

from agents.tools import get_service_logs, get_service_metrics, restart_service

class AgentState(TypedDict):

    # LangGraph required field for ReAct agents to maintain conversation/tool history
    messages: Annotated[List[BaseMessage], operator.add]
    # Raw Inputs (from simulation)
    services: List[Dict[str, Any]] # snapshot of all services
    logs: List[Dict[str, Any]] # latest logs

    # Monitor Agent Output
    alert: Optional[Dict[str, Any]]


    # Metadata/Control
    active_incident: Optional[List[str]]
    timestamp: Optional[str]

def route_after_monitor(state: AgentState):
    if state.get("alert"):
        return "diagnosis"

    return END

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "remediation"

tools = [
    get_service_logs,
    get_service_metrics,
    restart_service
]

tool_node = ToolNode(tools)

graph = StateGraph(AgentState)

graph.add_node("monitor", monitor_node)
graph.add_node("diagnosis", diagnosis_node)
graph.add_node("tools", tool_node)
graph.add_node("remediation", remediation_node)

graph.add_edge(START, "monitor")

graph.add_conditional_edges(
    "monitor",
    route_after_monitor
)

graph.add_conditional_edges(
    "diagnosis",
    should_continue
)

graph.add_edge("tools", "diagnosis")

graph.add_edge("remediation", END)

graph = graph.compile()
