"""
Configuration Debug Page
Shows current configuration sources and values for troubleshooting
"""

import streamlit as st
from utils.config import get_config
from utils.flexible_auth import require_authentication, check_authentication

# Configure page
st.set_page_config(
    page_title="🔧 Configuration Debug",
    page_icon="🔧",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.switch_page("login.py")

require_authentication()

# Get current user info to check if admin
auth_manager = st.session_state.get('auth_manager')
current_user = st.session_state.get('user', {})

# Only allow admins to see config debug
if current_user.get('role') != 'admin':
    st.error("🚫 Access denied. Admin role required.")
    st.info("Contact your administrator for access to configuration debugging.")
    st.stop()

st.title("🔧 Configuration Debug")
st.markdown("**Admin Only** - Configuration sources and current values")

# Get configuration
config = get_config()

# Show configuration sources
st.header("📋 Configuration Sources")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌐 Environment Variables")
    env_vars = [
        'SUPABASE_URL', 'SUPABASE_KEY', 'DEFAULT_WEBHOOK_URL',
        'ADMIN_EMAIL', 'APP_NAME', 'APP_ENV', 'SESSION_TIMEOUT_MINUTES'
    ]

    for var in env_vars:
        import os
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'URL' in var:
                display_value = value[:20] + '...' if len(value) > 20 else value
            else:
                display_value = value
            st.success(f"✅ {var}: {display_value}")
        else:
            st.error(f"❌ {var}: Not set")

with col2:
    st.subheader("📁 .env File")
    from pathlib import Path
    env_file = Path('.env')

    if env_file.exists():
        st.success("✅ .env file found")
        try:
            with open(env_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            st.info(f"📄 Contains {len(lines)} configuration lines")

            # Show variables (masked)
            for line in lines[:10]:  # Show first 10 lines
                if '=' in line:
                    key = line.split('=')[0]
                    st.text(f"• {key}")
        except Exception as e:
            st.error(f"❌ Error reading .env: {e}")
    else:
        st.warning("⚠️ .env file not found")

with col3:
    st.subheader("🔐 Streamlit Secrets")
    secrets_file = Path('.streamlit/secrets.toml')

    if secrets_file.exists():
        st.success("✅ secrets.toml found")
        try:
            # Check if secrets are accessible
            test_val = st.secrets.get('connections', {})
            if test_val:
                st.success("✅ Secrets loaded successfully")
            else:
                st.warning("⚠️ Secrets file exists but no data found")
        except Exception as e:
            st.error(f"❌ Error accessing secrets: {e}")
    else:
        st.warning("⚠️ secrets.toml not found")

st.divider()

# Show current configuration values
st.header("⚙️ Current Configuration")

try:
    debug_config = config.debug_config()

    # Application settings
    st.subheader("🎯 Application Settings")
    app_cols = st.columns(2)

    with app_cols[0]:
        st.info(f"**App Name:** {debug_config.get('APP_NAME', 'Not set')}")
        st.info(f"**Environment:** {debug_config.get('APP_ENV', 'Not set')}")
        st.info(f"**Session Timeout:** {debug_config.get('SESSION_TIMEOUT_MINUTES', 'Not set')} minutes")

    with app_cols[1]:
        st.info(f"**Admin Email:** {debug_config.get('ADMIN_EMAIL', 'Not set')}")
        st.info(f"**Deployment Mode:** {debug_config.get('_deployment_mode', 'Unknown')}")
        st.info(f"**Has .env File:** {debug_config.get('_has_env_file', 'Unknown')}")

    # Integration settings
    st.subheader("🔗 Integrations")
    webhook_url = debug_config.get('DEFAULT_WEBHOOK_URL', 'Not set')
    if webhook_url != 'Not set':
        st.success(f"✅ **Webhook URL:** {webhook_url}")
    else:
        st.error("❌ **Webhook URL:** Not configured")

    # Database connection test
    st.subheader("🗄️ Database Connection")

    with st.spinner("Testing database connection..."):
        try:
            supabase_config = config.get_supabase_config()
            if supabase_config['url'] and supabase_config['key']:
                st.success("✅ Supabase credentials found")

                # Test actual connection
                auth_manager = st.session_state.get('auth_manager')
                if auth_manager and auth_manager.check_database_connection():
                    st.success("✅ Database connection successful")
                else:
                    st.error("❌ Database connection failed")
            else:
                st.error("❌ Supabase credentials missing")
        except Exception as e:
            st.error(f"❌ Database test failed: {e}")

except Exception as e:
    st.error(f"❌ Error loading configuration: {e}")
    st.code(str(e))

st.divider()

# Troubleshooting tips
st.header("🔍 Troubleshooting Tips")

st.markdown("""
### Configuration Priority Order:
1. **Environment Variables** (highest priority) - Docker deployment
2. **Streamlit Secrets** (.streamlit/secrets.toml) - Local development
3. **Default Values** (lowest priority) - Fallback values

### Common Issues:

**🐳 Docker Deployment:**
- Environment variables should be set in your deployment platform
- Digital Ocean App Platform: Set via app spec or dashboard
- Docker Compose: Set in docker-compose.yml or .env file

**💻 Local Development:**
- Use .env file or .streamlit/secrets.toml
- Make sure .env file is in the same directory as your app
- Secrets.toml should be in .streamlit/ directory

**🔧 Production Issues:**
- Check that all required environment variables are set
- Verify Supabase credentials are correct
- Test webhook URL is accessible
- Ensure admin email matches your Supabase user table
""")

# Configuration refresh
if st.button("🔄 Refresh Configuration", help="Reload configuration from all sources"):
    # Clear any cached configuration
    if hasattr(st.session_state, 'auth_manager'):
        del st.session_state.auth_manager
    st.rerun()