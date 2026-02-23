#!/usr/bin/env python3
"""
Quick setup script for Password Security Toolkit
Helps generate SECRET_KEY and check environment
"""

import secrets
import os
import sys

def generate_secret_key():
    """Generate a cryptographically secure SECRET_KEY"""
    return secrets.token_hex(32)

def check_env_file():
    """Check if .env file exists"""
    return os.path.exists('.env')

def create_env_file():
    """Create .env file from .env.example"""
    if not os.path.exists('.env.example'):
        print("❌ .env.example file not found!")
        return False
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    # Generate SECRET_KEY
    secret_key = generate_secret_key()
    content = content.replace('generate-a-secure-key-here', secret_key)
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ .env file created successfully!")
    print(f"✅ Generated SECRET_KEY: {secret_key[:20]}...")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_wtf
        import flask_limiter
        import psycopg2
        import bcrypt
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("Run: pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("\n🔐 Password Security Toolkit - Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check .env file
    if check_env_file():
        print("✅ .env file exists")
        response = input("\n⚠️  Do you want to regenerate .env file? (y/N): ")
        if response.lower() == 'y':
            create_env_file()
    else:
        print("⚠️  .env file not found")
        response = input("   Create .env file from template? (Y/n): ")
        if response.lower() != 'n':
            create_env_file()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n💡 Install dependencies with:")
        print("   pip install -r requirements.txt")
        return
    
    # Generate new SECRET_KEY if needed
    print("\n🔑 SECRET_KEY Management")
    response = input("   Generate a new SECRET_KEY? (y/N): ")
    if response.lower() == 'y':
        new_key = generate_secret_key()
        print(f"\n   New SECRET_KEY: {new_key}")
        print("\n   Add this to your .env file:")
        print(f"   SECRET_KEY={new_key}")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📝 Next steps:")
    print("   1. Edit .env file with your database credentials")
    print("   2. Run: python init_postgres.py")
    print("   3. Run: python app.py")
    print("   4. Open: http://localhost:6001")
    print("\n👤 Default admin credentials:")
    print("   Username: admin")
    print("   Password: Admin@123")
    print("\n⚠️  Change the admin password after first login!")
    print("=" * 50 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
