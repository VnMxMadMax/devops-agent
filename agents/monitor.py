from typing import Dict, Any
from agents.orchestrator import AgentState


def monitor_node(state: AgentState) -> Dict[str, Any]:
    """
    Monitor node checks all services for threshold breaches.

    It compares each service's current metrics against its defined thresholds.
    If any metric exceeds its threshold, an alert is generated.

    Returns:
    - {"alert": {...}} if breach detected
    - {"alert": None} if system is healthy
    """

    services = state.get("services", [])

    for service in services:
        service_name = service.get("name")

        metrics = service.get("metrics", {})
        thresholds = service.get("thresholds", {})

        # Check each metric
        for metric_name in ["cpu", "memory", "latency", "error_rate"]:
            current_value = metrics.get(metric_name)
            threshold_value = thresholds.get(metric_name)

            # Skip if missing data
            if current_value is None or threshold_value is None:
                continue

            # Threshold breach condition
            if current_value > threshold_value:
                alert = {
                    "service": service_name,
                    "metric": metric_name,
                    "value": current_value,
                    "threshold": threshold_value,
                    "severity": _calculate_severity(current_value, threshold_value)
                }

                return {"alert": alert}

    # No issues found
    return {"alert": None}


def _calculate_severity(value: float, threshold: float) -> str:
    """
    Simple severity calculation based on how much the metric exceeds threshold.
    """

    ratio = value / threshold

    if ratio >= 1.5:
        return "critical"
    elif ratio >= 1.2:
        return "high"
    elif ratio >= 1.05:
        return "medium"
    else:
        return "low"