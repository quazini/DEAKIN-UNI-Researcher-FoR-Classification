"""
Admin-specific authentication that uses service role key for user management
This bypasses RLS while keeping regular operations secure
"""

import streamlit as st
import requests
import json
from argon2 import PasswordHasher
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from .config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize password hasher
ph = PasswordHasher()

class AdminAuthManager:
    """Admin authentication manager that uses service role for privileged operations"""

    def __init__(self):
        """Initialize with service role key from SUPABASE_KEY"""
        try:
            # Use ConfigManager for multi-source configuration
            config_manager = get_config()
            supabase_config = config_manager.get_supabase_config()
            app_config = config_manager.get_app_config()

            self.supabase_url = supabase_config['url']
            # Since you replaced SUPABASE_KEY with service role key, we use it directly
            self.service_key = supabase_config['key']
            self.admin_email = app_config['admin_email']

            # API setup
            self.api_url = f"{self.supabase_url}/rest/v1"

            # Use service role key for all operations (bypasses RLS)
            self.headers = {
                "apikey": self.service_key,
                "Authorization": f"Bearer {self.service_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }

            # For compatibility, set both to same headers
            self.anon_headers = self.headers
            self.admin_headers = self.headers

            logger.info("Admin Auth Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize admin auth manager: {e}")
            raise

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2"""
        return ph.hash(password)

    def create_user(self, email: str, password: str, name: str, role: str = 'user',
                   created_by: str = None) -> tuple[bool, str]:
        """Create a new user using admin privileges (bypasses RLS)"""
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

            # Use admin headers to bypass RLS
            url = f"{self.api_url}/users"
            response = requests.post(url, headers=self.admin_headers, json=user_data, timeout=10)

            if response.status_code == 201:
                logger.info(f"User {email} created successfully by {created_by}")
                return True, "User created successfully!"

            elif response.status_code == 409:
                return False, f"User with email {email} already exists"

            elif response.status_code == 401:
                return False, "Permission denied. Service role key may be missing or incorrect."

            else:
                logger.error(f"Failed to create user: {response.status_code} - {response.text}")
                return False, f"Failed to create user: {response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return False, "Failed to connect to database"
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False, f"Unexpected error: {str(e)}"

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (can use anon key for reading)"""
        try:
            url = f"{self.api_url}/users"
            params = {"order": "created_at.desc"}

            response = requests.get(url, headers=self.anon_headers, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            return []

    def update_user_status(self, email: str, is_active: bool) -> tuple[bool, str]:
        """Activate or deactivate a user (admin operation)"""
        try:
            url = f"{self.api_url}/users"
            data = {"is_active": is_active}
            params = {"email": f"eq.{email}"}

            # Use admin headers for privileged operation
            response = requests.patch(url, headers=self.admin_headers, params=params, json=data, timeout=10)

            if response.status_code in [200, 204]:
                status = "activated" if is_active else "deactivated"
                logger.info(f"User {email} {status}")
                return True, f"User {status} successfully"
            else:
                return False, f"Failed to update user status: {response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return False, "Failed to connect to database"
        except Exception as e:
            logger.error(f"Failed to update user status: {e}")
            return False, f"Unexpected error: {str(e)}"

    def reset_user_password(self, email: str, new_password: str) -> tuple[bool, str]:
        """Reset a user's password (admin operation)"""
        try:
            # Hash the new password
            hashed_password = self.hash_password(new_password)

            url = f"{self.api_url}/users"
            data = {
                "password": hashed_password,
                "password_reset_at": datetime.now().isoformat()
            }
            params = {"email": f"eq.{email}"}

            # Use admin headers for privileged operation
            response = requests.patch(url, headers=self.admin_headers, params=params, json=data, timeout=10)

            if response.status_code in [200, 204]:
                logger.info(f"Password reset for user {email}")
                return True, "Password reset successfully"
            else:
                return False, f"Failed to reset password: {response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return False, "Failed to connect to database"
        except Exception as e:
            logger.error(f"Failed to reset password: {e}")
            return False, f"Unexpected error: {str(e)}"

    def delete_user(self, email: str) -> tuple[bool, str]:
        """Delete a user (admin operation)"""
        try:
            url = f"{self.api_url}/users"
            params = {"email": f"eq.{email}"}

            # Use admin headers for privileged operation
            response = requests.delete(url, headers=self.admin_headers, params=params, timeout=10)

            if response.status_code in [200, 204]:
                logger.info(f"User {email} deleted")
                return True, "User deleted successfully"
            else:
                return False, f"Failed to delete user: {response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return False, "Failed to connect to database"
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False, f"Unexpected error: {str(e)}"

    def check_service_role_key(self) -> tuple[bool, str]:
        """Check if service role key is properly configured"""
        # Check if the key looks like a service role key (contains "service_role" in the JWT)
        try:
            import base64
            import json

            # Decode JWT payload (middle part)
            parts = self.service_key.split('.')
            if len(parts) >= 2:
                # Add padding if needed
                payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
                decoded = base64.b64decode(payload)
                jwt_data = json.loads(decoded)

                if jwt_data.get('role') == 'service_role':
                    return True, "Service role key detected and configured correctly"
                else:
                    return False, f"Using {jwt_data.get('role', 'unknown')} key - may have limited permissions"
        except:
            pass

        # Fallback: Test by trying to query
        try:
            url = f"{self.api_url}/users"
            params = {"select": "count", "limit": "1"}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                return True, "Key is working correctly"
            else:
                return False, f"Key test failed: {response.status_code}"

        except Exception as e:
            return False, f"Key test error: {str(e)}"

    def get_setup_instructions(self) -> str:
        """Get instructions for setting up service role key"""
        return """
🔧 Service Role Key Setup:

1. Go to your Supabase Dashboard
2. Navigate to Settings → API
3. Copy the 'service_role' key (NOT the anon key)
4. Add it to your .streamlit/secrets.toml:

[connections.supabase]
SUPABASE_URL = "your-url"
SUPABASE_KEY = "your-anon-key"
SERVICE_ROLE_KEY = "your-service-role-key"

5. Restart the Streamlit app

⚠️ Keep service role key secure - it has full database access!
        """

    def check_database_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            response = requests.get(
                f"{self.api_url}/users?select=email&limit=1",
                headers=self.headers,
                timeout=5
            )
            return response.status_code in [200, 206]
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False