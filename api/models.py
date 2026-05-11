from typing import List
from pydantic import BaseModel


class TriggerIncidentRequest(BaseModel):
    incident_name: str


class ServiceStatus(BaseModel):
    name: str
    status: str
    metrics: dict


class SimulationStatusResponse(BaseModel):
    services: List[ServiceStatus]
    active_incidents: List[str]