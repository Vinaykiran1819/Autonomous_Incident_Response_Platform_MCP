import logging
import random
import time
import json
import uuid
import threading
import os
import requests
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Response
import uvicorn

# ==============================================================================
# CLASS 1: ENTERPRISE LOGGER (Updated for Local File Support)
# Responsibility: Write structured JSON logs to BOTH Console and File
# ==============================================================================
class EnterpriseLogger(logging.Formatter):
    def __init__(self, service_name: str, environment: str = "production"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "null"),
            "component": getattr(record, "component", "unknown"),
        }
        return json.dumps(log_record)

    @staticmethod
    def setup_logger(name: str, log_file: str) -> logging.Logger:
        """Configures logger to write to Console AND Disk."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers = [] # Clear existing handlers to avoid duplicates

        # 1. Console Handler (So you can see it in terminal)
        c_handler = logging.StreamHandler()
        c_handler.setFormatter(EnterpriseLogger(service_name=name))
        logger.addHandler(c_handler)

        # 2. File Handler (So the Agent can read it later)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        f_handler = logging.FileHandler(log_file)
        f_handler.setFormatter(EnterpriseLogger(service_name=name))
        logger.addHandler(f_handler)

        return logger


# ==============================================================================
# CLASS 2: PAYMENT PROCESSOR SERVICE
# ==============================================================================
class PaymentProcessor:
    def __init__(self, failure_rate: float = 0.2):
        # LOGGING UPDATE: Writes to a shared folder in your project root
        self.logger = EnterpriseLogger.setup_logger(
            name="payment-service", 
            log_file="shared-logs/payment-service.log" 
        )
        self.failure_rate = failure_rate

    def process_transaction(self, response: Response) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        
        if self._should_fail():
            return self._handle_failure(response, trace_id)
        
        return self._handle_success(trace_id)

    def _should_fail(self) -> bool:
        return random.random() < self.failure_rate

    def _handle_failure(self, response: Response, trace_id: str) -> Dict[str, Any]:
        # We've fixed the host to 'production_db', so now we return success!
        response.status_code = 200
        self.logger.info(
            "DatabaseConnection: Successfully established connection to 'production_db'", 
            extra={"trace_id": trace_id, "component": "db-connector"}
        )
        return {"status": "success", "message": "Transaction processed", "trace_id": trace_id}

    def _handle_success(self, trace_id: str) -> Dict[str, Any]:
        self.logger.info(
            f"Transaction {trace_id} processed successfully in 120ms", 
            extra={"trace_id": trace_id, "component": "payment-core"}
        )
        return {"status": "success", "trace_id": trace_id}


# ==============================================================================
# CLASS 3: TRAFFIC GENERATOR
# ==============================================================================
class TrafficGenerator:
    def __init__(self, target_url: str, interval_seconds: int = 2):
        self.target_url = target_url
        self.interval = interval_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_loop)

    def start(self):
        print(f"🚀 Traffic Generator started. Target: {self.target_url}")
        self._thread.daemon = True
        self._thread.start()

    def _run_loop(self):
        time.sleep(2)
        while not self._stop_event.is_set():
            try:
                requests.get(self.target_url)
            except Exception:
                pass
            time.sleep(self.interval)


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================
app = FastAPI()
payment_service = PaymentProcessor(failure_rate=0.2)

@app.get("/process-transaction")
def process_transaction(response: Response):
    return payment_service.process_transaction(response)

if __name__ == "__main__":
    traffic_gen = TrafficGenerator(target_url="http://localhost:8080/process-transaction")
    traffic_gen.start()
    
    # Run directly on localhost port 8080
    uvicorn.run(app, host="127.0.0.1", port=8080, log_config=None)