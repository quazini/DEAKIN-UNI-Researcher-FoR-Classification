"""
Flexible authentication that handles both plain text and hashed passwords
This solves the hash truncation issue by allowing plain text passwords initially
"""

import streamlit as st
import requests
import json
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

class FlexibleAuthManager:
    """Authentication manager that handles both plain text and hashed passwords"""

    def __init__(self):
        """Initialize with flexible configuration"""
        try:
            config = get_config()
            supabase_config = config.get_supabase_config()
            app_config = config.get_app_config()

            self.supabase_url = supabase_config['url']
            self.supabase_key = supabase_config['key']
            self.admin_email = app_config['admin_email']

            # Construct API endpoint
            self.api_url = f"{self.supabase_url}/rest/v1"
            self.headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }

            logger.info("Flexible Auth Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize auth manager: {e}")
            raise

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2"""
        return ph.hash(password)

    def verify_password(self, stored_password: str, input_password: str) -> bool:
        """Verify password - handles both plain text and hashed passwords"""
        try:
            # First, check if stored password is already hashed (starts with $argon2)
            if stored_password.startswith('$argon2'):
                # It's already hashed, use normal verification
                ph.verify(stored_password, input_password)
                return True
            else:
                # It's plain text, compare directly
                return stored_password == input_password
        except (VerifyMismatchError, VerificationError, InvalidHash):
            # Hash verification failed, try plain text comparison
            return stored_password == input_password

    def upgrade_password_to_hash(self, email: str, plain_password: str) -> bool:
        """Upgrade a plain text password to hashed password"""
        try:
            hashed_password = self.hash_password(plain_password)

            url = f"{self.api_url}/users"
            data = {
                "password": hashed_password,
                "password_reset_at": datetime.now().isoformat()
            }
            params = {"email": f"eq.{email}"}

            response = requests.patch(url, headers=self.headers, params=params, json=data, timeout=10)

            if response.status_code in [200, 204]:
                logger.info(f"Password upgraded to hash for user {email}")
                return True
            else:
                logger.warning(f"Failed to upgrade password for {email}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error upgrading password: {e}")
            return False

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with flexible password handling"""
        try:
            # Query user from database
            url = f"{self.api_url}/users"
            params = {"email": f"eq.{email}"}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            users = response.json()

            if users and len(users) > 0:
                user = users[0]

                # Check if user is active
                if not user.get('is_active', False):
                    st.error("Your account has been deactivated. Please contact the administrator.")
                    return None

                stored_password = user.get('password')

                # Verify password (handles both plain text and hashed)
                if self.verify_password(stored_password, password):

                    # If stored password is plain text, upgrade it to hash
                    if not stored_password.startswith('$argon2'):
                        logger.info(f"Upgrading plain text password to hash for {email}")
                        self.upgrade_password_to_hash(email, password)

                    # Update last login
                    self._update_last_login(email)
                    return user
                else:
                    st.error("Invalid email or password")
                    return None
            else:
                st.error("Invalid email or password")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            st.error("Failed to connect to authentication service")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            st.error("Authentication failed. Please try again.")
            return None

    def _update_last_login(self, email: str):
        """Update user's last login timestamp"""
        try:
            url = f"{self.api_url}/users"
            data = {"last_login": datetime.now().isoformat()}
            params = {"email": f"eq.{email}"}

            response = requests.patch(url, headers=self.headers, params=params, json=data, timeout=10)
            response.raise_for_status()

        except Exception as e:
            logger.warning(f"Failed to update last login: {e}")

    def create_user(self, email: str, password: str, name: str, role: str = 'user',
                   created_by: str = None) -> bool:
        """Create a new user"""
        try:
            # Hash the password
            hashed_password = self.hash_password(password)

            # Prepare user data
            user_data = {
                'email': email,
                'password': hashed_password,
                'name': name,
                'role': role,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'created_by': created_by
            }

            # Insert user into database
            url = f"{self.api_url}/users"
            response = requests.post(url, headers=self.headers, json=user_data, timeout=10)

            if response.status_code == 201:
                logger.info(f"User {email} created successfully by {created_by}")
                return True
            else:
                logger.error(f"Failed to create user: {response.status_code} - {response.text}")
                if "duplicate key" in response.text.lower():
                    st.error(f"User with email {email} already exists")
                else:
                    st.error("Failed to create user. Please try again.")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            st.error("Failed to connect to database")
            return False
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            st.error("Failed to create user. Please try again.")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            url = f"{self.api_url}/users"
            params = {"order": "created_at.desc"}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            return []

    def update_user_status(self, email: str, is_active: bool) -> bool:
        """Activate or deactivate a user"""
        try:
            url = f"{self.api_url}/users"
            data = {"is_active": is_active}
            params = {"email": f"eq.{email}"}

            response = requests.patch(url, headers=self.headers, params=params, json=data, timeout=10)
            response.raise_for_status()

            status = "activated" if is_active else "deactivated"
            logger.info(f"User {email} {status}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to update user status: {e}")
            return False

    def reset_user_password(self, email: str, new_password: str) -> bool:
        """Reset a user's password"""
        try:
            # Hash the new password
            hashed_password = self.hash_password(new_password)

            # Update password in database
            url = f"{self.api_url}/users"
            data = {
                "password": hashed_password,
                "password_reset_at": datetime.now().isoformat()
            }
            params = {"email": f"eq.{email}"}

            response = requests.patch(url, headers=self.headers, params=params, json=data, timeout=10)
            response.raise_for_status()

            logger.info(f"Password reset for user {email}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to reset password: {e}")
            return False

    def is_admin(self, email: str) -> bool:
        """Check if a user is an admin"""
        try:
            url = f"{self.api_url}/users"
            params = {"email": f"eq.{email}", "select": "role"}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            users = response.json()
            if users and len(users) > 0:
                return users[0].get('role') == 'admin'
            return False

        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False

    def check_database_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            url = f"{self.api_url}/users"
            params = {"select": "count", "limit": "1"}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            return True

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def init_admin_user(self) -> bool:
        """Initialize the admin user if it doesn't exist"""
        try:
            # Check if admin exists
            url = f"{self.api_url}/users"
            params = {"email": f"eq.{self.admin_email}"}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            users = response.json()
            if users and len(users) > 0:
                return True  # Admin already exists

            # Create admin user with temporary password
            temp_password = "ChangeMe123!"

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


# Authentication helper functions (same interface as before)
def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def require_authentication():
    """Require authentication for a page"""
    if not check_authentication():
        st.error("🔒 Please login to access this page")
        st.stop()

def require_admin():
    """Require admin role for a page"""
    require_authentication()
    if st.session_state.get('user_role') != 'admin':
        st.error("🚫 Access denied. Admin privileges required.")
        st.stop()

def logout():
    """Clear session state and logout user"""
    keys_to_clear = ['authenticated', 'user_email', 'user_name', 'user_role', 'user_id']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    if 'messages' in st.session_state:
        st.session_state.messages = []

    st.success("👋 You have been logged out successfully")
    st.rerun()