# Example Configuration File for Meraki Dashboard
# =============================================
# Copy this file to config.py and modify the values
# =============================================

# Meraki API Configuration
MERAKI_API_KEY = "1234567890abcdef1234567890abcdef12345678"  # Your actual Meraki API key

# Dashboard Settings
USE_DEMO_DATA = False  # Set to True to use demo data instead of real API
DEFAULT_TIME_RANGE = "Last 24 hours"  # Default time range for analysis
DEFAULT_RESOLUTION = "5 minutes"  # Default data resolution

# Auto-refresh Settings
AUTO_REFRESH_ENABLED = False  # Enable auto-refresh by default
AUTO_REFRESH_INTERVAL = "1 minute"  # Default refresh interval

# Feature Toggles
ENABLE_ADVANCED_METRICS = True
ENABLE_TRAFFIC_ANALYSIS = True
ENABLE_CLIENT_ANALYSIS = True

# Default Bandwidth Analysis Types
DEFAULT_BANDWIDTH_ANALYSIS = [
    "WAN Uplinks (Primary/Secondary)",
    "Peak vs Average Analysis"
]

# Security Settings
HIDE_API_KEY_IN_UI = True  # Hide full API key in UI for security
SHOW_DEBUG_INFO = False  # Show debug information in UI

# =============================================
# Instructions:
# 1. Copy this file to config.py
# 2. Replace the MERAKI_API_KEY with your actual key
# 3. Adjust other settings as needed
# 4. Save the file
# 5. Run the dashboard
# =============================================
