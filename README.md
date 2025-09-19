# 🔬 FoR Classification Chat Interface

A beautiful Streamlit application for interacting with the n8n FoR (Fields of Research) Classification webhook system. This app provides an intuitive chat interface for researcher classification with enhanced visualizations.

## Features

- 💬 **Chat Interface**: Conversational UI for researcher queries
- 🎯 **FoR Classification**: Displays primary and secondary field classifications
- 👨‍🔬 **Researcher Profiles**: Comprehensive researcher information and metrics
- 📊 **Data Visualization**: Beautiful charts and confidence indicators
- 🔍 **Data Quality**: Shows data sources and match confidence
- 🎨 **Modern UI**: Responsive design with custom styling

## Prerequisites

- Python 3.8+
- Active n8n instance with FoR Classification workflow
- Webhook URL from your n8n workflow

## Installation

1. **Navigate to the project directory**:
   ```bash
   cd "Classification Agent"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the webhook URL**:
   - Update the `DEFAULT_WEBHOOK_URL` in `app.py` with your n8n webhook URL
   - Or configure it through the app interface sidebar

## Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Test the webhook connection** using the "🔧 Test Webhook Connection" button in the sidebar

4. **Start chatting**! Try queries like:
   - "Who is Dr. Jane Smith?"
   - "Classify Professor John Doe"
   - "Find researcher expertise in biotechnology"

## ✅ Current Status

The application is **fully functional** and ready to use with your n8n webhook:
- ✅ Response format parsing works correctly
- ✅ All UI components handle the n8n data structure
- ✅ Rich classification details are displayed
- ✅ Researcher profiles show institutional information
- ✅ Enhanced error handling and debugging tools included

## Usage Examples

### Sample Queries

- **Researcher Lookup**: "Who is Dr. Jane Smith?"
- **Direct Classification**: "Classify Professor John Doe"
- **Field Discovery**: "Show me researchers in biotechnology"
- **Research Area**: "Find experts in machine learning"
- **Institution Query**: "Who works at [University Name]?"
- **General Inquiry**: "Tell me about researchers in quantum computing"

### Expected Response Format

The n8n webhook should return data in this structure:

```json
{
  "llm_classification": {
    "primary_classifications": [...],
    "secondary_classifications": [...],
    "evidence_based_biography": "...",
    "query_response": "..."
  },
  "researcher_name": "...",
  "institutional_context": {...},
  "data_quality": {...}
}
```

## Configuration

### Webhook Settings

1. Open the sidebar in the app
2. Enter your n8n webhook URL in the "Settings" section
3. The URL should look like: `https://your-n8n-instance.com/webhook/[webhook-id]`

### Customization

- **Styling**: Modify `assets/styles.css` for custom appearance
- **Components**: Update files in `components/` for enhanced visualizations
- **Webhook Client**: Modify `utils/webhook_client.py` for different API patterns

## Project Structure

```
Classification Agent/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── components/
│   ├── __init__.py
│   ├── classification_display.py  # FoR classification components
│   └── researcher_profile.py      # Researcher profile components
├── utils/
│   ├── __init__.py
│   └── webhook_client.py          # Webhook communication utilities
└── assets/
    └── styles.css                 # Custom CSS styling
```

## Features Breakdown

### 🎯 Classification Display

- **Primary Classifications**: 5 main FoR fields with confidence indicators
- **Secondary Classifications**: 3 supporting fields
- **Evidence Keywords**: Visual tags showing supporting evidence
- **Reasoning**: Detailed explanation for each classification

### 👨‍🔬 Researcher Profiles

- **Basic Information**: Name, ORCID, institutional affiliation
- **Research Metrics**: Publications, citations, h-index, patents
- **Professional Biography**: AI-generated summary based on research data
- **Research Interests**: Visual tag cloud of expertise areas

### 🔍 Data Quality Indicators

- **Match Confidence**: Shows fuzzy matching results if applicable
- **Data Sources**: Displays which databases provided information
- **Completeness**: Indicates quality of institutional and research data

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Verify the webhook URL is correct
   - Check that your n8n instance is running
   - Ensure the webhook is accessible from your network

2. **Timeout Errors**:
   - Classification can take 15-30 seconds
   - Increase timeout in `webhook_client.py` if needed

3. **Invalid Response Format**:
   - Check that your n8n workflow returns the expected JSON structure
   - Review the webhook response in the browser developer tools

### Debug Mode

Enable detailed logging by modifying the webhook client:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your n8n workflow
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the n8n workflow configuration
- Ensure all required dependencies are installed

---

*Built with ❤️ using Streamlit and designed for the n8n FoR Classification workflow*