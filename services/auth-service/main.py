from fastapi import FastAPI
import logging
import random
import os

app = FastAPI()

# Setup Logging
log_dir = "/app/shared-logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "auth-service.log"),
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "auth-service", "message": "%(message)s"}'
)

@app.get("/")
def home():
    return {"status": "Auth Service Running"}

@app.get("/validate")
def validate_token():
    # Simulate a "Bad Deploy" config error (403 Forbidden)
    if random.random() < 0.4:
        logging.error('{"event": "auth_fail", "reason": "invalid_issuer_config", "user_id": 992}')
        return {"error": "Configuration Error: Issuer Mismatch"}, 403
    
    logging.info('{"event": "auth_success", "user_id": 102}')
    return {"status": "valid"}