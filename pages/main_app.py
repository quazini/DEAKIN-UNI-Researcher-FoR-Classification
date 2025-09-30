"""
FoR Classification Chat Interface
A Streamlit application for interacting with the n8n FoR Classification webhook
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Import custom components and utilities
from utils.webhook_client import WebhookClient
from components.classification_display import display_full_classification_results, display_data_quality_indicators
from components.researcher_profile import display_complete_researcher_profile
from utils.flexible_auth import require_authentication, logout, check_authentication
from utils.config import get_config
from utils.neo4j_service import get_neo4j_service, clear_researcher_cache

# Configure Streamlit page
st.set_page_config(
    page_title="🔬 FoR Classification Chat",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication - redirect to login if not authenticated
if not check_authentication():
    st.switch_page("login.py")

# Ensure user is authenticated for this page
require_authentication()

# Get configuration
config = get_config()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'webhook_url' not in st.session_state:
    st.session_state.webhook_url = config.get_webhook_url()

def send_to_webhook(message: str, session_id: str, webhook_url: str) -> Optional[Dict[Any, Any]]:
    """Send message to n8n webhook and return response"""
    try:
        client = WebhookClient(webhook_url)

        with st.spinner("🔄 Processing your request... This may take 15-30 seconds"):
            response = client.send_message(message, session_id)

            # Validate response
            if not client.validate_response(response):
                error_msg = client.extract_error_message(response)
                if error_msg:
                    st.error(f"❌ {error_msg}")
                else:
                    st.error("❌ Invalid response format from classification service")
                return None

            return response

    except TimeoutError:
        st.error("There was an error processing your request. Please verify that the researcher name is correct. If you're certain the name is accurate, try submitting your request again.")
        return None
    except ConnectionError:
        st.error("❌ Failed to connect to the classification service. Please check the webhook URL.")
        return None
    except ValueError as e:
        # Check if it's a JSON parsing error specifically
        if "Invalid JSON response" in str(e) or "Invalid response format" in str(e):
            st.error("There was an error processing your request. Please verify that the researcher name is correct. If you're certain the name is accurate, try submitting your request again.")
        else:
            st.error(f"❌ Service error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def display_message(message: Dict[str, Any], is_user: bool = False):
    """Display a chat message"""
    if is_user:
        with st.chat_message("user", avatar="👤"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            if message["type"] == "text":
                st.write(message["content"])
            elif message["type"] == "classification":
                # Display the original query response
                query_response = message.get("data", {}).get("llm_classification", {}).get("query_response", "")
                if query_response:
                    st.write(query_response)
                    st.divider()

                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["🎯 Classifications", "👨‍🔬 Researcher Profile", "🔍 Data Quality"])

                with tab1:
                    display_full_classification_results(message["data"])

                with tab2:
                    display_complete_researcher_profile(message["data"])

                with tab3:
                    display_data_quality_indicators(message["data"])

# Main UI
st.title("🔬 FoR Classification Chat Interface")
st.markdown("*Ask questions about researchers or request field classifications*")

# Sidebar with instructions and settings
with st.sidebar:
    # User info section at the top
    st.markdown("### 👤 User Profile")
    st.info(f"**{st.session_state.get('user_name', 'User')}**\n{st.session_state.get('user_email', '')}")

    # Admin panel button if user is admin
    if st.session_state.get('user_role') == 'admin':
        if st.button("👑 Admin Panel", use_container_width=True, type="primary"):
            st.switch_page("pages/admin.py")

    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("login.py")

    st.divider()

    # Researcher Lookup Section
    st.header("🔍 Researcher Lookup")

    # Initialize Neo4j service
    neo4j_service = get_neo4j_service()

    # Check connection status
    if neo4j_service.is_connected():
        # Get researchers list
        researchers = neo4j_service.get_researchers()

        if researchers:
            # Create options for selectbox (name as display, full dict as value)
            researcher_options = ["Select a researcher..."] + [r['name'] for r in researchers]

            selected_researcher_name = st.selectbox(
                "Choose researcher:",
                options=researcher_options,
                index=0,
                help="Select a researcher to auto-populate the chat input"
            )

            # Handle researcher selection
            if selected_researcher_name != "Select a researcher...":
                # Find the selected researcher
                selected_researcher = next(
                    (r for r in researchers if r['name'] == selected_researcher_name),
                    None
                )

                if selected_researcher:
                    # Store in session state
                    st.session_state['selected_researcher'] = selected_researcher

                    # Show researcher info
                    st.info(f"**Selected:** {selected_researcher['name']}\n**Contact ID:** {selected_researcher['contactRecordId']}")

                    # Button to populate chat input
                    if st.button("🗨️ Query this researcher", use_container_width=True):
                        # Store the query to be used in chat input
                        st.session_state['auto_query'] = f"Who is {selected_researcher['name']}?"
                        st.rerun()

            # Show researcher count
            st.caption(f"📊 {len(researchers)} researchers available")

            # Cache management
            if st.button("🔄 Refresh researcher list", help="Clear cache and reload researchers"):
                clear_researcher_cache()
                st.rerun()
        else:
            st.warning("No researchers found in the database.")

        # Connection status indicator
        status = neo4j_service.get_connection_status()
        if status['status'] == 'connected':
            st.success(f"✅ Neo4j: {status['details']}")
        else:
            st.error(f"❌ Neo4j: {status['message']}")
    else:
        st.error("❌ Neo4j database not connected")
        st.caption("Check environment variables: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")

        # Test connection button
        if st.button("🔧 Test Neo4j Connection"):
            # Reinitialize service by clearing the cache
            clear_researcher_cache()
            st.rerun()

    st.divider()

    st.header("💡 How to Use")
    st.markdown("""
    **Example queries:**
    - "Who is Dr. Jane Smith?"
    - "Classify Professor John Doe"
    - "Find researcher expertise in biotechnology"
    - "What are the research areas for Dr. Emily Johnson?"

    **Features:**
    - 🎯 FoR field classification
    - 👨‍🔬 Researcher profiles
    - 📊 Research metrics
    - 🔍 Confidence indicators
    """)

    st.divider()

    # Configuration
    st.header("⚙️ Settings")
    webhook_url = st.text_input("Webhook URL", value=st.session_state.webhook_url, help="n8n webhook endpoint")

    # Update session state if URL changed
    if webhook_url != st.session_state.webhook_url:
        st.session_state.webhook_url = webhook_url

    # Test webhook connection
    if st.button("🔧 Test Webhook Connection"):
        from utils.debug_webhook import test_webhook_connection, validate_webhook_url, suggest_webhook_fixes

        with st.spinner("Testing webhook connection..."):
            # URL validation
            validation = validate_webhook_url(st.session_state.webhook_url)
            test_results = test_webhook_connection(st.session_state.webhook_url)

            if test_results["connectivity"] and test_results["accepts_post"]:
                st.success("✅ Webhook connection successful!")
                if test_results["responds_to_test"]:
                    st.info("🎉 Webhook responds with valid data")
            else:
                st.error("❌ Webhook connection failed")

                with st.expander("🔍 Debug Information"):
                    st.write("**Connection Results:**")
                    st.json(test_results)

                    st.write("**URL Validation:**")
                    st.json(validation)

                    st.write("**Suggested Fixes:**")
                    suggestions = suggest_webhook_fixes(st.session_state.webhook_url)
                    for i, suggestion in enumerate(suggestions[:5], 1):
                        st.write(f"{i}. {suggestion}")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Troubleshooting section
    st.header("🔧 Troubleshooting")

    with st.expander("📖 Common Issues & Solutions"):
        st.markdown("""
        **🚨 Getting 404 Error?**
        1. **Check if n8n workflow is activated** (most common fix!)
        2. Verify webhook node is set to POST method
        3. Ensure "Respond to Webhook" is selected

        **⏰ Request Timeouts?**
        - Classification takes 15-30 seconds
        - Wait for the process to complete
        - Check n8n workflow for errors

        **❌ Connection Errors?**
        - Verify the webhook URL is correct
        - Check your internet connection
        - Try the webhook test button above

        **📋 Checklist:**
        - [ ] Workflow activated in n8n
        - [ ] All API keys configured (OpenAI, Neo4j, Qdrant)
        - [ ] Webhook responds to test
        """)

    st.divider()

    # Session info
    st.header("📋 Session Info")
    st.text(f"Session ID: {st.session_state.session_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    st.text(f"Role: {st.session_state.get('user_role', 'user').title()}")

    # Show current webhook status
    if st.session_state.webhook_url:
        webhook_domain = st.session_state.webhook_url.split('/')[2] if '/' in st.session_state.webhook_url else 'Unknown'
        st.text(f"Webhook: {webhook_domain}")

    # Add link to troubleshooting guide
    st.markdown("📖 [View Full Troubleshooting Guide](./TROUBLESHOOTING.md)")

# Chat interface
chat_container = st.container()

# Display existing messages
with chat_container:
    for message in st.session_state.messages:
        display_message(message, is_user=message.get("role") == "user")

# Message input
if not st.session_state.is_processing:
    # Check for auto-query from researcher selection
    auto_query = st.session_state.get('auto_query', '')
    if auto_query:
        # Use auto query and clear it
        prompt = auto_query
        st.session_state['auto_query'] = ''
    else:
        prompt = st.chat_input("Type your message here... (e.g., 'Who is Dr. Jane Smith?')")

    if prompt:
        # Add user message to history
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)

        # Display user message immediately
        with chat_container:
            display_message(user_message, is_user=True)

        # Set processing state
        st.session_state.is_processing = True

        # Send to webhook
        response_data = send_to_webhook(prompt, st.session_state.session_id, st.session_state.webhook_url)

        # Reset processing state
        st.session_state.is_processing = False

        if response_data:
            # Create assistant response
            assistant_message = {
                "role": "assistant",
                "type": "classification",
                "data": response_data,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.messages.append(assistant_message)

            # Display assistant response
            with chat_container:
                display_message(assistant_message)

        # Rerun to update the interface
        st.rerun()

else:
    st.info("🔄 Processing your request...")

# Footer
st.markdown("---")
st.markdown(f"*Powered by n8n FoR Classification Workflow | Built with Streamlit | Logged in as {st.session_state.get('user_name', 'User')}*")