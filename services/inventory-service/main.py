from fastapi import FastAPI
import logging
import random
import os
import time

app = FastAPI()

# Setup Logging
log_dir = "/app/shared-logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "inventory-service.log"),
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "inventory-service", "message": "%(message)s"}'
)

@app.get("/")
def home():
    return {"status": "Inventory Service Running"}

@app.get("/sync")
def sync_stock():
    # Simulate a "Database Lock" (High Latency)
    delay = random.uniform(0.1, 2.0)
    time.sleep(delay)
    
    if delay > 1.5:
        logging.warning(f'{{"event": "slow_query", "duration_ms": {delay*1000}, "table": "products"}}')
    
    logging.info('{"event": "stock_updated", "items": 50}')
    return {"status": "synced", "latency": delay}