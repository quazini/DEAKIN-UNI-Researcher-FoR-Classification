# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 streamlit

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/streamlit/.local

# Copy application code
COPY --chown=streamlit:streamlit . .

# Create necessary directories
RUN mkdir -p /app/.streamlit /app/logs \
    && chown -R streamlit:streamlit /app

# Switch to non-root user
USER streamlit

# Update PATH
ENV PATH=/home/streamlit/.local/bin:$PATH

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_PRIMARY_COLOR="#1E3A8A" \
    STREAMLIT_THEME_BACKGROUND_COLOR="#FFFFFF" \
    STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR="#F8FAFC" \
    STREAMLIT_THEME_TEXT_COLOR="#1E293B" \
    APP_ENV=production

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
ENTRYPOINT ["streamlit", "run"]
CMD ["login.py", "--server.maxUploadSize=50"]