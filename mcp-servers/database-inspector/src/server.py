from mcp.server.fastmcp import FastMCP
import psycopg2
import psycopg2.extras
import json
import os

# Initialize the MCP Server
mcp = FastMCP("Database Inspector")

# Database Connection Config
# Since this script runs on your Host, it connects to localhost:5432
# which Docker maps to the container's 5432.
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "password123",
    "dbname": "platform_db"
}

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise RuntimeError(f"Failed to connect to database: {str(e)}")

@mcp.tool()
def list_tables() -> str:
    """List all tables in the public schema of the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = [row[0] for row in cursor.fetchall()]
        return json.dumps({"tables": tables}, indent=2)
    finally:
        conn.close()

@mcp.tool()
def check_performance() -> str:
    """Check for long-running queries or locks that might be slowing down the system."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        # Query Postgres internal stats for activities running longer than 1 second
        cursor.execute("""
            SELECT pid, state, query, age(clock_timestamp(), query_start) as duration
            FROM pg_stat_activity 
            WHERE state != 'idle' 
            AND query NOT LIKE '%pg_stat_activity%' 
            ORDER BY duration DESC;
        """)
        
        rows = [dict(row) for row in cursor.fetchall()]
        
        # Convert datetime objects to string for JSON serialization
        for row in rows:
            if 'duration' in row:
                row['duration'] = str(row['duration'])
                
        if not rows:
            return "No performance issues found. Database is healthy."
            
        return json.dumps({"long_running_queries": rows}, indent=2)
    finally:
        conn.close()

@mcp.tool()
def run_read_query(query: str) -> str:
    """Run a SAFE, READ-ONLY SQL query to inspect data. 
    Only SELECT queries are allowed.
    """
    if not query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for safety."

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        return json.dumps(rows, indent=2, default=str)
    except Exception as e:
        return f"Query Error: {str(e)}"
    finally:
        conn.close()

@mcp.tool()
def terminate_query(pid: int) -> str:
    """
    Terminate a specific database query by its Process ID (PID).
    Use this when a query is stuck, locking the database, or running too long.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Postgres command to kill a specific process
        cursor.execute("SELECT pg_terminate_backend(%s);", (pid,))
        return f"✅ Successfully terminated query with PID {pid}."
    except Exception as e:
        return f"❌ Failed to terminate query: {str(e)}"
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()