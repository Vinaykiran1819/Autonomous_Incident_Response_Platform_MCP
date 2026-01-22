from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
import os
import sys
from pathlib import Path
from typing import Optional

# ==============================================================================
# CONFIGURATION
# ==============================================================================
mcp = FastMCP("Log Analyst")

# 1. Get the absolute path of THIS script
current_script_path = Path(__file__).resolve()

# 2. Go up 3 levels to find the Project Root
# server.py -> log-analyst -> mcp-servers -> Autonomous_Incident_Response_Platform_MCP
project_root = current_script_path.parent.parent.parent

# 3. Define the absolute path to shared-logs
LOG_DIR = project_root / "shared-logs"

# Debug: Print to console (visible in Inspector)
print(f"DEBUG: Log Analyst initialized. Root: {project_root}", file=sys.stderr)
print(f"DEBUG: Looking for logs at: {LOG_DIR}", file=sys.stderr)

def _load_df(service_name: Optional[str] = None) -> pd.DataFrame:
    """Helper to load JSON logs into a DataFrame"""
    all_records = []
    log_dir_str = str(LOG_DIR) # Convert Path to string for os functions

    # DEBUG CHECK: If folder is missing, return empty
    if not os.path.exists(log_dir_str):
        print(f"DEBUG: FOLDER MISSING: {log_dir_str}", file=sys.stderr)
        return pd.DataFrame()
    
    files = [f for f in os.listdir(log_dir_str) if f.endswith('.log')]
    
    for file in files:
        if service_name and service_name not in file: continue
        try:
            full_path = os.path.join(log_dir_str, file)
            with open(full_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            all_records.append(json.loads(line))
                        except: continue
        except Exception as e:
            print(f"Error reading {file}: {e}", file=sys.stderr)
            continue
        
    df = pd.DataFrame(all_records)
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
    return df

@mcp.tool()
def get_error_stats(service_name: str) -> str:
    """Get error counts and patterns for a specific service"""
    df = _load_df(service_name)
    
    # DEBUG RESPONSE: Tell the user where we looked if empty
    if df.empty:
        return f"No logs found for '{service_name}'. I searched in: {LOG_DIR}. Is the file 'payment-service.log' there?"

    error_df = df[df['level'] == 'ERROR']
    total_errors = len(error_df)
    
    if total_errors == 0:
        return json.dumps({"status": "healthy", "total_errors": 0})
        
    patterns = error_df['message'].value_counts().head(3).to_dict()
    
    return json.dumps({
        "total_errors": total_errors,
        "top_patterns": patterns,
        "checked_path": str(LOG_DIR) # Confirm path in success case too
    }, indent=2)

if __name__ == "__main__":
    mcp.run()