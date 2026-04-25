# Imports SERVICES from simulator/services.py
# Imports generate_normal_logs from simulator/log_generator.py
# Prints each service name + status
# Generates normal logs and prints each one

from simulator.service import SERVICES
from simulator.log_generator import generate_normal_logs


def main():
    print("=== SERVICE STATUS ===")
    for service in SERVICES:
        print(f"{service.name} -> {service.status}")

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