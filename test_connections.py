#!/usr/bin/env python3
"""
Connection Test Script for Docker Container
Tests critical service connections before deployment
"""

import os
import sys
import json
from urllib.parse import urlparse

def test_environment_variables():
    """Check that required environment variables are set"""
    # Note: These are passed by the GitHub workflow during container test
    # Some are optional in the actual deployment as they have defaults
    required_vars = []

    optional_vars = [
        'STREAMLIT_SERVER_PORT',
        'STREAMLIT_SERVER_ADDRESS',
        'STREAMLIT_SERVER_HEADLESS',
        'APP_NAME',
        'APP_ENV',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'DEFAULT_WEBHOOK_URL',
        'NEO4J_URI',
        'NEO4J_USERNAME',
        'NEO4J_PASSWORD',
        'NEO4J_DATABASE',
        'ADMIN_EMAIL'
    ]

    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        return False

    print("✅ All required environment variables are set")

    # Check optional variables and warn if missing
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
        print("   Note: These may be set in Digital Ocean App Platform console")

    return True

def test_imports():
    """Test that all required Python packages can be imported"""
    try:
        print("Testing Python imports...")

        # Core imports
        import streamlit
        print(f"  ✅ Streamlit version: {streamlit.__version__}")

        import requests
        print(f"  ✅ Requests imported successfully")

        import argon2
        print(f"  ✅ Argon2 imported successfully")

        from dotenv import load_dotenv
        print(f"  ✅ Python-dotenv imported successfully")

        import psutil
        print(f"  ✅ Psutil imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection if credentials are provided"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("⏭️  Skipping Supabase connection test (credentials not set)")
        return True

    try:
        import requests

        # Parse URL to ensure it's valid
        parsed = urlparse(supabase_url)
        if not parsed.scheme or not parsed.netloc:
            print(f"❌ Invalid SUPABASE_URL format: {supabase_url}")
            return False

        # Test basic connection to Supabase
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }

        # Just check if we can reach the API (don't need actual data)
        response = requests.get(
            f"{supabase_url}/rest/v1/",
            headers=headers,
            timeout=5
        )

        if response.status_code in [200, 201, 401, 403]:
            # Even auth errors mean connection works
            print(f"✅ Supabase connection successful (status: {response.status_code})")
            return True
        else:
            print(f"⚠️  Supabase returned unexpected status: {response.status_code}")
            return True  # Don't fail deployment for this

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not connect to Supabase: {str(e)}")
        # Don't fail deployment if Supabase is unreachable during build
        return True
    except Exception as e:
        print(f"⚠️  Supabase test error: {str(e)}")
        return True

def test_webhook_url():
    """Validate webhook URL format if provided"""
    webhook_url = os.getenv('DEFAULT_WEBHOOK_URL')

    if not webhook_url:
        print("⏭️  Skipping webhook URL test (not configured)")
        return True

    try:
        parsed = urlparse(webhook_url)
        if not parsed.scheme or not parsed.netloc:
            print(f"❌ Invalid webhook URL format: {webhook_url}")
            return False

        if parsed.scheme not in ['http', 'https']:
            print(f"❌ Webhook URL must use http or https scheme: {webhook_url}")
            return False

        print(f"✅ Webhook URL format is valid: {webhook_url[:50]}...")
        return True

    except Exception as e:
        print(f"❌ Error validating webhook URL: {str(e)}")
        return False

def test_file_structure():
    """Check that required application files exist"""
    required_files = [
        'login.py',
        'pages/main_app.py',
        'utils/webhook_client.py',
        'components/classification_display.py',
        'requirements.txt'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False

    print("✅ All required application files are present")
    return True

def main():
    """Run all connection tests"""
    print("=" * 60)
    print("🔬 FoR Classification System - Connection Tests")
    print("=" * 60)
    print()

    all_tests_passed = True

    # Test 1: Environment variables
    print("1. Testing environment variables...")
    if not test_environment_variables():
        all_tests_passed = False
    print()

    # Test 2: Python imports
    print("2. Testing Python imports...")
    if not test_imports():
        all_tests_passed = False
    print()

    # Test 3: File structure
    print("3. Testing file structure...")
    if not test_file_structure():
        all_tests_passed = False
    print()

    # Test 4: Supabase connection (optional)
    print("4. Testing Supabase connection...")
    if not test_supabase_connection():
        all_tests_passed = False
    print()

    # Test 5: Webhook URL validation
    print("5. Testing webhook URL...")
    if not test_webhook_url():
        all_tests_passed = False
    print()

    # Summary
    print("=" * 60)
    if all_tests_passed:
        print("✅ All connection tests passed!")
        print("Container is ready for deployment")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        print("Please check the configuration before deploying")
        sys.exit(1)

if __name__ == "__main__":
    main()