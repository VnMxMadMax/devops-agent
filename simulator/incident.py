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
    # FIX: Added log_impact so it can be accessed below
    log_impact: Optional[Dict[str, Any]] = None

    recovery_strategy: Optional[str] = None


# Incident #1: Memory leak in auth-service
auth_service_incident = Incident(
    name="memory_leak_auth",
    service="auth-service",
    severity="high",
    status="active",

    start_time=datetime.utcnow(),

    description="Memory leak in auth-service due to JWT decoding issue",
    root_cause="Improper memory handling during JWT decode",

    metric_impact={
        "memory": {
            "type": "increase",
            "rate": 0.5   # increases every tick
        }
    },

    log_impact={
        "level": "ERROR",
        "messages": [
            "JWT decode memory allocation failed",
            "OutOfMemoryError during token validation",
            "Heap allocation failure in auth-service"
        ],
        "frequency": 0.4   # 40% chance per tick
    }
)

PREBUILT_INCIDENTS = [
    auth_service_incident,
    # We can add more here later!
]

