from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class Incident(BaseModel):
    # Basic identity
    name: str
    service: str
    severity: str
    status: str

    # Timeline
    start_time: datetime
    end_time: Optional[datetime] = None

    # Root cause / description
    description: Optional[str] = None
    root_cause: Optional[str] = None

    # Behavior overrides
    metric_impact: Dict[str, Any]
    log_impact: Optional[Dict[str, Any]] = None

    recovery_strategy: Optional[str] = None


# ── Incident #1: Memory leak in auth-service ──────────────────────────────────
auth_memory_leak = Incident(
    name="memory_leak_auth",
    service="auth-service",
    severity="high",
    status="inactive",
    start_time=datetime.utcnow(),
    description="Memory leak in auth-service due to JWT decoding issue",
    root_cause="Improper memory handling during JWT decode",
    metric_impact={
        "memory": {
            "type": "increase",
            "rate": 4.0  # breaches 65% threshold in ~5 ticks
        }
    },
    log_impact={
        "level": "ERROR",
        "messages": [
            "JWT decode memory allocation failed",
            "OutOfMemoryError during token validation",
            "Heap allocation failure in auth-service"
        ],
        "frequency": 0.4
    }
)

# ── Incident #2: CPU spike in api-gateway ─────────────────────────────────────
api_gateway_cpu_spike = Incident(
    name="cpu_spike_api_gateway",
    service="api-gateway",
    severity="high",
    status="inactive",
    start_time=datetime.utcnow(),
    description="CPU spike in api-gateway due to traffic burst",
    root_cause="Sudden traffic surge causing CPU overload and thread pool exhaustion",
    metric_impact={
        "cpu": {
            "type": "increase",
            "rate": 6.0  # breaches 75% threshold in ~7 ticks
        }
    },
    log_impact={
        "level": "WARN",
        "messages": [
            "High CPU utilization detected: thread pool under pressure",
            "Request processing throttled due to CPU saturation",
            "Worker thread exhaustion: incoming requests queued"
        ],
        "frequency": 0.5
    }
)

# ── Incident #3: Latency spike in payment-service ─────────────────────────────
payment_latency_spike = Incident(
    name="latency_spike_payment",
    service="payment-service",
    severity="medium",
    status="inactive",
    start_time=datetime.utcnow(),
    description="Latency spike in payment-service due to external gateway timeout",
    root_cause="External payment gateway slow response causing cascading latency",
    metric_impact={
        "latency": {
            "type": "increase",
            "rate": 18.0  # breaches 250ms threshold in ~4 ticks
        }
    },
    log_impact={
        "level": "ERROR",
        "messages": [
            "External payment gateway timeout: connection exceeded limit",
            "Retry limit exceeded for payment processor API",
            "Circuit breaker OPEN: payment-gateway-api"
        ],
        "frequency": 0.6
    }
)

# ── Incident #4: Error rate spike in order-service ────────────────────────────
order_error_spike = Incident(
    name="error_rate_order",
    service="order-service",
    severity="high",
    status="inactive",
    start_time=datetime.utcnow(),
    description="High error rate in order-service due to DB connection failures",
    root_cause="Database connection pool exhaustion causing cascading request failures",
    metric_impact={
        "error_rate": {
            "type": "increase",
            "rate": 0.7  # breaches 3.0% threshold in ~3 ticks
        }
    },
    log_impact={
        "level": "ERROR",
        "messages": [
            "Database connection pool exhausted: cannot acquire connection",
            "SQLException: too many connections to postgres-db",
            "Order processing failed: upstream database unavailable"
        ],
        "frequency": 0.7
    }
)

PREBUILT_INCIDENTS = [
    auth_memory_leak,
    api_gateway_cpu_spike,
    payment_latency_spike,
    order_error_spike,
]
