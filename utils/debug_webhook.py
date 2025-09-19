"""
Debug utilities for webhook testing and troubleshooting
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

def test_webhook_connection(webhook_url: str) -> Dict[str, Any]:
    """
    Test basic connectivity to the webhook endpoint

    Args:
        webhook_url: The n8n webhook URL to test

    Returns:
        Dictionary with test results
    """
    results = {
        "url": webhook_url,
        "connectivity": False,
        "accepts_post": False,
        "responds_to_test": False,
        "error_message": None,
        "status_code": None,
        "response_headers": {},
        "response_content": None
    }

    try:
        # Test 1: Basic connectivity with GET request
        print(f"🔍 Testing basic connectivity to: {webhook_url}")
        get_response = requests.get(webhook_url, timeout=10)
        results["connectivity"] = True
        results["status_code"] = get_response.status_code
        results["response_headers"] = dict(get_response.headers)

        print(f"✅ Basic connectivity: {get_response.status_code}")

        # Test 2: POST request acceptance
        print("🔍 Testing POST request acceptance...")
        test_payload = {
            "chatInput": "test connection",
            "sessionId": "debug-test-session"
        }

        post_response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        results["accepts_post"] = post_response.status_code not in [404, 405, 501]
        results["status_code"] = post_response.status_code
        results["response_content"] = post_response.text[:500]  # First 500 chars

        print(f"✅ POST acceptance: {post_response.status_code}")

        # Test 3: Actual response test
        if post_response.status_code == 200:
            try:
                response_json = post_response.json()
                results["responds_to_test"] = True
                results["response_content"] = json.dumps(response_json, indent=2)[:1000]
                print("✅ Webhook responds with valid JSON")
            except json.JSONDecodeError:
                print("⚠️  Webhook responds but not with valid JSON")

    except requests.exceptions.ConnectionError:
        results["error_message"] = "Connection failed - cannot reach the webhook URL"
        print("❌ Connection failed - cannot reach the webhook URL")

    except requests.exceptions.Timeout:
        results["error_message"] = "Request timed out - webhook may be slow or unresponsive"
        print("❌ Request timed out")

    except Exception as e:
        results["error_message"] = f"Unexpected error: {str(e)}"
        print(f"❌ Unexpected error: {str(e)}")

    return results

def validate_webhook_url(webhook_url: str) -> Dict[str, Any]:
    """
    Validate the format and structure of the webhook URL

    Args:
        webhook_url: The webhook URL to validate

    Returns:
        Dictionary with validation results
    """
    validation = {
        "url": webhook_url,
        "valid_format": False,
        "is_https": False,
        "is_n8n_cloud": False,
        "has_webhook_path": False,
        "has_webhook_id": False,
        "issues": []
    }

    try:
        from urllib.parse import urlparse
        parsed = urlparse(webhook_url)

        # Check basic URL format
        if parsed.scheme and parsed.netloc:
            validation["valid_format"] = True
        else:
            validation["issues"].append("Invalid URL format")

        # Check HTTPS
        if parsed.scheme == "https":
            validation["is_https"] = True
        else:
            validation["issues"].append("Should use HTTPS for security")

        # Check if it's n8n cloud
        if "n8n.cloud" in parsed.netloc:
            validation["is_n8n_cloud"] = True

        # Check webhook path
        if "webhook" in parsed.path:
            validation["has_webhook_path"] = True
        else:
            validation["issues"].append("URL should contain 'webhook' in the path")

        # Check for webhook ID (UUID pattern)
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        if re.search(uuid_pattern, webhook_url):
            validation["has_webhook_id"] = True
        else:
            validation["issues"].append("URL should contain a webhook ID (UUID)")

    except Exception as e:
        validation["issues"].append(f"Error parsing URL: {str(e)}")

    return validation

def suggest_webhook_fixes(webhook_url: str) -> list:
    """
    Suggest potential fixes for common webhook issues

    Args:
        webhook_url: The problematic webhook URL

    Returns:
        List of suggested fixes
    """
    suggestions = []
    validation = validate_webhook_url(webhook_url)

    if not validation["valid_format"]:
        suggestions.append("Check the URL format - it should start with https://")

    if not validation["is_https"]:
        suggestions.append("Use HTTPS instead of HTTP for secure connections")

    if not validation["has_webhook_path"]:
        suggestions.append("Ensure the URL contains 'webhook' or 'webhook-test' in the path")

    if not validation["has_webhook_id"]:
        suggestions.append("Make sure the webhook ID is included in the URL")

    # Common n8n issues
    suggestions.extend([
        "Verify the n8n workflow is activated and running",
        "Check if the webhook node is configured as 'POST' method",
        "Ensure the webhook node is set to 'Respond to Webhook' mode",
        "Verify your n8n instance is accessible from your network",
        "Check if there are any firewall or proxy restrictions"
    ])

    return suggestions

def create_test_payload() -> Dict[str, Any]:
    """Create a test payload for webhook testing"""
    return {
        "chatInput": "test connection - please respond with a simple message",
        "sessionId": "debug-test-session-123"
    }

if __name__ == "__main__":
    # Quick test functionality
    test_url = "https://mbcrc.app.n8n.cloud/webhook-test/530ec5fa-656a-4c9c-bb05-5be7ff3bdef2"

    print("🔧 Webhook Debug Utility")
    print("=" * 50)

    # Validate URL format
    print("\n1. URL Validation:")
    validation = validate_webhook_url(test_url)
    for key, value in validation.items():
        if key != "issues":
            print(f"   {key}: {value}")
    if validation["issues"]:
        print("   Issues found:")
        for issue in validation["issues"]:
            print(f"     - {issue}")

    # Test connection
    print("\n2. Connection Test:")
    test_results = test_webhook_connection(test_url)
    print(f"   Connectivity: {test_results['connectivity']}")
    print(f"   Accepts POST: {test_results['accepts_post']}")
    print(f"   Status Code: {test_results['status_code']}")
    if test_results['error_message']:
        print(f"   Error: {test_results['error_message']}")

    # Suggestions
    print("\n3. Suggestions:")
    suggestions = suggest_webhook_fixes(test_url)
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"   {i}. {suggestion}")