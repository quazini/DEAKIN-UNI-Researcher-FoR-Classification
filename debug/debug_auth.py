"""
Debug page to check authentication configuration
"""

import streamlit as st
import os
from utils.config import get_config

st.set_page_config(page_title="Auth Debug", page_icon="🔍")

st.title("🔍 Authentication Debug")

# Check if user is admin (simple check for debugging)
if st.text_input("Debug Password:", type="password") != "debug123":
    st.error("Enter debug password to continue")
    st.stop()

st.success("Debug mode enabled")

# Check environment variables
st.header("Environment Variables")

env_vars = {
    "SUPABASE_URL": os.environ.get("SUPABASE_URL"),
    "SUPABASE_KEY": os.environ.get("SUPABASE_KEY"),
    "ADMIN_EMAIL": os.environ.get("ADMIN_EMAIL"),
    "APP_ENV": os.environ.get("APP_ENV"),
    "STREAMLIT_SERVER_HEADLESS": os.environ.get("STREAMLIT_SERVER_HEADLESS")
}

for key, value in env_vars.items():
    if value:
        if "KEY" in key:
            # Mask the key value
            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            st.code(f"{key}: {masked}")
        else:
            st.code(f"{key}: {value}")
    else:
        st.error(f"{key}: NOT SET ❌")

# Test Supabase connection
st.header("Supabase Connection Test")

try:
    config = get_config()
    supabase_config = config.get_supabase_config()

    st.write("URL:", supabase_config['url'])
    st.write("Key (first 10 chars):", supabase_config['key'][:10] + "...")

    # Try to make a simple request
    import requests

    url = f"{supabase_config['url']}/rest/v1/"
    headers = {
        "apikey": supabase_config['key'],
        "Authorization": f"Bearer {supabase_config['key']}"
    }

    response = requests.get(url, headers=headers, timeout=5)

    if response.status_code == 200:
        st.success(f"✅ Connection successful! Status: {response.status_code}")
    else:
        st.error(f"❌ Connection failed! Status: {response.status_code}")
        st.code(response.text[:500])

except Exception as e:
    st.error(f"Error: {str(e)}")

# Configuration debug
st.header("Configuration Debug")
config_debug = config.debug_config()
for key, value in config_debug.items():
    st.code(f"{key}: {value}")