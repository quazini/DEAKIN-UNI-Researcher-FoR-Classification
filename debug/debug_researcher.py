"""
Debug page to examine researcher profile data processing
"""

import streamlit as st
import json
from utils.webhook_client import WebhookClient
from utils.config import get_config

st.set_page_config(page_title="Researcher Debug", page_icon="🔍")

st.title("🔍 Researcher Profile Debug")

# Check if user is admin (simple check for debugging)
if st.text_input("Debug Password:", type="password") != "debug123":
    st.error("Enter debug password to continue")
    st.stop()

st.success("Debug mode enabled")

# Get configuration
config = get_config()

st.header("Test Researcher Profile Processing")

# Input for researcher query
test_query = st.text_input(
    "Enter researcher query:",
    value="Who is Jessica Tout-Lyon?",
    help="Enter a query to test how the profile data is processed"
)

if st.button("🔄 Process Query"):
    if test_query:
        with st.spinner("Processing query..."):
            try:
                # Send to webhook
                webhook_url = config.get_webhook_url()
                client = WebhookClient(webhook_url)

                response = client.send_message(test_query, "debug-session")

                if response:
                    st.success("✅ Response received successfully")

                    # Show raw response
                    st.subheader("📦 Raw Response Data")
                    with st.expander("View full raw response"):
                        st.json(response)

                    # Show extracted researcher name
                    st.subheader("👤 Extracted Researcher Name")
                    researcher_name = response.get('researcher_name', 'Not found')
                    st.code(f"Researcher Name: {researcher_name}")

                    # Show institutional context
                    st.subheader("🏛️ Institutional Context")
                    institutional_context = response.get('institutional_context', {})

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Organization:**", institutional_context.get('organization', 'Not set'))
                        st.write("**Position:**", institutional_context.get('position', 'Not set'))
                    with col2:
                        st.write("**Department:**", institutional_context.get('department', 'Not set'))
                        st.write("**Email:**", institutional_context.get('email', 'Not set'))

                    # Show biography for analysis
                    st.subheader("📖 Biography Analysis")
                    llm_data = response.get('llm_classification', {})
                    biography = (llm_data.get('evidence_based_biography', '') or
                               llm_data.get('enriched_biography', '') or
                               response.get('enriched_biography', ''))

                    if biography:
                        st.text_area("Biography:", biography, height=200)

                        # Show pattern matches
                        st.subheader("🔍 Pattern Matches in Biography")

                        import re

                        # University patterns
                        university_patterns = [
                            r'affiliated with ([^,\.]+University[^,\.]*)',
                            r'at ([^,\.]+University[^,\.]*)',
                            r'([A-Za-z\s]+University)',
                        ]

                        st.write("**University Patterns Found:**")
                        for i, pattern in enumerate(university_patterns):
                            match = re.search(pattern, biography, re.IGNORECASE)
                            if match:
                                st.write(f"✅ Pattern {i+1}: `{match.group(1).strip()}`")
                            else:
                                st.write(f"❌ Pattern {i+1}: No match")

                        # Name patterns
                        name_patterns = [
                            r'Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:-[A-Z][a-z]+)*)',
                            r'Professor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:-[A-Z][a-z]+)*)',
                            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:-[A-Z][a-z]+)*)\s+is\s+a\s+researcher',
                        ]

                        st.write("**Name Patterns Found:**")
                        for i, pattern in enumerate(name_patterns):
                            match = re.search(pattern, biography)
                            if match:
                                st.write(f"✅ Pattern {i+1}: `{match.group(1).strip()}`")
                            else:
                                st.write(f"❌ Pattern {i+1}: No match")
                    else:
                        st.warning("No biography found in response")

                    # Test extraction functions directly
                    st.subheader("🧪 Direct Function Testing")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Name Extraction Test:**")
                        extracted_name = client.extract_researcher_name_from_response(response)
                        st.code(f"Result: {extracted_name}")

                    with col2:
                        st.write("**Institutional Context Test:**")
                        extracted_context = client.extract_institutional_context(response)
                        st.json(extracted_context)

                else:
                    st.error("❌ No response received")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("Please enter a researcher query")

st.divider()

st.header("🛠️ Manual Testing")

st.subheader("Test Biography Text")
test_biography = st.text_area(
    "Enter biography text to test extraction:",
    value="Dr Jessica Tout-Lyon is a researcher affiliated with Charles Sturt University, specialising in aquatic science and environmental sciences.",
    height=100
)

if st.button("🔍 Test Extraction"):
    if test_biography:
        # Create a mock response
        mock_response = {
            'enriched_biography': test_biography
        }

        # Test with webhook client functions
        client = WebhookClient("dummy-url")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Extracted Name:**")
            name = client.extract_researcher_name_from_response(mock_response)
            st.code(name)

        with col2:
            st.write("**Extracted Institution:**")
            context = client.extract_institutional_context(mock_response)
            for key, value in context.items():
                st.write(f"**{key.title()}:** {value}")