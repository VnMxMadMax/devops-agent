import asyncio
import random

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    TriggerIncidentRequest,
    ServiceStatus,
    SimulationStatusResponse
)

from simulator.state import env, last_logs
import simulator.state as sim_state
from simulator.incident import PREBUILT_INCIDENTS

from agents.orchestrator import graph

app = FastAPI(title="Sentinel AI")

# Number of consecutive agent cycles an incident can remain unresolved
# before an escalation alert is pushed to the frontend.
ESCALATION_THRESHOLD = 5

origins = [
    "http://localhost:3000",  # Common port for React
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "https://sentinelai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Shared environment — used by both REST endpoints and the WebSocket.
# V1 design: single shared env. A V2 improvement would be per-client
# SimulationEnvironment instances to prevent multi-client state collisions.


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/status", response_model=SimulationStatusResponse)
async def get_status():

    services = []

    for svc in env.services:
        services.append(
            ServiceStatus(
                name=svc.name,
                status=svc.status,
                metrics=svc.metrics.model_dump()
            )
        )

    active_incidents = [
        incident.name
        for incident in env.active_incidents
    ]

    return SimulationStatusResponse(
        services=services,
        active_incidents=active_incidents
    )


@app.post("/incident/trigger")
async def trigger_incident(
    request: TriggerIncidentRequest
):
    env.trigger_incident(request.incident_name)

    return {
        "message": f"Incident triggered: {request.incident_name}"
    }


@app.post("/incident/trigger/random")
async def trigger_random_incident():
    """Pick a random incident that is not already active and trigger it."""
    active_names = {inc.name for inc in env.active_incidents}
    available = [inc for inc in PREBUILT_INCIDENTS if inc.name not in active_names]

    if not available:
        return {"message": "All incidents are already active"}

    chosen = random.choice(available)
    env.trigger_incident(chosen.name)

    return {
        "message": f"Random incident triggered: {chosen.name}",
        "incident": chosen.name,
        "service": chosen.service,
        "severity": chosen.severity
    }


@app.post("/incident/resolve")
async def resolve_incident(
    request: TriggerIncidentRequest
):
    env.resolve_incident(request.incident_name)
    # Clear the staleness counter so escalation resets if incident re-triggers
    sim_state.incident_tick_counts.pop(request.incident_name, None)

    return {
        "message": f"Incident resolved: {request.incident_name}"
    }


@app.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:

            # Advance simulation
            services, logs = env.tick()

            # Update shared log state so tools.get_service_logs reads real data
            sim_state.last_logs = logs

            # ── Cost Guard ────────────────────────────────────────────────
            # Only invoke the LangGraph pipeline (and spend API tokens) when
            # there is an active incident. Healthy ticks short-circuit here
            # with a free Python heartbeat — zero LLM cost.
            # ─────────────────────────────────────────────────────────────
            if not env.active_incidents:
                await websocket.send_json({
                    "type": "heartbeat",
                    "content": "System healthy — all services nominal"
                })
                await asyncio.sleep(1)
                continue

            # Build LangGraph state — only reached when an incident is active
            initial_state = {
                "messages": [],
                "services": [
                    svc.model_dump()
                    for svc in services
                ],
                "logs": logs,
                "alert": None,
                "active_incident": [
                    inc.name
                    for inc in env.active_incidents
                ],
                "timestamp": None
            }

            # Run blocking graph in thread pool
            # Use get_running_loop() — get_event_loop() is deprecated in Python 3.10+
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(
                    None,
                    graph.invoke,
                    initial_state
                )

                # Stream agent messages to frontend.
                # Filter rules:
                #   - Skip SystemMessage (raw LLM prompts — internal, not for UI)
                #   - Skip AIMessage with empty content (intermediate tool-call steps)
                messages = result.get("messages", [])
                for msg in messages:
                    msg_type = msg.__class__.__name__
                    content = str(msg.content).strip()
                    if msg_type == "SystemMessage":
                        continue
                    if msg_type == "AIMessage" and not content:
                        continue
                    await websocket.send_json({
                        "type": msg_type,
                        "content": content
                    })

                # ── Escalation Check ──────────────────────────────────────
                # If the agent did NOT call restart_service this cycle,
                # increment the staleness counter for each active incident.
                # Fire a one-time escalation alert at ESCALATION_THRESHOLD.
                # ──────────────────────────────────────────────────────────
                tool_outputs = [
                    str(msg.content)
                    for msg in messages
                    if msg.__class__.__name__ == "ToolMessage"
                ]
                restart_executed = any(
                    "restarted successfully" in out for out in tool_outputs
                )

                for inc in env.active_incidents:
                    if restart_executed:
                        # Restart happened — reset counter for this incident
                        sim_state.incident_tick_counts.pop(inc.name, None)
                    else:
                        count = sim_state.incident_tick_counts.get(inc.name, 0) + 1
                        sim_state.incident_tick_counts[inc.name] = count

                        # Fire exactly once when threshold is crossed
                        if count == ESCALATION_THRESHOLD:
                            await websocket.send_json({
                                "type": "EscalationAlert",
                                "content": (
                                    f"🚨 ESCALATION — [{inc.name}] on {inc.service} "
                                    f"has been active for {count} agent cycles without "
                                    f"automated resolution. Human intervention required."
                                )
                            })

            except Exception as e:
                print(f"[WebSocket Error] graph.invoke failed: {e}")
                await websocket.send_json({
                    "type": "SystemMessage",
                    "content": f"Pipeline Error: {str(e)}"
                })

            # 1-second tick
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")