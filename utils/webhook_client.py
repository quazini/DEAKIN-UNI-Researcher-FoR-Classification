"""
Webhook client utilities for n8n FoR Classification workflow
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookClient:
    """Client for interacting with n8n FoR Classification webhook"""

    def __init__(self, webhook_url: str, timeout: int = 60):
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send_message(self, message: str, session_id: str) -> Optional[Dict[Any, Any]]:
        """
        Send message to n8n webhook and return parsed response

        Args:
            message: User input message (e.g., "Who is Colin Barrow?")
            session_id: Unique session identifier

        Returns:
            Parsed JSON response or None if error occurred
        """
        payload = {
            "chatInput": message,
            "sessionId": session_id
        }

        try:
            logger.info(f"Sending request to webhook: {message[:50]}...")

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )

            response.raise_for_status()
            result = response.json()

            logger.info("Successfully received response from webhook")
            # Normalize response format for display components
            normalized_response = self.normalize_response_format(result)
            return normalized_response

        except requests.exceptions.Timeout:
            logger.error("Request timeout - classification taking longer than expected")
            raise TimeoutError("Classification request timed out")

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to webhook URL: {self.webhook_url}")
            raise ConnectionError("Failed to connect to classification service")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP error: {status_code}")

            if status_code == 404:
                raise ValueError("Webhook not found (404). Please check:\n• Is the webhook URL correct?\n• Is the n8n workflow activated?\n• Is the webhook node properly configured?")
            elif status_code == 405:
                raise ValueError("Method not allowed (405). The webhook may not accept POST requests.")
            elif status_code == 500:
                raise ValueError("Server error (500). There may be an issue with the n8n workflow.")
            elif status_code == 403:
                raise ValueError("Access forbidden (403). Check webhook permissions and authentication.")
            else:
                raise ValueError(f"Server error: {status_code}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON response from webhook")
            raise ValueError("Invalid response format from classification service")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise RuntimeError(f"Unexpected error: {str(e)}")

    def validate_response(self, response: Dict[Any, Any]) -> bool:
        """
        Validate that the response contains expected FoR classification data

        Args:
            response: Parsed JSON response from webhook

        Returns:
            True if response is valid, False otherwise
        """
        # Handle array response from n8n
        if isinstance(response, list) and len(response) > 0:
            response = response[0]

        if not isinstance(response, dict):
            return False

        # Check for new response format (direct fields)
        has_direct_classifications = bool(response.get('primary_classifications'))

        # Check for old response format (nested under llm_classification)
        llm_classification = response.get('llm_classification', {})
        has_nested_classifications = bool(llm_classification.get('primary_classifications'))

        # Check for researcher data
        has_researcher_data = bool(response.get('researcher_name'))

        return has_direct_classifications or has_nested_classifications or has_researcher_data

    def extract_error_message(self, response: Dict[Any, Any]) -> Optional[str]:
        """
        Extract error message from webhook response if present

        Args:
            response: Parsed JSON response from webhook

        Returns:
            Error message string or None if no error
        """
        # Check for various error fields that might be present
        error_fields = ['error', 'error_message', 'validation_error', 'termination_reason']

        for field in error_fields:
            if field in response and response[field]:
                return str(response[field])

        # Check for validation failures
        validation_guardrail = response.get('validation_guardrail', {})
        if validation_guardrail.get('validation_status') == 'not_found':
            return "Researcher not found in the classification system"

        return None

    def normalize_response_format(self, response: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Normalize n8n response format to match display component expectations

        Args:
            response: Raw response from n8n webhook

        Returns:
            Normalized response format
        """
        # Handle array response from n8n
        if isinstance(response, list) and len(response) > 0:
            response = response[0]

        if not isinstance(response, dict):
            return response

        # If already in nested format, return as-is
        if 'llm_classification' in response:
            return response

        # Convert new flat format to nested format expected by components
        normalized = {
            'llm_classification': {
                'primary_classifications': [],
                'secondary_classifications': [],
                'evidence_based_biography': response.get('enriched_biography', ''),
                'enriched_biography': response.get('enriched_biography', ''),
                'classification_rationale': response.get('llm_rationale', ''),
                'confidence_level': response.get('llm_confidence_level', 'medium'),
                'query_response': f"Classification completed for researcher with {response.get('classification_confidence', 'medium')} confidence."
            },
            'researcher_name': self.extract_researcher_name_from_response(response),
            'classification_timestamp': response.get('classification_timestamp', ''),
            'classification_confidence': response.get('classification_confidence', 'medium'),
            'institutional_context': {
                'organization': 'Deakin University',  # Default based on biography
                'position': 'Professor',
                'department': 'School of Life and Environmental Sciences',
                'email': 'Not available'
            },
            'institutional_data_complete': True,
            'data_sources_used': ['n8n_workflow'],
            'search_quality': {
                'fuzzy_match_used': False,
                'confidence_score': 1.0,
                'match_type': 'exact_match'
            }
        }

        # Convert primary classifications
        primary_classifications = response.get('primary_classifications', [])
        for classification in primary_classifications:
            normalized_classification = {
                'field_number': classification.get('field_number', ''),
                'field_name': classification.get('field_name', ''),
                'confidence': classification.get('llm_confidence', 'medium'),
                'reasoning': classification.get('llm_reasoning', ''),
                'evidence_keywords': classification.get('evidence_keywords', []),
                # Preserve additional n8n fields
                'rank': classification.get('rank', 0),
                'group_name': classification.get('group_name', ''),
                'group_number': classification.get('group_number', ''),
                'division_name': classification.get('division_name', ''),
                'division_number': classification.get('division_number', ''),
                'field_semantic_score': classification.get('field_semantic_score'),
                'field_combined_score': classification.get('field_combined_score'),
                'hierarchy_validated': classification.get('hierarchy_validated', False),
                'classification_source': classification.get('classification_source', ''),
                'classification_method': classification.get('classification_method', '')
            }
            normalized['llm_classification']['primary_classifications'].append(normalized_classification)

        # Convert secondary classifications
        secondary_classifications = response.get('secondary_classifications', [])
        for classification in secondary_classifications:
            normalized_classification = {
                'field_number': classification.get('field_number', ''),
                'field_name': classification.get('field_name', ''),
                'confidence': classification.get('llm_confidence', 'medium'),
                'reasoning': classification.get('llm_reasoning', ''),
                'evidence_keywords': classification.get('evidence_keywords', []),
                # Preserve additional n8n fields
                'rank': classification.get('rank', 0),
                'group_name': classification.get('group_name', ''),
                'group_number': classification.get('group_number', ''),
                'division_name': classification.get('division_name', ''),
                'division_number': classification.get('division_number', ''),
                'field_semantic_score': classification.get('field_semantic_score'),
                'field_combined_score': classification.get('field_combined_score'),
                'hierarchy_validated': classification.get('hierarchy_validated', False),
                'classification_source': classification.get('classification_source', ''),
                'classification_method': classification.get('classification_method', '')
            }
            normalized['llm_classification']['secondary_classifications'].append(normalized_classification)

        # Add additional response metadata
        normalized.update({
            'classification_method': response.get('classification_method', ''),
            'filtering_efficiency': response.get('filtering_efficiency', ''),
            'status': response.get('status', ''),
            'primary_research_areas': response.get('primary_research_areas', []),
            'secondary_research_areas': response.get('secondary_research_areas', [])
        })

        return normalized

    def extract_researcher_name_from_response(self, response: Dict[Any, Any]) -> str:
        """Extract researcher name from biography or other fields"""
        biography = response.get('enriched_biography', '')

        # Try to extract name from biography (looks for "Professor [Name]")
        import re
        name_match = re.search(r'Professor\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', biography)
        if name_match:
            return name_match.group(1)

        # Fallback
        return "Researcher"