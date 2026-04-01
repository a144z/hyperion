# data_logger.py

import json
import os
import time
from typing import Dict, Any
from .config import config

LOG_FILE = os.path.join(config.log_dir, "traces.jsonl")

def ensure_log_dir():
    os.makedirs(config.log_dir, exist_ok=True)

def log_failure(state, tactics, result):
    ensure_log_dir()
    with open(LOG_FILE, "a") as f:
        entry = {
            "timestamp": time.time(),
            "state_goal": state.goal,
            "tactics": tactics,
            "error_message": result.error_message,
            "first_error_token": result.first_error_token,
            "success": False
        }
        f.write(json.dumps(entry) + "\n")

def log_success(state, tactics):
    ensure_log_dir()
    with open(LOG_FILE, "a") as f:
        entry = {
            "timestamp": time.time(),
            "state_goal": state.goal,
            "tactics": tactics,
            "success": True
        }
        f.write(json.dumps(entry) + "\n")