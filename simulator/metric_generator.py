import random

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def generate_normal_metrics(services: list):
    """
    Adds realistic jitter around baseline values.
    Prevents drift and enforces bounds.
    """
    for service in services:
        base = service.baseline

        # CPU & Memory (bounded 0–100)
        service.metrics.cpu = round(clamp(
            base.cpu + random.uniform(-2.0, 2.0), 0.0, 100.0
        ),2)
        service.metrics.memory = round(clamp(
            base.memory + random.uniform(-2.0, 2.0), 0.0, 100.0
        ),2)

        # Latency (>= 0, jitter around baseline)
        service.metrics.latency = round(max(
            0.0,
            base.latency + random.uniform(-10.0, 10.0)
        ),2)

        # Error rate (>= 0, small jitter)
        service.metrics.error_rate = round(max(
            0.0,
            base.error_rate + random.uniform(-0.2, 0.2)
        ), 3)

def apply_incident_to_metrics(service, incidents):
    """
    Instead of modifying the metrics directly (which get overwritten by the jitter),
    an active incident modifies the service BASELINE. 
    Then, the metric_generator naturally adds jitter around the new, broken baseline!
    """
    for incident in incidents:
        if incident.service == service.name and incident.status == "active":
            for metric_name, rule in incident.metric_impact.items():
                
                # FIX: Use getattr/setattr to dynamically update Pydantic models
                current_baseline = getattr(service.baseline, metric_name)
                
                if rule["type"] == "increase":
                    # E.g., for a memory leak, increase the baseline slowly every tick
                    setattr(service.baseline, metric_name, current_baseline + rule["rate"])

                elif rule["type"] == "spike":
                    # Immediately jump the baseline to a specific high value
                    setattr(service.baseline, metric_name, rule["value"])

                elif rule["type"] == "decrease":
                    setattr(service.baseline, metric_name, current_baseline - rule["rate"])