"""
Shared simulation environment singleton.

Both api/main.py and agents/tools.py import `env` and `last_logs` from here.
This guarantees the REST endpoints, WebSocket loop, and remediation
tools are all operating on the exact same SimulationEnvironment instance.
"""
from simulator.environment import SimulationEnvironment

env = SimulationEnvironment()

# Stores the log output from the most recent simulation tick.
# Updated by api/main.py after every tick so agents/tools.py
# can read real logs instead of hardcoded stubs.
last_logs: list = []

# Tracks how many consecutive agent cycles each active incident has gone
# without an automated restart. Used by main.py to fire escalation alerts.
# Keys: incident_name (str) | Values: cycle count (int)
incident_tick_counts: dict = {}
