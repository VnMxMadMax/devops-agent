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