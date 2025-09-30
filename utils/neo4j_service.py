"""
Neo4j service for researcher lookup functionality
"""

import streamlit as st
import logging
from typing import List, Dict, Optional, Tuple
from neo4j import GraphDatabase
from utils.config import get_config

# Configure logging
logger = logging.getLogger(__name__)

class Neo4jService:
    """Service for interacting with Neo4j database to fetch researcher data"""

    def __init__(self):
        self.driver = None
        self.config = get_config()
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize Neo4j connection"""
        try:
            neo4j_config = self.config.get_neo4j_config()
            logger.info(f"Neo4j config loaded: URI={neo4j_config.get('uri', 'NOT_FOUND')[:30]}...")

            self.driver = GraphDatabase.driver(
                neo4j_config['uri'],
                auth=(neo4j_config['user'], neo4j_config['password'])
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            # Add more debugging info
            try:
                neo4j_config = self.config.get_neo4j_config()
                logger.error(f"Config debug - URI exists: {'uri' in neo4j_config}")
            except Exception as config_error:
                logger.error(f"Config loading error: {str(config_error)}")
            self.driver = None

    def is_connected(self) -> bool:
        """Check if Neo4j connection is available"""
        return self.driver is not None

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

    @st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
    def get_researchers(_self) -> List[Dict[str, str]]:
        """
        Fetch all researchers from Neo4j EnrichedResearcher nodes

        Returns:
            List of dictionaries containing researcher names and contact record IDs
        """
        if not _self.is_connected():
            logger.warning("Neo4j not connected, returning empty list")
            return []

        try:
            query = """
            MATCH (r:EnrichedResearcher)
            WHERE r.full_name IS NOT NULL AND r.full_name <> ""
            RETURN r.full_name as name, r.contact_record_id as contactRecordId
            ORDER BY r.full_name
            """

            with _self.driver.session(database=_self.config.get_neo4j_config()['database']) as session:
                result = session.run(query)
                researchers = []

                for record in result:
                    name = record.get('name')
                    contact_id = record.get('contactRecordId')

                    if name and name.strip():  # Only include researchers with valid names
                        researchers.append({
                            'name': name.strip(),
                            'contactRecordId': contact_id or 'Unknown'
                        })

                logger.info(f"Retrieved {len(researchers)} researchers from Neo4j")
                return researchers

        except Exception as e:
            logger.error(f"Error fetching researchers from Neo4j: {str(e)}")
            return []

    @st.cache_data(ttl=60)  # Cache for 1 minute
    def search_researchers(_self, search_term: str) -> List[Dict[str, str]]:
        """
        Search for researchers by name using fuzzy matching

        Args:
            search_term: The search term to match against researcher names

        Returns:
            List of matching researchers
        """
        if not _self.is_connected() or not search_term:
            return []

        try:
            # Use CONTAINS for fuzzy matching
            query = """
            MATCH (r:EnrichedResearcher)
            WHERE toLower(r.full_name) CONTAINS toLower($search_term)
            RETURN r.full_name as name, r.contact_record_id as contactRecordId
            ORDER BY r.full_name
            LIMIT 20
            """

            with _self.driver.session() as session:
                result = session.run(query, search_term=search_term)
                researchers = []

                for record in result:
                    name = record.get('name')
                    contact_id = record.get('contactRecordId')

                    if name:
                        researchers.append({
                            'name': name,
                            'contactRecordId': contact_id or 'Unknown'
                        })

                return researchers

        except Exception as e:
            logger.error(f"Error searching researchers in Neo4j: {str(e)}")
            return []

    def get_connection_status(self) -> Dict[str, str]:
        """
        Get detailed connection status for debugging

        Returns:
            Dictionary with connection status information
        """
        if not self.is_connected():
            return {
                'status': 'disconnected',
                'message': 'Not connected to Neo4j',
                'details': 'Check environment variables: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD'
            }

        try:
            # Test query to verify database access
            config = self.config.get_neo4j_config()
            with self.driver.session(database=config['database']) as session:
                result = session.run("MATCH (r:EnrichedResearcher) RETURN count(r) as total")
                total_researchers = result.single()['total']

                return {
                    'status': 'connected',
                    'message': f'Connected successfully',
                    'details': f'Found {total_researchers} researchers in database'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Connected but query failed',
                'details': str(e)
            }


# Global instance
_neo4j_service = None

def get_neo4j_service() -> Neo4jService:
    """Get or create the global Neo4j service instance"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service

def clear_researcher_cache():
    """Clear the researcher cache"""
    try:
        get_neo4j_service().get_researchers.clear()
        get_neo4j_service().search_researchers.clear()
    except:
        pass  # Ignore errors if cache doesn't exist