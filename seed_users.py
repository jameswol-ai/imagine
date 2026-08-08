import bcrypt
import psycopg2

# Database connection details (Replace with your actual Render/Local PostgreSQL credentials)
DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "your_db_user",
    "password": "your_db_password",
    "host": "your_db_host",  # e.g., "dpg-xxxx-a.render.com" or "localhost"
    "port": "5432"
}

# Seed accounts: Plain-text password will be hashed before insertion
SEED_USERS = [
    {
        "username": "admin_user",
        "password": "AdminPassword123!",
        "role": "Admin"
    },
    {
        "username": "pm_jane",
        "password": "PM_Password2026!",
        "role": "Project Manager"
    },
    {
        "username": "eng_mark",
        "password": "EngineerPass2026!",
        "role": "Lead Engineer"
    },
    {
        "username": "inspector_sam",
        "password": "InspectPass123!",
        "role": "Junior Inspector"
    }
]

def hash_password(password: str) -> str:
    """Generates a salt and hashes a plain-text password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def seed_database():
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Ensure table schema exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(30) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Insert or update seed users
        insert_query = """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO UPDATE 
            SET password_hash = EXCLUDED.password_hash, 
                role = EXCLUDED.role;
        """

        for user in SEED_USERS:
            hashed_pw = hash_password(user["password"])
            cursor.execute(insert_query, (user["username"], hashed_pw, user["role"]))
            print(f"  [+] Seeded user: '{user['username']}' | Role: '{user['role']}'")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n✅ Database user seeding completed successfully!")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")

if __name__ == "__main__":
    seed_database()
