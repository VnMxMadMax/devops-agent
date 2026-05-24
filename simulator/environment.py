from datetime import datetime
from simulator.service import SERVICES
from simulator.incident import PREBUILT_INCIDENTS
from simulator.metric_generator import apply_incident_to_metrics, generate_normal_metrics
from simulator.log_generator import apply_incident_to_logs, generate_normal_logs

class SimulationEnvironment:
    def __init__(self):
        self.services = SERVICES
        self.active_incidents = []
        # Snapshot the original healthy baselines so resolve_incident can
        # fully reset a service — not just freeze it at its elevated state.
        self._original_baselines = {
            svc.name: svc.baseline.model_copy()
            for svc in self.services
        }
        
    def trigger_incident(self, incident_name: str):
        # Guard: don't allow the same incident to be active twice
        active_names = {inc.name for inc in self.active_incidents}
        if incident_name in active_names:
            return

        for inc in PREBUILT_INCIDENTS:
            if inc.name == incident_name:
                # Copy so PREBUILT_INCIDENTS template stays pristine
                # and the incident can be re-triggered after resolving.
                fresh = inc.model_copy()
                fresh.status = "active"
                fresh.start_time = datetime.utcnow()
                self.active_incidents.append(fresh)
                break
        
    def resolve_incident(self, incident_name: str):
        remaining = []
        for inc in self.active_incidents:
            if inc.name == incident_name:
                inc.status = "resolved"
                inc.end_time = datetime.utcnow()

                for svc in self.services:
                    if svc.name == inc.service:
                        # Reset to the ORIGINAL healthy baseline, not the
                        # current elevated state (which would lock in the fault).
                        orig = self._original_baselines[svc.name]
                        svc.baseline = orig.model_copy()
                        svc.metrics  = orig.model_copy()

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
