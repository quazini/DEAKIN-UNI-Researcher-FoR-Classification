"""
Beautiful Login Page for FoR Classification System
"""

import streamlit as st
from utils.flexible_auth import FlexibleAuthManager, check_authentication
import time

# Configure page
st.set_page_config(
    page_title="Login - FoR Classification",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding-top: 2rem;
    }

    /* Login container */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }

    /* Title styling */
    .login-title {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .login-subtitle {
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        border: none;
        padding: 0.75rem;
        font-size: 1rem;
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        background: white;
        color: #667eea;
        border: none;
        padding: 0.75rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    /* Footer styling */
    .login-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 2rem;
        font-size: 0.9rem;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Success/Error message styling */
    .stAlert {
        border-radius: 10px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Check if already authenticated
if check_authentication():
    st.switch_page("pages/main_app.py")

# Initialize authentication manager
try:
    auth_manager = FlexibleAuthManager()
except Exception as e:
    st.error("⚠️ Could not connect to authentication service. Please check your configuration.")
    st.error(f"Error details: {str(e)}")
    st.stop()

# Create login form
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Logo and title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<h1 class="login-title">🔬</h1>', unsafe_allow_html=True)

st.markdown('<h1 class="login-title">FoR Classification</h1>', unsafe_allow_html=True)
st.markdown('<p class="login-subtitle">Researcher Intelligence System</p>', unsafe_allow_html=True)

# Create form
with st.form("login_form", clear_on_submit=True):
    email = st.text_input(
        "Email Address",
        placeholder="Enter your email",
        help="Your registered email address"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        help="Your secure password"
    )

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Submit button
    submit = st.form_submit_button("🔓 Login", use_container_width=True)

    if submit:
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            # Show loading animation
            with st.spinner("🔐 Authenticating..."):
                user = auth_manager.authenticate_user(email, password)

                if user:
                    # Set session state
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = user['email']
                    st.session_state['user_name'] = user.get('name', 'User')
                    st.session_state['user_role'] = user.get('role', 'user')
                    st.session_state['user_id'] = user.get('id')

                    # Show success message
                    st.success(f"✅ Welcome back, {user.get('name', 'User')}!")
                    time.sleep(1)

                    # Redirect to main app
                    st.switch_page("pages/main_app.py")

# Footer
st.markdown("""
<div class="login-footer">
    <p>🔒 Secure Authentication via Supabase</p>
    <p style="margin-top: 0.5rem; font-size: 0.8rem;">
        Access restricted to authorized users only
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Help section
with st.expander("❓ Need Help?"):
    st.markdown("""
    **Login Issues:**
    - Ensure you're using your registered email address
    - Passwords are case-sensitive
    - Contact your administrator if you've forgotten your password

    **New User?**
    - Only administrators can create new accounts
    - Contact your system administrator to request access

    **Technical Support:**
    - If you continue to experience issues, please contact IT support
    """)

# Admin hint (subtle, at the bottom)
if st.button("👑", help="Admin access", key="admin_hint"):
    st.info("Administrators can access the admin panel after logging in with admin credentials")