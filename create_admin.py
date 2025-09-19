#!/usr/bin/env python3
"""
Direct admin user creation script
This bypasses the secrets.toml reading issue and creates your admin user directly
"""

import requests
import json
from argon2 import PasswordHasher
from datetime import datetime

# Your Supabase credentials (hardcoded for this one-time setup)
SUPABASE_URL = "https://esgwrqcyhtzcsbepvqhc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzZ3dycWN5aHR6Y3NiZXB2cWhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzNzQ5NDUsImV4cCI6MjA2OTk1MDk0NX0.CqWWtD4fAMrlqo-RrlI2Q07DBgNGcvAdOMqJ5cUS2zg"
ADMIN_EMAIL = "nanvenfaden@gmail.com"

def create_admin_user():
    """Create admin user directly"""
    print("🔐 Creating Admin User...")
    print("=" * 40)

    # Initialize password hasher
    ph = PasswordHasher()

    # Admin credentials
    admin_password = "ChangeMe123!"
    hashed_password = ph.hash(admin_password)

    # API setup - use service role key approach
    api_url = f"{SUPABASE_URL}/rest/v1"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    print("ℹ️  Note: If RLS is enabled, we'll need to disable it temporarily or use service role key")

    # First, check if admin already exists
    print(f"\n1. Checking if admin user exists...")
    check_url = f"{api_url}/users"
    params = {"email": f"eq.{ADMIN_EMAIL}"}

    try:
        response = requests.get(check_url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            users = response.json()
            if users and len(users) > 0:
                print(f"✅ Admin user {ADMIN_EMAIL} already exists!")
                print(f"   You can login with:")
                print(f"   Email: {ADMIN_EMAIL}")
                print(f"   Password: (your existing password)")
                return True
        elif response.status_code == 404:
            print("❌ Users table doesn't exist. Please create it first!")
            print("\n📝 Go to your Supabase SQL Editor and run:")
            print("""
CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    last_login TIMESTAMP,
    password_reset_at TIMESTAMP
);
            """)
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

    # Create admin user
    print(f"\n2. Creating admin user: {ADMIN_EMAIL}")

    user_data = {
        'email': ADMIN_EMAIL,
        'password': hashed_password,
        'name': 'Administrator',
        'role': 'admin',
        'is_active': True,
        'created_at': datetime.now().isoformat(),
        'created_by': 'setup_script'
    }

    try:
        create_url = f"{api_url}/users"
        response = requests.post(create_url, headers=headers, json=user_data, timeout=10)

        if response.status_code == 201:
            print("🎉 SUCCESS! Admin user created!")
            print("=" * 40)
            print(f"📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Password: {admin_password}")
            print("=" * 40)
            print("\n📝 Next steps:")
            print("1. Run: streamlit run login.py")
            print("2. Login with the credentials above")
            print("3. Click '👑 Admin Panel' in the sidebar")
            print("4. Reset your password to something secure")
            print("\n⚠️  IMPORTANT: Change the password immediately after first login!")
            return True

        elif response.status_code == 409:
            print(f"ℹ️  User {ADMIN_EMAIL} already exists")
            print(f"   Try logging in with your existing password")
            return True

        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = create_admin_user()
    if success:
        print("\n🚀 You're all set! Run 'streamlit run login.py' to start using the app!")
    else:
        print("\n🚨 Setup failed. Please check the errors above and try again.")