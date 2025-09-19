"""
Admin Panel for User Management
Only accessible to users with admin role
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.flexible_auth import require_admin, logout
from utils.admin_auth import AdminAuthManager
import random
import string

# Configure page
st.set_page_config(
    page_title="Admin Panel - FoR Classification",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check admin access
require_admin()

# Initialize admin authentication manager
auth_manager = AdminAuthManager()

# Custom CSS for admin panel
st.markdown("""
<style>
    /* Admin header styling */
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }

    .admin-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
    }

    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Button styling */
    .action-button {
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_temp_password(length=12):
    """Generate a secure temporary password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

# Header
st.markdown("""
<div class="admin-header">
    <h1 class="admin-title">👑 Admin Panel</h1>
    <p>User Management & System Administration</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.header("🧭 Navigation")

    if st.button("🏠 Back to Main App", use_container_width=True):
        st.switch_page("pages/main_app.py")

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("login.py")

    st.divider()

    # Admin info
    st.header("👤 Admin Info")
    st.text(f"Logged in as: {st.session_state.get('user_name', 'Admin')}")
    st.text(f"Email: {st.session_state.get('user_email', '')}")

# Main content - Tabs for different admin functions
tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "➕ Create User", "📊 Statistics", "⚙️ Settings"])

with tab1:
    st.header("👥 User Management")

    # Fetch all users
    users = auth_manager.get_all_users()

    if users:
        # Convert to DataFrame for better display
        df = pd.DataFrame(users)

        # Select columns to display
        display_columns = ['name', 'email', 'role', 'is_active', 'created_at', 'last_login']
        available_columns = [col for col in display_columns if col in df.columns]

        # Display user table
        st.subheader(f"Total Users: {len(users)}")

        # Create columns for filters
        col1, col2, col3 = st.columns(3)

        with col1:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user"])

        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])

        with col3:
            search = st.text_input("Search by name or email")

        # Apply filters
        filtered_df = df.copy()

        if role_filter != "All":
            filtered_df = filtered_df[filtered_df['role'] == role_filter]

        if status_filter == "Active":
            filtered_df = filtered_df[filtered_df['is_active'] == True]
        elif status_filter == "Inactive":
            filtered_df = filtered_df[filtered_df['is_active'] == False]

        if search:
            mask = (filtered_df['name'].str.contains(search, case=False, na=False) |
                   filtered_df['email'].str.contains(search, case=False, na=False))
            filtered_df = filtered_df[mask]

        # Display filtered users
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # User actions
        st.subheader("🔧 User Actions")

        col1, col2 = st.columns(2)

        with col1:
            # Select user for actions
            user_emails = [user['email'] for user in users if user['email'] != st.session_state.get('user_email')]
            selected_user = st.selectbox("Select User", user_emails)

        with col2:
            # Get selected user details
            selected_user_data = next((u for u in users if u['email'] == selected_user), None)

            if selected_user_data:
                st.info(f"Status: {'✅ Active' if selected_user_data['is_active'] else '❌ Inactive'}")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if selected_user_data:
                if selected_user_data['is_active']:
                    if st.button("🚫 Deactivate User", use_container_width=True):
                        success, message = auth_manager.update_user_status(selected_user, False)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    if st.button("✅ Activate User", use_container_width=True):
                        success, message = auth_manager.update_user_status(selected_user, True)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

        with col2:
            if st.button("🔐 Reset Password", use_container_width=True):
                new_password = generate_temp_password()
                success, message = auth_manager.reset_user_password(selected_user, new_password)
                if success:
                    st.success(f"✅ {message}")
                    st.info(f"New temporary password: `{new_password}`")
                    st.warning("Please share this password securely with the user")
                else:
                    st.error(f"❌ {message}")

        with col3:
            if st.button("🗑️ Delete User", use_container_width=True, type="secondary"):
                st.error("User deletion is permanently disabled for safety")

    else:
        st.info("No users found in the database")

