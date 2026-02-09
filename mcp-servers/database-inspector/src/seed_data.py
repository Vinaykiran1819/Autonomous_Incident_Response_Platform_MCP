import psycopg2

# Database Connection Config
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "password123",
    "dbname": "platform_db"
}

def seed_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        print("🚀 creating tables...")
        
        # 1. Create Users Table
        cursor.execute("""
            DROP TABLE IF EXISTS users CASCADE;
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Create Payments Table (This simulates our 'Payment Service')
        cursor.execute("""
            DROP TABLE IF EXISTS payments CASCADE;
            CREATE TABLE payments (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id),
                amount DECIMAL(10, 2),
                status TEXT CHECK (status IN ('pending', 'completed', 'failed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("🌱 Inserting mock data...")

        # 3. Insert Mock Users
        cursor.execute("""
            INSERT INTO users (name, email) VALUES 
            ('Alice Smith', 'alice@example.com'),
            ('Bob Jones', 'bob@example.com'),
            ('Charlie Brown', 'charlie@example.com');
        """)

        # 4. Insert Mock Payments
        cursor.execute("""
            INSERT INTO payments (user_id, amount, status) VALUES 
            (1, 100.50, 'completed'),
            (1, 25.00, 'failed'),
            (2, 200.00, 'pending'),
            (3, 50.00, 'completed');
        """)

        print("✅ Database successfully seeded!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    seed_database()