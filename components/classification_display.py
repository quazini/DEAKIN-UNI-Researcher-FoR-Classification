"""
Enhanced classification display components for FoR results
"""

import streamlit as st
from typing import Dict, List, Any

def display_confidence_meter(confidence: str) -> str:
    """Create a visual confidence indicator"""
    confidence_mapping = {
        'high': {'emoji': '🟢', 'color': '#16a34a', 'percentage': 85},
        'medium': {'emoji': '🟡', 'color': '#eab308', 'percentage': 65},
        'low': {'emoji': '🔴', 'color': '#dc2626', 'percentage': 40},
        'unknown': {'emoji': '⚪', 'color': '#6b7280', 'percentage': 20}
    }

    conf_data = confidence_mapping.get(confidence.lower(), confidence_mapping['unknown'])

    # Create a progress bar style confidence meter
    progress_html = f"""
    <div style="background-color: #e5e7eb; border-radius: 10px; padding: 2px; margin: 5px 0;">
        <div style="background-color: {conf_data['color']}; width: {conf_data['percentage']}%;
                    height: 20px; border-radius: 8px; text-align: center; color: white;
                    line-height: 20px; font-size: 12px; font-weight: bold;">
            {conf_data['emoji']} {confidence.title()} ({conf_data['percentage']}%)
        </div>
    </div>
    """
    return progress_html

def display_keyword_tags(keywords: List[str], color_scheme: str = "primary"):
    """Display styled keyword tags using Streamlit components"""
    if not keywords:
        return

    color_schemes = {
        "primary": {"bg": "#dbeafe", "border": "#3b82f6", "emoji": "🔹"},
        "secondary": {"bg": "#f3e8ff", "border": "#8b5cf6", "emoji": "🔸"},
        "success": {"bg": "#dcfce7", "border": "#22c55e", "emoji": "🟢"},
        "warning": {"bg": "#fef3c7", "border": "#f59e0b", "emoji": "🟡"}
    }

    scheme = color_schemes.get(color_scheme, color_schemes["primary"])

    # Create a compact HTML representation for better rendering
    tags_html = ""
    for keyword in keywords[:8]:  # Limit to 8 keywords
        # Clean the keyword text
        clean_keyword = str(keyword).strip().title()
        tags_html += f'<span style="background-color: {scheme["bg"]}; border: 1px solid {scheme["border"]}; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; display: inline-block;">{scheme["emoji"]} {clean_keyword}</span> '

    if tags_html:
        st.markdown(f'<div style="line-height: 2;">{tags_html}</div>', unsafe_allow_html=True)

def display_classification_card(classification: Dict[str, Any], is_primary: bool = True, index: int = 0):
    """Display a single classification in an enhanced card format"""

    field_number = classification.get('field_number', 'N/A')
    field_name = classification.get('field_name', 'Unknown Field')
    confidence = classification.get('confidence', 'unknown')
    reasoning = classification.get('reasoning', 'No reasoning provided')
    keywords = classification.get('evidence_keywords', [])

    # Card styling
    card_border = "#3b82f6" if is_primary else "#8b5cf6"
    card_bg = "#f8fafc" if is_primary else "#fafafa"

    # Expanded state for first few items
    expanded = (is_primary and index < 2) or (not is_primary and index < 1)

    # Get hierarchy information if available
    group_name = classification.get('group_name', '')
    division_name = classification.get('division_name', '')
    rank = classification.get('rank', index + 1)

    with st.expander(
        f"**#{rank} - {field_number}: {field_name}**",
        expanded=expanded
    ):
        # Create columns for layout
        col1, col2 = st.columns([1, 2])

        with col1:
            # Confidence meter
            st.markdown("**Confidence Level:**")
            confidence_html = display_confidence_meter(confidence)
            st.markdown(confidence_html, unsafe_allow_html=True)

            # Hierarchy information
            if group_name or division_name:
                st.markdown("**Hierarchy:**")
                if division_name:
                    st.caption(f"🏢 Division: {division_name}")
                if group_name:
                    st.caption(f"📂 Group: {group_name}")

        with col2:
            # Evidence keywords
            if keywords:
                st.markdown("**Evidence Keywords:**")
                color_scheme = "primary" if is_primary else "secondary"
                display_keyword_tags(keywords, color_scheme)

            # Show scoring details if available
            field_score = classification.get('field_semantic_score')
            combined_score = classification.get('field_combined_score')
            if field_score is not None or combined_score is not None:
                with st.expander("📊 Scoring Details", expanded=False):
                    if field_score is not None:
                        st.caption(f"Semantic Score: {field_score:.3f}")
                    if combined_score is not None:
                        st.caption(f"Combined Score: {combined_score:.3f}")

        # Reasoning section
        st.markdown("**Classification Reasoning:**")
        st.markdown(f"> {reasoning}")

        # Add field number highlight for easy reference
        st.caption(f"Field Reference: **{field_number}** | Rank: **#{rank}**")

