# Streamlit Best Practices & Coding Guidelines

## 📚 Official Documentation Links

- **Main Documentation**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **API Reference**: [https://docs.streamlit.io/develop/api-reference](https://docs.streamlit.io/develop/api-reference)
- **Basic Concepts**: [https://docs.streamlit.io/get-started/fundamentals/main-concepts](https://docs.streamlit.io/get-started/fundamentals/main-concepts)
- **Cheat Sheet**: [https://docs.streamlit.io/develop/quick-reference/cheat-sheet](https://docs.streamlit.io/develop/quick-reference/cheat-sheet)
- **Community Forum**: [https://discuss.streamlit.io/](https://discuss.streamlit.io/)
- **Component Gallery**: [https://streamlit.io/gallery](https://streamlit.io/gallery)

## 🏗️ Project Structure & Organization

### Recommended Project Structure
```
my_streamlit_app/
├── .streamlit/
│   ├── config.toml          # App configuration and styling
│   └── secrets.toml         # Secure credentials (add to .gitignore)
├── assets/                  # Reusable UI assets (images, custom CSS)
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── data_processing.py   # Data manipulation functions
│   ├── charts.py           # Chart creation functions
│   └── helpers.py          # General helper functions
├── pages/                   # Multi-page apps (optional)
│   ├── 1_📊_Dashboard.py
│   └── 2_📈_Analytics.py
├── data/                    # Data files
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Git ignore file
└── streamlit_app.py        # Main Streamlit app
```

### Key Structure Principles
- **Keep main script clean**: Focus only on UI and workflow in `streamlit_app.py`
- **Modular approach**: Separate business logic into utility modules
- **Consistent naming**: Use descriptive names for files and functions
- **Documentation**: Include comprehensive README and docstrings

## 🎨 UI/UX Best Practices

### Layout Organization
```python
# Use page config for better presentation
st.set_page_config(
    page_title="My App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Organize with columns for better layout
col1, col2, col3 = st.columns([2, 3, 1])
with col1:
    st.metric("Revenue", "$1.2M", "12%")
with col2:
    st.line_chart(data)
with col3:
    st.button("Refresh")
```

### Visual Hierarchy
```python
# Use proper heading structure
st.title("🏠 Main Application Title")
st.header("📊 Dashboard Section")
st.subheader("Key Metrics")

# Add visual separation
st.divider()  # Adds a horizontal line
st.markdown("---")  # Alternative divider
```

### Sidebar Usage
```python
# Input widgets in sidebar for clean layout
with st.sidebar:
    st.header("⚙️ Controls")
    selected_date = st.date_input("Select Date")
    chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Area"])
    show_data = st.checkbox("Show Raw Data")
```

## 💾 State Management & Session State

### Session State Best Practices
```python
# Initialize session state properly
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Use callbacks for complex state updates
def increment_counter():
    st.session_state.counter += 1

def reset_data():
    st.session_state.user_data = {}
    st.session_state.counter = 0

st.button("Increment", on_click=increment_counter)
st.button("Reset", on_click=reset_data)
```

### Widget Keys for State Management
```python
# Always use keys for important widgets
name = st.text_input("Enter name:", key="user_name")
age = st.number_input("Enter age:", key="user_age", min_value=0)

# Access values anywhere using session state
if st.button("Submit"):
    st.success(f"Hello {st.session_state.user_name}, age {st.session_state.user_age}")
```

## 🚀 Performance Optimization

### Caching Strategies
```python
# Cache data loading operations
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(file_path):
    """Load and process data file."""
    return pd.read_csv(file_path)

# Cache expensive computations
@st.cache_data
def process_data(df, filters):
    """Apply filters and transformations."""
    return df.query(filters).groupby('category').sum()

# Cache resources (models, connections)
@st.cache_resource
def load_model():
    """Load ML model once per session."""
    return joblib.load('model.pkl')

# Clear cache when needed
@st.cache_data
def get_updated_data():
    return fetch_latest_data()

# Clear specific cached function
if st.button("Refresh Data"):
    get_updated_data.clear()
```

### Widget Optimization
```python
# Avoid high-cardinality widgets
# BAD: Creates 10 million options
price = st.selectbox("House Price", range(10000000))

# GOOD: Reasonable options
price_range = st.select_slider(
    "Price Range", 
    options=["<100k", "100k-500k", "500k-1M", "1M+"]
)

# Use appropriate data types
amount = st.number_input("Amount", min_value=0.0, max_value=1000000.0, step=0.01)
```

### Progress Indication
```python
# Show progress for long operations
def long_computation():
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f'Processing {i+1}/100')
        time.sleep(0.1)
    
    status_text.text('Complete!')

# Use spinners for indeterminate progress
with st.spinner('Loading data...'):
    data = load_large_dataset()
st.success('Data loaded successfully!')
```

## 🔒 Security & Configuration

### Secure Secrets Management
```python
# .streamlit/secrets.toml
[database]
username = "myuser"
password = "mypassword"
host = "localhost"

[api]
key = "your-secret-api-key"

# Access in your app
import streamlit as st

# Secure API calls
api_key = st.secrets["api"]["key"]
db_config = st.secrets["database"]

# Environment-specific configs
if "production" in st.secrets:
    database_url = st.secrets["production"]["database_url"]
else:
    database_url = st.secrets["development"]["database_url"]
```

### Input Validation
```python
# Validate user inputs
def validate_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

email = st.text_input("Email Address")
if email and not validate_email(email):
    st.error("Please enter a valid email address")

# Sanitize file uploads
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
        st.error("File too large. Please upload a file smaller than 10MB.")
    else:
        df = pd.read_csv(uploaded_file)
```

## 📊 Data Handling Best Practices

### Efficient Data Display
```python
# Use appropriate display methods
st.dataframe(df, use_container_width=True)  # Interactive table
st.table(df.head())  # Static table for small data
st.json({"key": "value"})  # JSON data

# Add interactivity to data
edited_df = st.data_editor(
    df,
    column_config={
        "price": st.column_config.NumberColumn(
            "Price ($)",
            min_value=0,
            format="$%d"
        )
    }
)
```

### Chart Best Practices
```python
# Use built-in charts for simple cases
st.line_chart(df.set_index('date')['value'])
st.bar_chart(df.set_index('category')['count'])
st.area_chart(df[['series1', 'series2']])

# Custom charts with Plotly for advanced features
import plotly.express as px

fig = px.scatter(df, x='x_col', y='y_col', color='category',
                title='Scatter Plot with Custom Styling')
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)
```

## 🧪 Error Handling & User Feedback

### Comprehensive Error Handling
```python
def safe_data_operation(df, operation):
    try:
        if df.empty:
            st.warning("No data available to process.")
            return None
        
        result = perform_operation(df, operation)
        
        if result is None:
            st.error("Operation failed. Please check your data.")
            return None
        
        st.success("Operation completed successfully!")
        return result
        
    except FileNotFoundError:
        st.error("Data file not found. Please upload a valid file.")
    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("Please refresh the page and try again.")
    
    return None
```

### User Feedback Patterns
```python
# Status messages
st.info("ℹ️ This is an informational message")
st.success("✅ Operation completed successfully!")
st.warning("⚠️ Please review your input")
st.error("❌ An error occurred")

# Toast notifications for quick feedback
if st.button("Save Data"):
    save_data()
    st.toast("Data saved successfully!", icon='🎉')

# Progress status with context
with st.status("Downloading data...", expanded=True) as status:
    st.write("Searching for data...")
    time.sleep(2)
    st.write("Found URL.")
    time.sleep(1)
    st.write("Downloading data...")
    time.sleep(1)
    status.update(label="Download complete!", state="complete", expanded=False)
```

## 🎯 Advanced Patterns

### Custom Components Integration
```python
# Using community components
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header

colored_header(
    label="My Dashboard",
    description="Real-time analytics",
    color_name="blue-70"
)

# Custom CSS styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")
```

### Dynamic Content Generation
```python
# Generate content based on user input
selected_metrics = st.multiselect(
    "Choose metrics to display:",
    ["Revenue", "Users", "Conversion Rate", "Retention"]
)

# Create dynamic layout
cols = st.columns(len(selected_metrics) if selected_metrics else 1)

for i, metric in enumerate(selected_metrics):
    with cols[i]:
        value = get_metric_value(metric)
        change = get_metric_change(metric)
        st.metric(metric, value, change)
```

### Multi-page Applications
```python
# pages/main_app.py structure for multi-page apps
import streamlit as st

st.set_page_config(
    page_title="My App",
    page_icon="🏠",
    layout="wide"
)

# Navigation
st.sidebar.title("Navigation")
pages = {
    "Home": "🏠",
    "Analytics": "📊", 
    "Settings": "⚙️"
}

selected_page = st.sidebar.radio("Go to", list(pages.keys()))

if selected_page == "Home":
    show_home_page()
elif selected_page == "Analytics":
    show_analytics_page()
else:
    show_settings_page()
```

## 📏 Code Quality Standards

### Function Organization
```python
def create_dashboard():
    """Main dashboard creation function."""
    setup_page_config()
    display_header()
    
    data = load_and_cache_data()
    if data is not None:
        display_metrics(data)
        display_charts(data)
        display_data_table(data)

def setup_page_config():
    """Configure page settings."""
    st.set_page_config(
        page_title="Dashboard",
        page_icon="📊",
        layout="wide"
    )

def display_header():
    """Display page header and description."""
    st.title("📊 Business Dashboard")
    st.markdown("Real-time business metrics and analytics")

# Call main function
if __name__ == "__main__":
    create_dashboard()
```

### Documentation Standards
```python
def process_sales_data(df: pd.DataFrame, 
                      date_range: tuple, 
                      categories: list) -> pd.DataFrame:
    """
    Process sales data with filtering and aggregation.
    
    Args:
        df: Raw sales DataFrame with columns ['date', 'category', 'amount']
        date_range: Tuple of (start_date, end_date) for filtering
        categories: List of categories to include in analysis
    
    Returns:
        Processed DataFrame with aggregated metrics
        
    Raises:
        ValueError: If required columns are missing
        
    Example:
        >>> df = load_sales_data()
        >>> result = process_sales_data(df, ('2023-01-01', '2023-12-31'), ['A', 'B'])
    """
    # Implementation here
    pass
```

## 🔄 Development Workflow

### Testing Patterns
```python
# Create test functions
def test_data_processing():
    """Test data processing functions."""
    sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    result = process_data(sample_data)
    assert not result.empty, "Processed data should not be empty"

# Debug mode toggle
DEBUG = st.sidebar.checkbox("Debug Mode")

if DEBUG:
    st.subheader("Debug Information")
    st.write("Session State:", st.session_state)
    st.write("Data Shape:", data.shape if 'data' in locals() else "No data")
```

### Deployment Checklist
- [ ] Remove debug code and test data
- [ ] Secure all API keys in st.secrets
- [ ] Add comprehensive error handling
- [ ] Optimize caching strategies
- [ ] Test with production data volumes
- [ ] Add loading indicators
- [ ] Verify mobile responsiveness
- [ ] Document user workflow

## 🔧 Common Patterns & Snippets

### File Upload Handler
```python
def handle_file_upload():
    """Standard file upload with validation."""
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=['csv', 'xlsx', 'json'],
        help="Upload your data file (max 200MB)"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            
            st.success(f"Successfully loaded {len(df)} rows")
            return df
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            
    return None
```

### Data Filter Component
```python
def create_data_filters(df):
    """Create reusable filter component."""
    st.subheader("🔍 Filters")
    
    filters = {}
    
    # Date range filter
    if 'date' in df.columns:
        date_col = pd.to_datetime(df['date'])
        filters['date_range'] = st.date_input(
            "Date Range",
            value=[date_col.min(), date_col.max()],
            min_value=date_col.min(),
            max_value=date_col.max()
        )
    
    # Category filter
    if 'category' in df.columns:
        filters['categories'] = st.multiselect(
            "Categories",
            options=df['category'].unique(),
            default=df['category'].unique()
        )
    
    return filters
```

---

## 📖 Additional Resources

- **Streamlit Blog**: [https://blog.streamlit.io/](https://blog.streamlit.io/)
- **Best Practices for GenAI Apps**: [https://blog.streamlit.io/best-practices-for-building-genai-apps-with-streamlit/](https://blog.streamlit.io/best-practices-for-building-genai-apps-with-streamlit/)
- **Performance Tips**: [https://blog.streamlit.io/six-tips-for-improving-your-streamlit-app-performance/](https://blog.streamlit.io/six-tips-for-improving-your-streamlit-app-performance/)
- **Component Gallery**: [https://streamlit.io/gallery](https://streamlit.io/gallery)
- **Streamlit Extras**: [https://github.com/arnaudmiribel/streamlit-extras](https://github.com/arnaudmiribel/streamlit-extras)

Remember: Start simple, iterate quickly, and always prioritize user experience!