with tab2:
    st.header("➕ Create New User")

    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_email = st.text_input("Email Address*", placeholder="user@example.com")
            new_name = st.text_input("Full Name*", placeholder="John Doe")

        with col2:
            new_role = st.selectbox("Role", ["user", "admin"])
            new_password = st.text_input(
                "Temporary Password*",
                value=generate_temp_password(),
                help="Share this password securely with the user"
            )

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            submit = st.form_submit_button("✅ Create User", use_container_width=True, type="primary")

        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        if submit:
            if not new_email or not new_name or not new_password:
                st.error("Please fill in all required fields")
            else:
                # Check service role key status first
                service_ok, service_msg = auth_manager.check_service_role_key()
                if not service_ok:
                    st.warning(f"⚠️ {service_msg}")
                    with st.expander("🔧 Setup Instructions"):
                        st.code(auth_manager.get_setup_instructions())

                success, message = auth_manager.create_user(
                    email=new_email,
                    password=new_password,
                    name=new_name,
                    role=new_role,
                    created_by=st.session_state.get('user_email')
                )

                if success:
                    st.success(f"✅ {message}")
                    st.info(f"User: {new_email}")
                    st.info(f"Temporary password: `{new_password}`")
                    st.warning("Please share this password securely with the user")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")
                    if "permission denied" in message.lower() or "service role" in message.lower():
                        with st.expander("🔧 Fix Permission Issues"):
                            st.code(auth_manager.get_setup_instructions())

with tab3:
    st.header("📊 System Statistics")

    # Get user statistics
    users = auth_manager.get_all_users()

    if users:
        df = pd.DataFrame(users)

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Users", len(users))

        with col2:
            active_users = len(df[df['is_active'] == True])
            st.metric("Active Users", active_users)

        with col3:
            admin_count = len(df[df['role'] == 'admin'])
            st.metric("Administrators", admin_count)

        with col4:
            user_count = len(df[df['role'] == 'user'])
            st.metric("Regular Users", user_count)

        st.divider()

        # User creation timeline
        st.subheader("📈 User Registration Timeline")

        if 'created_at' in df.columns:
            # Handle different datetime formats (with or without microseconds)
            df['created_at'] = pd.to_datetime(df['created_at'], format='mixed')
            df['date'] = df['created_at'].dt.date

            registrations = df.groupby('date').size().reset_index(name='New Users')
            st.line_chart(registrations.set_index('date'))

        # Role distribution
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👥 Role Distribution")
            role_counts = df['role'].value_counts()
            st.bar_chart(role_counts)

        with col2:
            st.subheader("✅ Status Distribution")
            status_counts = df['is_active'].value_counts()
            status_counts.index = ['Active' if x else 'Inactive' for x in status_counts.index]
            st.bar_chart(status_counts)

        # Recent activity
        st.divider()
        st.subheader("🕒 Recent User Activity")

        if 'last_login' in df.columns:
            recent_activity = df[['name', 'email', 'last_login']].copy()
            # Handle different datetime formats
            recent_activity['last_login'] = pd.to_datetime(recent_activity['last_login'], format='mixed', errors='coerce')
            recent_activity = recent_activity.dropna(subset=['last_login'])
            recent_activity = recent_activity.sort_values('last_login', ascending=False).head(10)

            st.dataframe(
                recent_activity,
                use_container_width=True,
                hide_index=True
            )

with tab4:
    st.header("⚙️ System Settings")

    # Database connection status
    st.subheader("🗄️ Database Status")

    col1, col2 = st.columns(2)

    with col1:
        if auth_manager.check_database_connection():
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Connection Failed")

    with col2:
        st.info(f"Supabase URL: {auth_manager.supabase_url.split('.')[0]}...")

    st.divider()

    # Admin initialization
    st.subheader("🔧 Admin Initialization")

    if st.button("Initialize Admin User", help="Creates the default admin user if it doesn't exist"):
        if auth_manager.init_admin_user():
            st.success("Admin user initialized successfully")
            st.info("Default password: ChangeMe123! (Please change immediately)")
        else:
            st.info("Admin user already exists or initialization failed")

    st.divider()

    # Session info
    st.subheader("📋 Current Session")

    session_info = {
        "User": st.session_state.get('user_name', 'Unknown'),
        "Email": st.session_state.get('user_email', 'Unknown'),
        "Role": st.session_state.get('user_role', 'Unknown'),
        "Session ID": st.session_state.get('session_id', 'Unknown')[:8] + "..."
    }

    for key, value in session_info.items():
        st.text(f"{key}: {value}")

# Footer
st.markdown("---")
st.markdown("*Admin Panel - FoR Classification System | Powered by Supabase*")