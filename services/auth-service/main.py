from fastapi import FastAPI, Response
import logging
import random
import os
import json
from datetime import datetime

app = FastAPI()

# Standardize path to match your Docker Compose volume
LOG_DIR = "/app/shared-logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "auth-service.log")

# Configure logging to write raw messages (we will format the JSON ourselves)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "auth-service", "message": "%(message)s"}'
)

def log_event(level: str, message: str, extra: dict = None):
    """Helper to ensure logs are perfectly formatted JSON for the AI"""
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": "auth-service",
        "message": message
    }
    if extra:
        payload.update(extra)
    logging.info(json.dumps(payload))

@app.get("/validate")
def validate_token(response: Response):
    # 40% chance of a "Bad Configuration" failure
    if random.random() < 0.4:
        log_event("ERROR", "Configuration Error: Issuer Mismatch", {"error_code": "invalid_issuer_config"})
        response.status_code = 403
        return {"error": "Unauthorized", "detail": "Issuer mismatch detected"}
    
    log_event("INFO", "Token validated successfully", {"user_id": random.randint(1000, 9999)})
    return {"status": "valid"}