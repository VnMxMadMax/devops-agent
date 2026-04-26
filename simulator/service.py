from pydantic import BaseModel

class Metrics(BaseModel):
    cpu: float
    memory: float
    latency: float
    error_rate: float


class Thresholds(BaseModel):
    cpu: float
    memory: float
    latency: float
    error_rate: float


class Service(BaseModel):
    name: str
    role: str
    status: str
    metrics: Metrics
    thresholds: Thresholds
    baseline: Metrics


# api-gateway
api_gateway = Service(
    name="api-gateway",
    role="gateway",
    status="healthy",
    metrics=Metrics(cpu=35.0, memory=50.0, latency=100.0, error_rate=0.8),
    baseline=Metrics(cpu=35.0, memory=50.0, latency=100.0, error_rate=0.8),
    thresholds=Thresholds(cpu=75.0, memory=70.0, latency=150.0, error_rate=2.0)
)

# auth-service
auth_service = Service(
    name="auth-service",
    role="authentication",
    status="healthy",
    metrics=Metrics(cpu=28.0, memory=45.0, latency=70.0, error_rate=0.5),
    baseline=Metrics(cpu=28.0, memory=45.0, latency=70.0, error_rate=0.5),
    thresholds=Thresholds(cpu=65.0, memory=65.0, latency=120.0, error_rate=1.5)
)

# order-service
order_service = Service(
    name="order-service",
    role="business-logic",
    status="healthy",
    metrics=Metrics(cpu=50.0, memory=60.0, latency=130.0, error_rate=1.5),
    baseline=Metrics(cpu=50.0, memory=60.0, latency=130.0, error_rate=1.5),
    thresholds=Thresholds(cpu=85.0, memory=80.0, latency=200.0, error_rate=3.0)
)

# payment-service
payment_service = Service(
    name="payment-service",
    role="external-api",
    status="healthy",
    metrics=Metrics(cpu=32.0, memory=48.0, latency=180.0, error_rate=1.0),
    baseline=Metrics(cpu=32.0, memory=48.0, latency=180.0, error_rate=1.0),
    thresholds=Thresholds(cpu=70.0, memory=70.0, latency=250.0, error_rate=2.5)
)

# postgres-db
postgres_db = Service(
    name="postgres-db",
    role="database",
    status="healthy",
    metrics=Metrics(cpu=45.0, memory=70.0, latency=35.0, error_rate=0.3),
    baseline=Metrics(cpu=45.0, memory=70.0, latency=35.0, error_rate=0.3),
    thresholds=Thresholds(cpu=80.0, memory=85.0, latency=80.0, error_rate=1.0)
)


# Constant collection
SERVICES = [
    api_gateway,
    auth_service,
    order_service,
    payment_service,
    postgres_db
]


for service in SERVICES:
    print(service.name, "->", service.metrics, "| thresholds:", service.thresholds)