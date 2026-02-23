#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script
Run this before starting the Flask app
"""

try:
    import psycopg
    from psycopg import sql
    USING_PSYCOPG3 = True
except ImportError:
    import psycopg2 as psycopg
    from psycopg2 import sql
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    USING_PSYCOPG3 = False

import getpass
import sys

def create_database():
    """Create PostgreSQL database and user"""
    
    print("🔧 PostgreSQL Database Setup")
    print("=" * 50)
    
    # Get PostgreSQL credentials
    print("\nEnter PostgreSQL superuser credentials:")
    pg_user = input("Superuser username [postgres]: ") or "postgres"
    pg_password = getpass.getpass("Superuser password: ")
    pg_host = input("Host [localhost]: ") or "localhost"
    pg_port = input("Port [5432]: ") or "5432"
    
    try:
        # Connect to PostgreSQL server (default database)
        print("\n🔌 Connecting to PostgreSQL...")
        connection = psycopg.connect(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            dbname='postgres',
            autocommit=True
        )
        cursor = connection.cursor()
        
        # Database and user details
        db_name = 'password_security_db'
        db_user = 'cyber_user'
        db_password = 'CyberSecure123!'  # Change this!
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"⚠️  Database '{db_name}' already exists")
            overwrite = input("Do you want to drop and recreate it? (yes/no): ")
            if overwrite.lower() == 'yes':
                cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name)))
                print(f"🗑️  Dropped existing database '{db_name}'")
            else:
                print("Keeping existing database")
                cursor.close()
                connection.close()
                return
        
        # Create database
        print(f"\n📦 Creating database '{db_name}'...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            print(f"👤 Creating user '{db_user}'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(db_user)),
                (db_password,)
            )
        else:
            print(f"👤 User '{db_user}' already exists")
        
        # Grant privileges on database
        print(f"🔑 Granting database privileges...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(db_name),
                sql.Identifier(db_user)
            )
        )
        
        cursor.close()
        connection.close()
        
        # Connect to the new database to grant schema privileges
        print(f"🔑 Granting schema privileges...")
        schema_conn = psycopg.connect(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            dbname=db_name,
            autocommit=True
        )
        schema_cursor = schema_conn.cursor()
        
        # Grant schema privileges
        schema_cursor.execute(
            sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(sql.Identifier(db_user))
        )
        schema_cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {}").format(sql.Identifier(db_user))
        )
        schema_cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {}").format(sql.Identifier(db_user))
        )
        schema_cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(sql.Identifier(db_user))
        )
        schema_cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {}").format(sql.Identifier(db_user))
        )
        
        schema_cursor.close()
        schema_conn.close()
        
        # Connect to new database and create tables
        print(f"\n📋 Creating tables in '{db_name}'...")
        create_tables(pg_host, pg_port, db_name, db_user, db_password)
        
        print("\n✅ PostgreSQL setup complete!")
        print("\n📋 Connection Details:")
        print(f"   Host: {pg_host}")
        print(f"   Port: {pg_port}")
        print(f"   Database: {db_name}")
        print(f"   Username: {db_user}")
        print(f"   Password: {db_password}")
        
        print("\n💡 Next steps:")
        print("   1. Update .env file with these credentials")
        print("   2. Run: python app.py")
        
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   - Make sure PostgreSQL server is running")
        print("   - Check username/password")
        print("   - Windows: Check Services for PostgreSQL")
        print("   - Verify connection: psql -U postgres")
        sys.exit(1)

def create_tables(host, port, database, user, password):
    """Create application tables"""
    
    try:
        connection = psycopg.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email_confirmed BOOLEAN DEFAULT FALSE,
                email_confirmed_at TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMP,
                last_login TIMESTAMP,
                password_reset_token VARCHAR(100),
                password_reset_expires TIMESTAMP
            )
        """)
        print("   ✓ Created 'user' table")
        
        # Create password_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
                password_length INTEGER NOT NULL,
                strength_score INTEGER NOT NULL,
                strength_level VARCHAR(20) NOT NULL,
                feedback TEXT NOT NULL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✓ Created 'password_history' table")
        
        # Create login_attempt table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempt (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
                username_attempted VARCHAR(80) NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                user_agent VARCHAR(200),
                success BOOLEAN DEFAULT FALSE,
                failure_reason VARCHAR(100),
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✓ Created 'login_attempt' table")
        
        # Create system_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value VARCHAR(500) NOT NULL,
                description VARCHAR(200),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✓ Created 'system_settings' table")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_username 
            ON "user"(username)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_email 
            ON "user"(email)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_history_user_id 
            ON password_history(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_history_analyzed_at 
            ON password_history(analyzed_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_attempt_user_id 
            ON login_attempt(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_attempt_attempted_at 
            ON login_attempt(attempted_at DESC)
        """)
        print("   ✓ Created indexes")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("   ✓ All tables created successfully")
        
    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
        sys.exit(1)

def update_env_file():
    """Update .env file with PostgreSQL configuration"""
    
    env_content = """# Database Configuration (PostgreSQL)
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=cyber_user
POSTGRES_PASSWORD=CyberSecure123!
POSTGRES_DB=password_security_db

# App Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Updated .env file with PostgreSQL configuration")
    except Exception as e:
        print(f"\n⚠️  Could not update .env file: {e}")
        print("Please update it manually with the connection details above")

if __name__ == "__main__":
    print("🔐 Password Security Toolkit - PostgreSQL Setup")
    print("=" * 50)
    
    # Check if psycopg is installed
    try:
        import psycopg
    except ImportError:
        print("❌ psycopg is not installed!")
        print("\nInstall it with:")
        print("   pip install psycopg")
        sys.exit(1)
    
    create_database()
    update_env_file()
    
    print("\n🎉 Setup complete! Your database is ready to use.")
