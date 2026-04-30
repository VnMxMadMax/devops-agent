import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):

    # LangGraph required field for ReAct agents to maintain conversation/tool history
    messages: Annotated[List[BaseMessage], operator.add]
    # Raw Inputs (from simulation)
    services: List[Dict[str, Any]] # snapshot of all services
    logs: List[Dict[str, Any]] # latest logs

    # Monitor Agent Output
    alert: Optional[Dict[str, Any]]

    # Diagnosis Agent Output
    root_cause: Optional[str]

    # Remediation Agent Output
    remediation_plan: Optional[str]

    # Metadata/Control
    active_incident: Optional[List[str]]
    timestamp: Optional[str]

