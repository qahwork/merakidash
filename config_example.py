# Meraki Network Analytics Dashboard Pro - Configuration Template
# =============================================================
# Copy this file to config.py and modify the values for your environment
# =============================================================

# =============================================
# 🔐 API CONFIGURATION
# =============================================

# Meraki API Key (REQUIRED)
# Get your API key from: https://dashboard.meraki.com/organization/settings/api
MERAKI_API_KEY = "your_meraki_api_key_here"

# API Rate Limiting
API_RATE_LIMIT = 5  # Requests per second
API_TIMEOUT = 30  # Request timeout in seconds

# =============================================
# 🔑 LOGIN CONFIGURATION
# =============================================

# Login Credentials (REQUIRED)
LOGIN_USERNAME = "admin"  # Change to your desired username
LOGIN_PASSWORD = "your_secure_password_here"  # Change to your secure password

# =============================================
# 🏢 ORGANIZATION CONFIGURATION
# =============================================

# Default Organization (Optional)
# Set to None to show all organizations, or specify an organization ID
DEFAULT_ORGANIZATION = None  # Example: "123456789012345678"

# Allowed Organization IDs (Optional)
# Set to None to show all organizations, or specify a list of organization IDs
ALLOWED_ORGANIZATION_IDS = None  # Example: ["123456789012345678", "987654321098765432"]

# =============================================
# 🎨 BRANDING CONFIGURATION
# =============================================

# Company Logo (Optional)
# Add your company logo file to the project root and specify the filename
COMPANY_LOGO_PATH = "company_logo.png"  # Path to your company logo file

# Company Information
COMPANY_NAME = "Your Company Name"  # Your company name
COMPANY_TAGLINE = "Your Company Tagline"  # Your company tagline/slogan
COMPANY_COLOR = "#FF6B35"  # Your company's primary color (hex code)

# =============================================
# 🎛️ DASHBOARD SETTINGS
# =============================================

# Demo Mode (for testing without hardware)
USE_DEMO_DATA = False

# Default Analysis Settings
DEFAULT_TIME_RANGE = "Last 24 hours"  # Options: "Last hour", "Last 2 hours", "Last 24 hours", "Last 3 days", "Last week", "Last month"
DEFAULT_RESOLUTION = "5 minutes"  # Options: "1 minute", "5 minutes", "15 minutes", "1 hour", "1 day"

# Performance Settings
MAX_WORKERS = 200  # Maximum parallel API workers
CACHE_TTL = 60  # Cache time-to-live in seconds
ENABLE_PARALLEL_LOADING = True  # Enable parallel data loading

# =============================================
# 🔄 AUTO-REFRESH SETTINGS
# =============================================

AUTO_REFRESH_ENABLED = False  # Enable auto-refresh by default
AUTO_REFRESH_INTERVAL = "1 minute"  # Options: "30 seconds", "1 minute", "5 minutes", "15 minutes"

# =============================================
# 🎯 FEATURE TOGGLES
# =============================================

# Core Features
ENABLE_ADVANCED_METRICS = True
ENABLE_TRAFFIC_ANALYSIS = True
ENABLE_CLIENT_ANALYSIS = True
ENABLE_SWITCH_MONITORING = True
ENABLE_BANDWIDTH_ANALYSIS = True
ENABLE_DEVICE_ALERTS = True
ENABLE_LICENSE_INFO = True

# Advanced Features
ENABLE_WEBHOOK_RECEIVER = True
ENABLE_DATA_EXPORT = True
ENABLE_REAL_TIME_MONITORING = True

# =============================================
# 📊 DEFAULT ANALYSIS TYPES
# =============================================

# Default Bandwidth Analysis Types
DEFAULT_BANDWIDTH_ANALYSIS = [
    "WAN Uplinks (Primary/Secondary)",
    "Peak vs Average Analysis",
    "VPN Tunnel Performance"
]

# Default Traffic Analysis Types
DEFAULT_TRAFFIC_ANALYSIS = [
    "Application Usage",
    "Client Activity",
    "Upload vs Download"
]

# =============================================
# 🔒 SECURITY SETTINGS
# =============================================

# UI Security
HIDE_API_KEY_IN_UI = True  # Hide full API key in UI for security
SHOW_DEBUG_INFO = False  # Show debug information in UI
ENABLE_ACCESS_LOG = True  # Log access attempts

# Session Security
SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)
MAX_SESSION_AGE = 86400  # Maximum session age in seconds (24 hours)

# =============================================
# 🌐 WEBHOOK CONFIGURATION
# =============================================

# Webhook Settings
WEBHOOK_ENABLED = True
WEBHOOK_SECRET = "your_webhook_secret_here"  # Shared secret for webhook validation
WEBHOOK_STORE_EVENTS = 1000  # Maximum number of events to store in memory
WEBHOOK_PORT = 8080  # Port for webhook receiver

# Webhook Event Types
WEBHOOK_EVENT_TYPES = [
    "device_status_changed",
    "network_alert",
    "client_connected",
    "client_disconnected"
]

# =============================================
# 🐳 DOCKER CONFIGURATION
# =============================================

# Docker Settings
DOCKER_PORT = 8501  # Port for Streamlit app
DOCKER_HOST = "0.0.0.0"  # Host binding
DOCKER_HEADLESS = True  # Run in headless mode

# =============================================
# 📝 LOGGING CONFIGURATION
# =============================================

# Log Levels
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/dashboard.log"  # Log file path
LOG_MAX_SIZE = 10485760  # Max log file size (10MB)
LOG_BACKUP_COUNT = 5  # Number of backup log files

# =============================================
# 🚀 DEPLOYMENT SETTINGS
# =============================================

# Production Settings
PRODUCTION_MODE = False  # Enable production optimizations
ENABLE_HTTPS = False  # Enable HTTPS (requires SSL certificates)
SSL_CERT_PATH = "ssl/cert.pem"  # SSL certificate path
SSL_KEY_PATH = "ssl/key.pem"  # SSL private key path

# Nginx Configuration
NGINX_ENABLED = True  # Enable Nginx reverse proxy
NGINX_PORT = 80  # Nginx port
NGINX_SSL_PORT = 443  # Nginx SSL port

# =============================================
# 📋 INSTRUCTIONS
# =============================================
# 1. Copy this file to config.py
# 2. Replace MERAKI_API_KEY with your actual Meraki API key
# 3. Adjust other settings according to your environment
# 4. For production deployment:
#    - Set PRODUCTION_MODE = True
#    - Configure SSL certificates
#    - Set appropriate log levels
# 5. Save the file and run the dashboard
# =============================================
