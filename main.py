
from simulator.service import SERVICES
from simulator.log_generator import generate_normal_logs
from simulator.metric_generator import generate_normal_metrics


def main():
    generate_normal_metrics(services=SERVICES)

    print("=== SERVICE STATUS ===")
    for service in SERVICES:
        print(f"{service.name} -> {service.status}")
        print(f"metrics   = {service.metrics}")
        print(f"baseline  = {service.baseline}")
        print("-" * 40)

    print("\n=== GENERATED LOGS ===")
    logs = generate_normal_logs(SERVICES)

    for log in logs:
        print(
            f"[{log['timestamp']}] "
            f"{log['service']} "
            f"{log['level']} - {log['message']}"
        )


if __name__ == "__main__":
    main()