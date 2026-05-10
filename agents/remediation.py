from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from agents.tools import restart_service

# Load env
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-5.4-2026-03-05",
    temperature=0
)


def remediation_node(state: AgentState) -> Dict[str, Any]:
    """
    Remediation node:
    - Reads conversation history (including diagnosis)
    - Determines appropriate fix
    - Executes low-risk fixes using tools
    """

    messages: List = state.get("messages", [])
    alert = state.get("alert")

    # If no alert → nothing to fix
    if not alert:
        return {}

    # Strong system prompt (critical for tool usage)
    system_prompt = """
You are an automated DevOps Remediation Agent.

Your responsibilities:
1. Read the full conversation history (including diagnosis).
2. Identify the root cause of the issue.
3. Suggest a remediation plan.

CRITICAL RULE:
- If the fix is LOW RISK (e.g., restarting a service, clearing cache),
  you MUST execute it immediately using the available tools.

- If the fix is MEDIUM or HIGH RISK (e.g., deployment rollback, scaling),
  DO NOT execute it. Instead, explain the recommended action clearly.

Guidelines:
- Be concise and technical.
- Prefer concrete actions over vague suggestions.
- Use tools only when appropriate.

Available tool:
- restart_service(service_name)
"""

    # Bind tools
    tools = [restart_service]
    llm_with_tools = llm.bind_tools(tools)

    # Append system prompt to history
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