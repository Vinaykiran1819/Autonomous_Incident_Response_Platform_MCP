from fastapi import FastAPI, Response
import logging
import random
import os
import json
import time
from datetime import datetime

app = FastAPI()

LOG_DIR = "/app/shared-logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "inventory-service.log")

logging.basicConfig(
        filename=LOG_FILE, 
        level=logging.INFO, 
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "inventory-service", "message": "%(message)s"}'
        )

def log_event(level: str, message: str, extra: dict = None):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": "inventory-service",
        "message": message
    }
    if extra: payload.update(extra)
    logging.info(json.dumps(payload))

@app.get("/check-stock")
def check_stock(response: Response):
    # Simulate high latency (slowness)
    delay = random.uniform(0.1, 2.0)
    time.sleep(delay)
    
    if delay > 1.5:
        log_event("WARNING", f"Slow database query detected: {delay}s", {"latency": delay})
    
    log_event("INFO", "Inventory check completed", {"stock_status": "in_stock"})
    return {"status": "available", "latency": delay}