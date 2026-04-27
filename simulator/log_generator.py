from datetime import datetime
import random


def generate_log(service_name: str, level: str, message: str) -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service_name,
        "level": level,
        "message": message
    }


def generate_normal_logs(services: list) -> list:
    logs = []

    # predefined realistic messages per service
    service_messages = {
        "api-gateway": [
            "GET /api/orders routed to order-service",
            "Request processed in 95ms",
            "POST /api/login routed to auth-service"
        ],
        "auth-service": [
            "JWT token validated for user_id=2847",
            "Session refreshed successfully",
            "User login successful"
        ],
        "order-service": [
            "Order #8821 created successfully",
            "Inventory check passed",
            "Order status updated to SHIPPED"
        ],
        "payment-service": [
            "Payment processed: txn_id=TXN9921",
            "External API responded in 175ms",
            "Payment authorization successful"
        ],
        "postgres-db": [
            "Query executed in 32ms: SELECT * FROM orders",
            "Connection pool: 8/20 active",
            "Index scan completed on users table"
        ]
    }

    for service in services:
        messages = service_messages.get(service.name, [])

        # pick 2–3 logs per service
        num_logs = random.randint(2, 3)
        selected_messages = random.sample(messages, k=num_logs)

        for msg in selected_messages:
            level = random.choices(
                ["INFO", "DEBUG"],
                weights=[0.8, 0.2]  # mostly INFO, some DEBUG
            )[0]

            log = generate_log(service.name, level, msg)
            logs.append(log)

    return logs

def apply_incident_to_logs(service, logs, incidents):
    """
    Injects realistic ERROR logs based on the active incident.
    """
    for incident in incidents:
        if incident.service == service.name and incident.status == "active" and incident.log_impact:
            
            # Use random chance to see if we emit an error log this tick
            if random.random() < incident.log_impact.get("frequency", 0.5):
                
                error_message = random.choice(
                    incident.log_impact.get("messages", ["Unknown error"])
                )

                # FIX: generate_log returns a dict, so we append it to our logs list
                logs.append(generate_log(
                    service.name,
                    incident.log_impact.get("level", "ERROR"),
                    error_message
                ))
    
    return logs