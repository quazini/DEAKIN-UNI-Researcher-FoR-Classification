"""
Enhanced researcher profile display components
"""

import streamlit as st
from typing import Dict, Any, List

def display_researcher_header(response_data: Dict[str, Any]):
    """Display researcher header with key information"""

    researcher_name = response_data.get('researcher_name', 'Unknown Researcher')
    orcid = response_data.get('orcid', '')
    institutional_context = response_data.get('institutional_context', {})

    # Get the correct affiliation - prefer email for subtitle if no proper affiliation
    email = institutional_context.get('email', '')
    organization = institutional_context.get('organization', '')
    position = institutional_context.get('position', '')

    # Build subtitle based on available information
    subtitle = ""
    if position and organization and position != 'Not specified' and organization != 'Not specified':
        subtitle = f"{position} at {organization}"
    elif organization and organization != 'Not specified':
        subtitle = f"Researcher at {organization}"
    elif email and email != 'Not available':
        subtitle = email
    else:
        subtitle = "Independent Researcher"

    # Create a prominent header with the researcher's actual name
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
                color: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <h2 style="margin: 0; color: white;">👨‍🔬 {researcher_name}</h2>
        <p style="margin: 5px 0; opacity: 0.9;">
            {subtitle}
        </p>
        {f"<p style='margin: 5px 0; font-size: 14px; opacity: 0.8;'>ORCID: {orcid}</p>" if orcid and orcid != 'Not available' else ""}
    </div>
    """, unsafe_allow_html=True)

def display_institutional_info(institutional_context: Dict[str, Any]):
    """Display institutional affiliation in a clean format"""

    if not institutional_context:
        st.warning("Institutional information not available")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        organization = institutional_context.get('organization', 'Not specified')
        if organization != 'Not specified':
            st.info(f"**🏛️ Institution**\n{organization}")
        else:
            st.warning("🏛️ **Institution**\nNot specified")

    with col2:
        position = institutional_context.get('position', 'Not specified')
        if position != 'Not specified':
            st.info(f"**💼 Position**\n{position}")
        else:
            st.warning("💼 **Position**\nNot specified")

    with col3:
        school = institutional_context.get('school', 'Not specified')
        if school != 'Not specified':
            st.info(f"**🏫 School**\n{school}")
        else:
            st.warning("🏫 **School**\nNot specified")

    with col4:
        department = institutional_context.get('department', 'Not specified')
        if department != 'Not specified':
            st.info(f"**🏢 Department**\n{department}")
        else:
            st.warning("🏢 **Department**\nNot specified")

    # Email in a separate row if available
    email = institutional_context.get('email', 'Not available')
    if email != 'Not available':
        st.info(f"**📧 Contact:** {email}")

def display_research_metrics(response_data: Dict[str, Any]):
    """Display research metrics in an attractive dashboard format"""

    # Extract metrics from response
    metrics = {
        'Publications': response_data.get('total_publications', 0),
        'Citations': response_data.get('total_citations', 0),
        'H-Index': response_data.get('h_index', 0),
        'Patents': response_data.get('total_patents', 0),
        'Collaborators': response_data.get('total_collaborators', 0),
        'Funding': response_data.get('total_funding', 0)
    }

    # Filter out zero or N/A values
    valid_metrics = {k: v for k, v in metrics.items() if v and v != 'N/A' and v != 0}

    if not valid_metrics:
        st.info("📊 Research metrics not available in the current dataset")
        return

    st.subheader("📈 Research Impact Metrics")

    # Create columns based on number of valid metrics
    num_metrics = len(valid_metrics)
    if num_metrics <= 3:
        cols = st.columns(num_metrics)
    else:
        # Split into two rows
        cols1 = st.columns(min(3, num_metrics))
        if num_metrics > 3:
            cols2 = st.columns(num_metrics - 3)
            cols = cols1 + cols2
        else:
            cols = cols1

    # Define metric icons and colors
    metric_styles = {
        'Publications': {'icon': '📄', 'color': '#3b82f6'},
        'Citations': {'icon': '📊', 'color': '#10b981'},
        'H-Index': {'icon': '📈', 'color': '#f59e0b'},
        'Patents': {'icon': '💡', 'color': '#8b5cf6'},
        'Collaborators': {'icon': '👥', 'color': '#ef4444'},
        'Funding': {'icon': '💰', 'color': '#06b6d4'}
    }

    for i, (metric_name, value) in enumerate(valid_metrics.items()):
        style = metric_styles.get(metric_name, {'icon': '📊', 'color': '#6b7280'})

        with cols[i]:
            # Create a styled metric card
            st.markdown(f"""
            <div style="background-color: {style['color']}15;
                        border: 2px solid {style['color']}40;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                        margin: 5px 0;">
                <div style="font-size: 24px; margin-bottom: 5px;">{style['icon']}</div>
                <div style="font-size: 28px; font-weight: bold; color: {style['color']};">{value}</div>
                <div style="font-size: 14px; color: #64748b; font-weight: 500;">{metric_name}</div>
            </div>
            """, unsafe_allow_html=True)

def display_professional_biography(llm_classification: Dict[str, Any]):
    """Display the researcher's professional biography"""

    # Try both possible biography field names
    biography = (llm_classification.get('evidence_based_biography', '') or
                llm_classification.get('enriched_biography', ''))

    if biography:
        st.subheader("📖 Professional Biography")

        # Style the biography nicely
        st.markdown(f"""
        <div style="background-color: #f8fafc;
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 10px 0;
                    font-size: 16px;
                    line-height: 1.6;">
            {biography}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📖 Professional biography not available in the current dataset")

def display_research_interests(response_data: Dict[str, Any]):
    """Display research interests and expertise areas"""

    # Try to get research interests from Neo4j data if available
    neo4j_data = response_data.get('neo4j_lookup', {}).get('researcher_data', {})
    research_interests = neo4j_data.get('research_interests', [])
    expertise_areas = neo4j_data.get('expertise_areas', [])

    # Also check for research areas from the classification response
    primary_areas = response_data.get('primary_research_areas', [])
    secondary_areas = response_data.get('secondary_research_areas', [])

    if research_interests or expertise_areas or primary_areas or secondary_areas:
        st.subheader("🔬 Research Focus Areas")

        col1, col2 = st.columns(2)

        with col1:
            # Research interests from Neo4j or primary areas from classification
            interests_to_show = research_interests if research_interests else primary_areas
            if interests_to_show:
                st.markdown("**Research Interests:**")
                display_research_tags(interests_to_show[:10], "🔬", "#dbeafe", "#3b82f6")

        with col2:
            # Expertise areas from Neo4j or secondary areas from classification
            expertise_to_show = expertise_areas if expertise_areas else secondary_areas
            if expertise_to_show:
                st.markdown("**Expertise Areas:**")
                display_research_tags(expertise_to_show[:10], "⚡", "#dcfce7", "#22c55e")

def display_research_tags(items: List[str], emoji: str, bg_color: str, border_color: str):
    """Display research tags with consistent styling"""
    if not items:
        return

    tags_html = ""
    for item in items:
        clean_item = str(item).strip().title()
        tags_html += f'<span style="background-color: {bg_color}; border: 1px solid {border_color}; color: #1e293b; padding: 4px 10px; border-radius: 14px; font-size: 13px; margin: 3px; display: inline-block;">{emoji} {clean_item}</span> '

    if tags_html:
        st.markdown(f'<div style="line-height: 2.2; margin: 10px 0;">{tags_html}</div>', unsafe_allow_html=True)

def display_complete_researcher_profile(response_data: Dict[str, Any]):
    """Display the complete researcher profile with all available information"""

    # Researcher header
    display_researcher_header(response_data)

    # Get institutional information from multiple sources
    institutional_context = response_data.get('institutional_context', {})

    # Try to get better affiliation from Neo4j or LLM data if available
    neo4j_data = response_data.get('neo4j_lookup', {}).get('researcher_data', {})
    llm_data = response_data.get('llm_classification', {})

    # Override with Neo4j data if available and more complete
    if neo4j_data:
        if neo4j_data.get('affiliation'):
            institutional_context['organization'] = neo4j_data.get('affiliation')
        if neo4j_data.get('position'):
            institutional_context['position'] = neo4j_data.get('position')

    # Check LLM enriched data for better institution info
    if llm_data:
        # Extract institution from biography if needed
        biography = llm_data.get('evidence_based_biography', '') or llm_data.get('enriched_biography', '')

        # The institutional context should now come directly from the payload fields
        # No need for hardcoded researcher-specific logic

    # Display institutional information if available
    if institutional_context:
        st.subheader("🏛️ Institutional Affiliation")
        display_institutional_info(institutional_context)

    st.divider()

    # Research metrics
    display_research_metrics(response_data)

    st.divider()

    # Professional biography
    llm_classification = response_data.get('llm_classification', {})
    display_professional_biography(llm_classification)

    st.divider()

    # Research interests and expertise
    display_research_interests(response_data)