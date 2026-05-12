import asyncio

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

from simulator.environment import SimulationEnvironment

from agents.orchestrator import graph

app = FastAPI(title="Sentinel AI")

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
# Shared environment — used by both REST endpoints and the WebSocket
env = SimulationEnvironment()

# Alias so the WebSocket handler can reference the shared env by its own name
ws_env = env


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


@app.post("/incident/resolve")
async def resolve_incident(
    request: TriggerIncidentRequest
):
    env.resolve_incident(request.incident_name)

    return {
        "message": f"Incident resolved: {request.incident_name}"
    }


@app.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket):

    await websocket.accept()

    # Use the SHARED env so REST endpoints can control this simulation
    ws_env.trigger_incident("memory_leak_auth")

    try:
        while True:

            # Advance simulation
            services, logs = ws_env.tick()

            # Build LangGraph state
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
                    for inc in ws_env.active_incidents
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

                # Stream messages to frontend
                messages = result.get("messages", [])
                if messages:
                    for msg in messages:
                        await websocket.send_json({
                            "type": msg.__class__.__name__,
                            "content": str(msg.content)
                        })
                else:
                    # Send a heartbeat so client knows the system is healthy
                    await websocket.send_json({
                        "type": "heartbeat",
                        "content": "System healthy — no alerts this tick"
                    })
            except Exception as e:
                print(f"[WebSocket Error] graph.invoke failed: {e}")
                await websocket.send_json({
                    "type": "SystemMessage",
                    "content": f"Pipeline Error: {str(e)}"
                })

            # 1-second heartbeat
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")