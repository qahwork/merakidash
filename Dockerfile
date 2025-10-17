# Meraki Network Analytics Dashboard Pro - Production Dockerfile
# Optimized for Ubuntu Server deployment
# =============================================================

# Use Python 3.11 slim image based on Ubuntu
FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Set work directory
WORKDIR /app

# Install system dependencies for Ubuntu
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /app/logs

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app && \
    chmod +x /app/meraki_dashboard_complete_final.py

# Switch to non-root user
USER streamlit

# Create necessary directories
RUN mkdir -p /app/logs /app/ssl /app/data

# Expose port
EXPOSE 8501

# Health check with retry
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Add labels for better container management
LABEL maintainer="Meraki Dashboard Team"
LABEL version="1.0.0"
LABEL description="Meraki Network Analytics Dashboard Pro"

# Run the application with production settings
CMD ["streamlit", "run", "meraki_dashboard_complete_final.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true"]
