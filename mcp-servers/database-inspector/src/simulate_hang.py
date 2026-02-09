import psycopg2
import time

# Same config
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "password123",
    "dbname": "platform_db"
}

def create_hang():
    print("😈 Simulating a database lock for 60 seconds...")
    print("   (Go ask Claude to 'check performance' NOW!)")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # This command forces the database to sleep, effectively 
        # appearing as a "slow query" to your monitoring tool.
        cursor.execute("SELECT pg_sleep(60);")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
        print("✅ Simulation ended.")

if __name__ == "__main__":
    create_hang()