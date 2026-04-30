from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agents.orchestrator import AgentState
from agents.tools import get_service_logs, get_service_metrics

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-5.4",
    temperature=0
)


def diagnosis_node(state: AgentState) -> Dict[str, Any]:
    """
    Diagnosis node analyzes the alert and determines root cause
    using available tools (logs, metrics).
    """

    alert = state.get("alert")
    messages: List = state.get("messages", [])

    # If no alert → do nothing
    if not alert:
        return {}

    service = alert["service"]
    metric = alert["metric"]
    value = alert["value"]
    threshold = alert["threshold"]

    # System Prompt (very important)
    system_prompt = f"""
You are an expert DevOps engineer performing root cause analysis.

An alert has been triggered in the system:

Service: {service}
Metric: {metric}
Current Value: {value}
Threshold: {threshold}

Your task:
- Investigate the issue using available tools
- Identify the most likely root cause
- Be precise and technical in your reasoning

You have access to tools for retrieving service logs and metrics.
Use them when necessary before concluding.
"""

    # Bind tools
    tools = [get_service_logs, get_service_metrics]
    llm_with_tools = llm.bind_tools(tools)

    # Add system message (only once ideally)
    updated_messages = messages + [
        SystemMessage(content=system_prompt)
    ]

    # Invoke LLM
    response = llm_with_tools.invoke(updated_messages)

    # We only return the NEW messages to the state!
    # LangGraph's operator.add will append them to the existing list automatically.
    return {
        "messages": [SystemMessage(content=system_prompt), response]
    }