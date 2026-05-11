from typing import Dict, Any, List
import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from memory.incident_memory import save_incident

# Load env
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-5.4-2026-03-05",
    temperature=0
)


def postmortem_node(state: AgentState) -> Dict[str, Any]:
    """
    Post-Mortem node:
    - Reads full conversation history
    - Extracts incident summary
    - Stores incident into ChromaDB memory
    """

    messages: List = state.get("messages", [])

    incident_id = str(uuid.uuid4())

    system_prompt = """
You are a DevOps Post-Mortem Analysis Agent.

Your task:
Read the full conversation history and extract:

1. Symptoms
   - What alert or abnormal behavior was detected?
   - Include affected service and major symptoms.

2. Root Cause
   - What was the most likely technical root cause?

3. Resolution
   - What remediation action fixed the issue?

Return your answer EXACTLY in this format:

Symptoms: <text>

Root Cause: <text>

Resolution: <text>
"""

    updated_messages = messages + [
        SystemMessage(content=system_prompt)
    ]

    # Invoke LLM
    response = llm.invoke(updated_messages)

    content = response.content

    # Multi-line section parser
    symptoms = ""
    root_cause = ""
    resolution = ""

    current_section = None
    section_lines: Dict[str, List[str]] = {
        "symptoms": [],
        "root_cause": [],
        "resolution": []
    }

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("Symptoms:"):
            current_section = "symptoms"
            remainder = stripped.replace("Symptoms:", "").strip()
            if remainder:
                section_lines["symptoms"].append(remainder)
        elif stripped.startswith("Root Cause:"):
            current_section = "root_cause"
            remainder = stripped.replace("Root Cause:", "").strip()
            if remainder:
                section_lines["root_cause"].append(remainder)
        elif stripped.startswith("Resolution:"):
            current_section = "resolution"
            remainder = stripped.replace("Resolution:", "").strip()
            if remainder:
                section_lines["resolution"].append(remainder)
        elif stripped and current_section:
            section_lines[current_section].append(stripped)

    symptoms = " ".join(section_lines["symptoms"])
    root_cause = " ".join(section_lines["root_cause"])
    resolution = " ".join(section_lines["resolution"])

    # Guard: only save if we actually extracted something meaningful
    if not any([symptoms, root_cause, resolution]):
        print("[PostMortem] WARNING: Could not parse LLM response. Skipping memory save.")
        return {"alert": None}

    # Save to ChromaDB memory
    save_incident(
        incident_id=incident_id,
        symptoms=symptoms,
        root_cause=root_cause,
        resolution=resolution
    )

    print(f"[PostMortem] Incident saved: {incident_id}")

    # Return a valid state update — LangGraph requires at least one key
    return {"alert": None}