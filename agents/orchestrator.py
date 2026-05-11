import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated

from langchain_core.messages import BaseMessage, AIMessage

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

from agents.remediation import remediation_node
from agents.monitor import monitor_node
from agents.diagnosis import diagnosis_node
from agents.postmortem import postmortem_node

from agents.tools import get_service_logs, get_service_metrics, restart_service, query_incident_memory

from agents.state import AgentState

def route_after_monitor(state: AgentState):
    if state.get("alert"):
        return "diagnosis"

    return END

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "diag_tools"

    return "remediation"

def should_remediate_continue(state: AgentState):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "remed_tools"

    return "postmortem"


diag_tools = [
    get_service_logs,
    get_service_metrics,
    query_incident_memory
]

diag_tool_node = ToolNode(diag_tools)

remed_tools = [
    restart_service
]

remed_tool_node = ToolNode(remed_tools)

graph = StateGraph(AgentState)

graph.add_node("monitor", monitor_node)
graph.add_node("diagnosis", diagnosis_node)
graph.add_node("diag_tools", diag_tool_node)
graph.add_node("remed_tools", remed_tool_node)
graph.add_node("remediation", remediation_node)
graph.add_node("postmortem", postmortem_node)

graph.add_edge(START, "monitor")

graph.add_conditional_edges(
    "monitor",
    route_after_monitor
)

graph.add_conditional_edges(
    "diagnosis",
    should_continue
)

graph.add_edge("diag_tools", "diagnosis")

graph.add_conditional_edges(
    "remediation",
    should_remediate_continue
)

graph.add_edge("remed_tools", "remediation")

graph.add_edge("postmortem", END)

graph = graph.compile()
