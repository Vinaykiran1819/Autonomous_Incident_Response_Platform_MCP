import os
import json
import time
from pathlib import Path

# Paths to the shared logs
LOG_DIR = Path("./shared-logs")

def scan_logs():
    print("\n" + "="*50)
    print("🚀 INCIDENT COMMAND DASHBOARD - MONITORING SERVICES")
    print("="*50 + "\n")

    while True:
        if not LOG_DIR.exists():
            continue

        for log_file in LOG_DIR.glob("*.log"):
            service_name = log_file.stem
            with open(log_file, 'r') as f:
                # Read the last line (the most recent event)
                lines = f.readlines()
                if not lines: continue
                
                try:
                    last_log = json.loads(lines[-1])
                    level = last_log.get("level", "INFO")
                    
                    if level in ["ERROR", "WARNING"]:
                        print(f"🚨 ALERT: {service_name.upper()} is reporting {level}!")
                        print(f"   Message: {last_log.get('message')}")
                        print(f"   👉 ACTION: Copy this to your MCP Client: ")
                        print(f"      'Investigate {service_name} and resolve the root cause.'\n")
                except:
                    continue
        
        time.sleep(3) # Check every 3 seconds

if __name__ == "__main__":
    scan_logs()