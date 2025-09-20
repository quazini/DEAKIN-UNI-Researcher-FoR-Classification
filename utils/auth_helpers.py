"""
Authentication helper utilities for Supabase integration
"""

import streamlit as st
from supabase import create_client, Client
from supabase.client import ClientOptions
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from .config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize password hasher
ph = PasswordHasher()

class AuthenticationManager:
    """Manages authentication with Supabase"""

    def __init__(self):
        """Initialize Supabase client from configuration"""
        try:
            # Use ConfigManager for multi-source configuration
            config_manager = get_config()
            supabase_config = config_manager.get_supabase_config()

            self.supabase_url = supabase_config['url']
            self.supabase_key = supabase_config['key']

            # Use official initialization pattern with client options
            options = ClientOptions(
                postgrest_client_timeout=30,
                storage_client_timeout=30,
                schema="public"
            )

            self.client: Client = create_client(
                self.supabase_url,
                self.supabase_key,
                options=options
            )

            self.admin_email = st.secrets.get("admin", {}).get("ADMIN_EMAIL", "")

        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2"""
        return ph.hash(password)

    def verify_password(self, hashed_password: str, plain_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            ph.verify(hashed_password, plain_password)
            return True
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password

        Returns:
            User data dict if authentication successful, None otherwise
        """
        try:
            # Query user from database
            response = self.client.table('users').select('*').eq('email', email).execute()

            if response.data and len(response.data) > 0:
                user = response.data[0]  # Get first user from list

                # Check if user is active
                if not user.get('is_active', False):
                    st.error("Your account has been deactivated. Please contact the administrator.")
                    return None

                # Verify password
                if self.verify_password(user['password'], password):
                    # Update last login
                    self.client.table('users').update({
                        'last_login': datetime.now().isoformat()
                    }).eq('email', email).execute()

                    return user
                else:
                    st.error("Invalid email or password")
                    return None
            else:
                st.error("Invalid email or password")
                return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            st.error("Authentication failed. Please try again.")
            return None

    def create_user(self, email: str, password: str, name: str, role: str = 'user',
                   created_by: str = None) -> bool:
        """
        Create a new user (admin only)

        Returns:
            True if user created successfully, False otherwise
        """
        try:
            # Hash the password
            hashed_password = self.hash_password(password)

            # Insert user into database
            response = self.client.table('users').insert({
                'email': email,
                'password': hashed_password,
                'name': name,
                'role': role,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'created_by': created_by
            }).execute()

            if response.data:
                logger.info(f"User {email} created successfully by {created_by}")
                return True
            return False

        except Exception as e:
            if "duplicate key" in str(e).lower():
                st.error(f"User with email {email} already exists")
            else:
                logger.error(f"Failed to create user: {e}")
                st.error("Failed to create user. Please try again.")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users (admin only)

        Returns:
            List of user dictionaries
        """
        try:
            response = self.client.table('users').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            return []

    def update_user_status(self, email: str, is_active: bool) -> bool:
        """
        Activate or deactivate a user (admin only)

        Returns:
            True if status updated successfully, False otherwise
        """
        try:
            response = self.client.table('users').update({
                'is_active': is_active
            }).eq('email', email).execute()

            if response.data:
                status = "activated" if is_active else "deactivated"
                logger.info(f"User {email} {status}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update user status: {e}")
            return False

    def reset_user_password(self, email: str, new_password: str) -> bool:
        """
        Reset a user's password (admin only)

        Returns:
            True if password reset successfully, False otherwise
        """
        try:
            # Hash the new password
            hashed_password = self.hash_password(new_password)

            # Update password in database
            response = self.client.table('users').update({
                'password': hashed_password,
                'password_reset_at': datetime.now().isoformat()
            }).eq('email', email).execute()

            if response.data:
                logger.info(f"Password reset for user {email}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to reset password: {e}")
            return False

    def is_admin(self, email: str) -> bool:
        """
        Check if a user is an admin

        Returns:
            True if user is admin, False otherwise
        """
        try:
            response = self.client.table('users').select('role').eq('email', email).execute()

            if response.data and len(response.data) > 0:
                return response.data[0].get('role') == 'admin'
            return False

        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False

    def check_database_connection(self) -> bool:
        """
        Check if database connection is working

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try a simple query
            response = self.client.table('users').select('count', count='exact').execute()
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def init_admin_user(self) -> bool:
        """
        Initialize the admin user if it doesn't exist
        This should only be run once during initial setup

        Returns:
            True if admin user exists or created, False otherwise
        """
        try:
            # Check if admin exists
            response = self.client.table('users').select('email').eq('email', self.admin_email).execute()

            if response.data and len(response.data) > 0:
                return True  # Admin already exists

            # Create admin user with temporary password
            temp_password = "ChangeMe123!"  # You should change this immediately

            return self.create_user(
                email=self.admin_email,
                password=temp_password,
                name="Administrator",
                role="admin",
                created_by="system"
            )

        except Exception as e:
            logger.error(f"Failed to initialize admin user: {e}")
            return False


def check_authentication():
    """
    Check if user is authenticated in the current session

    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def require_authentication():
    """
    Decorator to require authentication for a page
    Redirects to login if not authenticated
    """
    if not check_authentication():
        st.error("🔒 Please login to access this page")
        st.stop()


def require_admin():
    """
    Decorator to require admin role for a page
    Shows error if user is not an admin
    """
    require_authentication()

    if st.session_state.get('user_role') != 'admin':
        st.error("🚫 Access denied. Admin privileges required.")
        st.stop()


def logout():
    """
    Clear session state and logout user
    """
    keys_to_clear = ['authenticated', 'user_email', 'user_name', 'user_role', 'user_id']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Clear message history as well
    if 'messages' in st.session_state:
        st.session_state.messages = []

    st.success("👋 You have been logged out successfully")
    st.rerun()