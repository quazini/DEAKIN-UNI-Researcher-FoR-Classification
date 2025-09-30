"""
Configuration manager that supports multiple sources:
1. Environment variables (Docker deployment)
2. .env files (local development)
3. Streamlit secrets.toml (legacy support)
"""

import os
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if available
except ImportError:
    pass  # dotenv not available, continue without it


class ConfigManager:
    """Unified configuration management for all deployment scenarios"""

    def __init__(self):
        self._load_env_file()

    def _secrets_file_exists(self) -> bool:
        """Check if any Streamlit secrets file exists"""
        secrets_paths = [
            Path('.streamlit/secrets.toml'),
            Path('/home/streamlit/.streamlit/secrets.toml'),
            Path('/app/.streamlit/secrets.toml')
        ]
        return any(path.exists() for path in secrets_paths)

    def _load_env_file(self):
        """Load .env file if it exists"""
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Only set if not already in environment
                            if key.strip() not in os.environ:
                                os.environ[key.strip()] = value.strip()
            except Exception as e:
                st.warning(f"Could not load .env file: {e}")

    def get(self, key: str, default: Optional[str] = None, fallback_path: Optional[str] = None) -> str:
        """
        Get configuration value from multiple sources in order:
        1. Environment variables
        2. Streamlit secrets (with optional path)
        3. Default value
        """
        # Try environment variable first
        value = os.environ.get(key)
        if value:
            return value

        # Try Streamlit secrets with path (only if secrets file exists)
        if fallback_path and self._secrets_file_exists():
            try:
                secrets_value = st.secrets
                for part in fallback_path.split('.'):
                    secrets_value = secrets_value[part]
                return str(secrets_value)
            except (KeyError, AttributeError, FileNotFoundError, Exception):
                pass

        # Try Streamlit secrets direct key (only if secrets file exists)
        if self._secrets_file_exists():
            try:
                return str(st.secrets[key])
            except (KeyError, AttributeError, FileNotFoundError, Exception):
                pass

        if default is not None:
            return default

        raise ValueError(f"Configuration key '{key}' not found in environment, .env file, or Streamlit secrets")

    def get_supabase_config(self) -> Dict[str, str]:
        """Get Supabase configuration"""
        return {
            'url': self.get('SUPABASE_URL', fallback_path='connections.supabase.SUPABASE_URL'),
            'key': self.get('SUPABASE_KEY', fallback_path='connections.supabase.SUPABASE_KEY')
        }

    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return {
            'name': self.get('APP_NAME', default='FoR Classification System'),
            'env': self.get('APP_ENV', default='development'),
            'session_timeout': int(self.get('SESSION_TIMEOUT_MINUTES', default='60')),
            'admin_email': self.get('ADMIN_EMAIL', fallback_path='admin.ADMIN_EMAIL'),
        }

    def get_webhook_url(self) -> str:
        """Get webhook URL"""
        return self.get('DEFAULT_WEBHOOK_URL',
                       default='https://mbcrc.app.n8n.cloud/webhook/530ec5fa-656a-4c9c-bb05-5be7ff3bdef2')

    def get_neo4j_config(self) -> Dict[str, str]:
        """Get Neo4j configuration from environment or secrets"""
        try:
            # Try environment variables first (for production deployment)
            return {
                'uri': self.get('NEO4J_URI'),
                'user': self.get('NEO4J_USERNAME'),
                'password': self.get('NEO4J_PASSWORD'),
                'database': self.get('NEO4J_DATABASE', default='neo4j')
            }
        except ValueError:
            # Fallback to Streamlit secrets (for local development)
            return {
                'uri': st.secrets["neo4j"]["NEO4J_URI"],
                'user': st.secrets["neo4j"]["NEO4J_USERNAME"],
                'password': st.secrets["neo4j"]["NEO4J_PASSWORD"],
                'database': st.secrets["neo4j"]["NEO4J_DATABASE"]
            }

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.get('APP_ENV', default='development').lower() == 'production'

    def debug_config(self) -> Dict[str, str]:
        """Return configuration for debugging (without secrets)"""
        config = {}

        # Safe values to show
        safe_keys = [
            'APP_NAME', 'APP_ENV', 'SESSION_TIMEOUT_MINUTES',
            'DEFAULT_WEBHOOK_URL', 'ADMIN_EMAIL', 'NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_DATABASE'
        ]

        for key in safe_keys:
            try:
                value = self.get(key, default='Not set')
                # Mask sensitive values
                if 'webhook' in key.lower() and value != 'Not set':
                    config[key] = value[:30] + '...' if len(value) > 30 else value
                else:
                    config[key] = value
            except:
                config[key] = 'Not set'

        # Add source indicators
        config['_has_env_file'] = str(Path('.env').exists())
        config['_has_secrets_toml'] = str(Path('.streamlit/secrets.toml').exists())
        config['_deployment_mode'] = 'Docker' if os.environ.get('STREAMLIT_SERVER_HEADLESS') else 'Local'

        return config


# Global instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration manager instance"""
    return config