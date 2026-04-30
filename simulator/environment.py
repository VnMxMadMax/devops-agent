from datetime import datetime
from simulator.service import SERVICES
from simulator.incident import PREBUILT_INCIDENTS
from simulator.metric_generator import apply_incident_to_metrics, generate_normal_metrics
from simulator.log_generator import apply_incident_to_logs, generate_normal_logs

class SimulationEnvironment:
    def __init__(self):
        # Load your SERVICES list here
        # Keep track of active incidents (empty list by default)
        self.services = SERVICES
        self.active_incidents = []
        
    def trigger_incident(self, incident_name: str):
        # Find the incident in PREBUILT_INCIDENTS by name
        # Add it to the active incidents list
        for inc in PREBUILT_INCIDENTS:
            if inc.name == incident_name:
                inc.status = "active"
                inc.start_time = datetime.utcnow()
                self.active_incidents.append(inc)
                break
        
    def resolve_incident(self, incident_name: str):
        # Remove the incident from the active incidents list
        # Bonus: Reset the affected service's baseline back to normal!
        remaining = []
        for inc in self.active_incidents:
            if inc.name == incident_name:
                inc.status = "resolved"
                inc.end_time = datetime.utcnow()

                for svc in self.services:
                    if svc.name == inc.service:
                        svc.baseline = svc.metrics.model_copy()

            else:
                remaining.append(inc)

        self.active_incidents = remaining
        
    def tick(self):
        """
        1 second of simulated time
        """
        # 1. Apply incident → shifts baseline
        for service in self.services:
            # 1. Apply incident → shifts baseline
            apply_incident_to_metrics(service, self.active_incidents)

        # 2. Generate metrics for ALL services (baseline + jitter)
        generate_normal_metrics(self.services)

        # 3. Generate logs
        logs = []
        for service in self.services:
            service_logs = generate_normal_logs([service])

            # 4. Inject incident logs
            service_logs = apply_incident_to_logs(
                service,
                service_logs,
                self.active_incidents
            )

            logs.extend(service_logs)

        # 5. Return system snapshot
        return self.services, logs