def display_classification_overview(classification_data: Dict[str, Any]):
    """Display high-level classification overview with metrics"""

    llm_classification = classification_data.get('llm_classification', {})
    primary_count = len(llm_classification.get('primary_classifications', []))
    secondary_count = len(llm_classification.get('secondary_classifications', []))

    # Overall confidence
    overall_confidence = llm_classification.get('confidence_level', 'medium')

    # Create overview metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Primary Fields", primary_count, help="Main classification fields")

    with col2:
        st.metric("Secondary Fields", secondary_count, help="Supporting classification fields")

    with col3:
        confidence_emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(overall_confidence, '⚪')
        st.metric("Overall Confidence", f"{confidence_emoji} {overall_confidence.title()}")

    with col4:
        # Data quality indicator
        institutional_complete = classification_data.get('institutional_data_complete', False)
        quality_emoji = '✅' if institutional_complete else '⚠️'
        quality_text = 'Complete' if institutional_complete else 'Partial'
        st.metric("Data Quality", f"{quality_emoji} {quality_text}")

    # Show additional n8n-specific metadata if available
    if classification_data.get('classification_timestamp'):
        timestamp = classification_data.get('classification_timestamp', '')
        method = classification_data.get('classification_method', 'standard')

        with st.expander("🔍 Classification Metadata", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Timestamp:** {timestamp[:19].replace('T', ' ')} UTC")
                st.write(f"**Method:** {method}")
            with col2:
                confidence = classification_data.get('classification_confidence', 'medium')
                efficiency = classification_data.get('filtering_efficiency', 'N/A')
                st.write(f"**Confidence:** {confidence}")
                st.write(f"**Filtering:** {efficiency}")

def display_full_classification_results(classification_data: Dict[str, Any]):
    """Display complete classification results with enhanced formatting"""

    if not classification_data:
        st.warning("No classification data available")
        return

    llm_classification = classification_data.get('llm_classification', {})

    # Classification overview
    st.subheader("📊 Classification Overview")
    display_classification_overview(classification_data)

    st.divider()

    # Query response (if available)
    query_response = llm_classification.get('query_response', '')
    if query_response:
        st.subheader("💬 Direct Response")
        st.info(query_response)
        st.divider()

    # Primary Classifications
    primary_classifications = llm_classification.get('primary_classifications', [])
    if primary_classifications:
        st.subheader("🎯 Primary Classifications")
        st.caption("These are the main Fields of Research that best match the researcher's expertise")

        for i, classification in enumerate(primary_classifications):
            display_classification_card(classification, is_primary=True, index=i)

    # Secondary Classifications
    secondary_classifications = llm_classification.get('secondary_classifications', [])
    if secondary_classifications:
        st.subheader("🔄 Secondary Classifications")
        st.caption("These are additional relevant fields that complement the primary classifications")

        for i, classification in enumerate(secondary_classifications):
            display_classification_card(classification, is_primary=False, index=i)

    # Classification Rationale
    rationale = llm_classification.get('classification_rationale', '')
    if rationale:
        with st.expander("📋 Overall Classification Rationale", expanded=False):
            st.markdown(rationale)

def display_data_quality_indicators(response_data: Dict[str, Any]):
    """Display data quality and source indicators"""

    st.subheader("🔍 Data Quality & Sources")

    # Create columns for different indicators
    col1, col2 = st.columns(2)

    with col1:
        # Fuzzy matching info
        search_quality = response_data.get('search_quality', {})
        if search_quality.get('fuzzy_match_used'):
            match_score = search_quality.get('confidence_score', 1.0)
            original_query = search_quality.get('original_query', '')
            resolved_name = search_quality.get('resolved_name', '')

            st.info(f"""
            **Fuzzy Match Applied** 🔍
            Searched: "{original_query}"
            Found: "{resolved_name}"
            Confidence: {match_score*100:.1f}%
            """)
        else:
            st.success("**Exact Match Found** ✅")

    with col2:
        # Data sources
        data_sources = response_data.get('data_sources_used', [])
        if data_sources:
            sources_text = ", ".join([source.title() for source in data_sources])
            st.info(f"**Data Sources:** {sources_text}")

        # Institutional data completeness
        institutional_complete = response_data.get('institutional_data_complete', False)
        if institutional_complete:
            st.success("**Institutional Data:** Complete ✅")
        else:
            st.warning("**Institutional Data:** Partial ⚠️")