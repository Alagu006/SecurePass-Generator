"""Quick migration - Run this while Flask app is running"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5555'),
    user=os.getenv('POSTGRES_USER', 'cyber_user'),
    password=os.getenv('POSTGRES_PASSWORD', 'CyberSecure123!'),
    dbname=os.getenv('POSTGRES_DB', 'password_security_db')
)
conn.autocommit = True
cursor = conn.cursor()

print("🔄 Running migration...")

# Add is_admin column
try:
    cursor.execute('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
    print("✅ Added is_admin column")
except Exception as e:
    if "already exists" in str(e):
        print("✅ is_admin column already exists")
    else:
        print(f"❌ Error adding is_admin: {e}")

# Create system_settings table
try:
    cursor.execute("""
        CREATE TABLE system_settings (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value VARCHAR(500) NOT NULL,
            description VARCHAR(200),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created system_settings table")
except Exception as e:
    if "already exists" in str(e):
        print("✅ system_settings table already exists")
    else:
        print(f"❌ Error creating table: {e}")

# Create user_activity table
try:
    cursor.execute("""
        CREATE TABLE user_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            activity_type VARCHAR(50) NOT NULL,
            details VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created user_activity table")
except Exception as e:
    if "already exists" in str(e):
        print("✅ user_activity table already exists")
    else:
        print(f"❌ Error creating table: {e}")

# Create indexes
try:
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity(created_at DESC)')
    print("✅ Created indexes")
except Exception as e:
    print(f"⚠️  Indexes: {e}")

# Insert default setting
try:
    cursor.execute("""
        INSERT INTO system_settings (setting_key, setting_value, description)
        VALUES ('require_email_confirmation', 'false', 'Require users to confirm email before login')
        ON CONFLICT (setting_key) DO NOTHING
    """)
    print("✅ Added default settings")
except Exception as e:
    print(f"⚠️  Settings: {e}")

# Update admin user
try:
    cursor.execute('UPDATE "user" SET is_admin = TRUE WHERE username = \'admin\'')
    print("✅ Updated admin user")
except Exception as e:
    print(f"⚠️  Admin update: {e}")

cursor.close()
conn.close()

print("\n✅ Migration complete! Restart Flask app.")
