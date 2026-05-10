import time
from simulator.environment import SimulationEnvironment
from agents.orchestrator import graph


def main():
    # 1. Initialize environment
    env = SimulationEnvironment()

    # 2. Trigger incident
    env.trigger_incident("memory_leak_auth")

    print(">>> Simulation started... (Press Ctrl+C to stop)\n")

    while True:
        # 3. Run one tick
        services, logs = env.tick()

        # Convert Pydantic Service objects to dicts
        services_dict = [s.model_dump() for s in services]

        # Initial LangGraph state
        initial_state = {
            "services": services_dict,
            "logs": logs,
            "messages": [],
            "active_incident": [inc.name for inc in env.active_incidents]
        }

        # Invoke graph
        result = graph.invoke(initial_state)

        # Print latest agent messages
        print("\n=== AGENT OUTPUT ===")

        for msg in result["messages"][-4:]:
            print(msg)

        # 4. Print service state
        print("\n=== SERVICE STATUS ===")
        for service in services:
            print(f"{service.name} -> {service.status}")
            print(f"metrics   = {service.metrics}")
            print(f"baseline  = {service.baseline}")
            print("-" * 40)

        # 5. Print logs
        print("\n=== LOGS ===")
        for log in logs:
            print(
                f"[{log['timestamp']}] "
                f"{log['service']} "
                f"{log['level']} - {log['message']}"
            )

        # 6. Wait 1 second (heartbeat)
        time.sleep(1)


if __name__ == "__main__":
    main()