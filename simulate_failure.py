import requests
import time
import sys

def trigger_payment_failure():
    print("🧨 Triggering Payment Service Failures (500 Errors)...")
    for _ in range(5):
        try:
            # Payment service has a 20% natural failure rate; we call it repeatedly to ensure errors
            requests.get("http://localhost:8080/process-transaction")
        except:
            pass
    print("✅ Done. Check alerts_dashboard.py for 'ConnectionRefused' alerts.")

def trigger_inventory_latency():
    print("⏳ Triggering Inventory Service Latency...")
    # This endpoint sleeps for a random duration; we call it to hit the >1.5s warning threshold
    for _ in range(3):
        requests.get("http://localhost:8081/sync")
    print("✅ Done. Check alerts_dashboard.py for 'slow_query' warnings.")

def trigger_auth_error():
    print("🔐 Triggering Auth Service Config Errors (403 Forbidden)...")
    for _ in range(5):
        requests.get("http://localhost:8082/validate")
    print("✅ Done. Check alerts_dashboard.py for 'invalid_issuer_config' alerts.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simulate_failure.py [payment|inventory|auth]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    if cmd == "payment": trigger_payment_failure()
    elif cmd == "inventory": trigger_inventory_latency()
    elif cmd == "auth": trigger_auth_error()
    else: print("Unknown command. Use payment, inventory, or auth.")