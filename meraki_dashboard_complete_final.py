# Meraki Network Analytics Dashboard - Complete Fixed Version
# Fixed metrics calculation and enhanced traffic analysis display
import streamlit as st
import meraki
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
import os
import sys
import time

# Parallel processing imports
import concurrent.futures
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from functools import partial
import logging
import queue
import time

# Performance optimization: Enable parallel API calls for maximum speed
# This implementation uses ThreadPoolExecutor to run multiple API calls simultaneously
# Expected performance improvement: 3-5x faster data loading compared to sequential calls

# Suppress Streamlit ScriptRunContext warnings in parallel threads
logging.getLogger("streamlit.runtime.scriptrunner.script_runner").setLevel(logging.ERROR)

# Set environment variable to suppress Streamlit warnings
import os
os.environ["STREAMLIT_LOGGER_LEVEL"] = "ERROR"

# Additional warning suppression for parallel processing
import warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# Set up thread-local warning suppression
import threading
_thread_local = threading.local()

def setup_thread_warnings():
    """Setup warning suppression for each thread"""
    if not hasattr(_thread_local, 'warnings_setup'):
        import warnings
        import os
        # Set environment variable for this thread
        os.environ["STREAMLIT_LOGGER_LEVEL"] = "ERROR"
        warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")
        warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
        warnings.filterwarnings("ignore", category=RuntimeWarning, module="streamlit")
        _thread_local.warnings_setup = True

warnings.filterwarnings('ignore')

# Session persistence
import json
import hashlib
from pathlib import Path

# Configuration
try:
    # Try to import from current directory first
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import MERAKI_API_KEY, DEFAULT_ORGANIZATION, DEFAULT_NETWORKS, DEFAULT_TIMESPAN, DEFAULT_RESOLUTION, DEFAULT_BANDWIDTH_ANALYSIS, SHOW_DEBUG_INFO
except ImportError:
    try:
        # Try to import from Documents/merakitest
        sys.path.insert(0, os.path.expanduser("~/Documents/merakitest"))
        from config import MERAKI_API_KEY, DEFAULT_ORGANIZATION, DEFAULT_NETWORKS, DEFAULT_TIMESPAN, DEFAULT_RESOLUTION, DEFAULT_BANDWIDTH_ANALYSIS, SHOW_DEBUG_INFO
    except ImportError:
        # Fallback to safe default values - NO HARDCODED API KEYS
        MERAKI_API_KEY = None  # Must be set via config.py or environment variable
        DEFAULT_ORGANIZATION = None  # Must be set via config.py
        DEFAULT_NETWORKS = []
        DEFAULT_TIMESPAN = "Last 24 hours"
        DEFAULT_RESOLUTION = "5 minutes"
        DEFAULT_BANDWIDTH_ANALYSIS = ["WAN Uplinks (Primary/Secondary)", "Peak vs Average Analysis"]
        SHOW_DEBUG_INFO = False

# Page config
st.set_page_config(
    page_title="Meraki Network Analytics Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better text visibility and layout optimization
st.markdown("""
<style>
    /* ========== TOP PADDING REMOVAL - ENHANCED VERSION ========== */
    /* Based on suggested approach but with broader compatibility */
    
    /* Main content area - multiple selectors for version compatibility */
    .css-18e3th9, .main .block-container, .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        max-width: 100% !important;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Header removal - comprehensive approach */
    .stApp > header, header, .css-1v0mbdj {
        background-color: transparent !important;
        height: 0rem !important;
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        visibility: hidden;
    }
    
    /* Main container - multiple selectors */
    .main, .css-k1ih3n {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    /* Sidebar content - enhanced with suggested classes */
    .css-1lcbmhc, .css-1d391kg, section[data-testid="stSidebar"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        font-size: 0.85rem;
        line-height: 1.3;
    }
    
    /* Sidebar inner elements */
    section[data-testid="stSidebar"] > div, 
    .sidebar .sidebar-content,
    .css-1lcbmhc > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    /* App container - comprehensive removal */
    .stApp, .css-1y4p8pa {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
    
    /* Hide Streamlit branding completely */
    #MainMenu, footer, .css-14xtw13 {visibility: hidden;}
    
    /* ========== SIDEBAR FONT SIZE INCREASE ========== */
    /* Increase font size for organization and network selection */
    
    /* Organization selection label - more specific selectors */
    .stSidebar .stSelectbox label,
    .stSidebar .stSelectbox > label,
    .stSidebar .stSelectbox label[data-testid="stSelectboxLabel"],
    .stSidebar .stSelectbox .stMarkdown {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #262730 !important;
    }
    
    /* Network selection label - more specific selectors */
    .stSidebar .stMultiSelect label,
    .stSidebar .stMultiSelect > label,
    .stSidebar .stMultiSelect label[data-testid="stMultiSelectLabel"],
    .stSidebar .stMultiSelect .stMarkdown {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #262730 !important;
    }
    
    /* Selectbox and multiselect input text */
    .stSidebar .stSelectbox > div > div > div,
    .stSidebar .stMultiSelect > div > div > div {
        font-size: 1rem !important;
    }
    
    /* Sidebar headers */
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar text content */
    .stSidebar .stMarkdown {
        font-size: 1.1rem !important;
    }
    
    /* Sidebar buttons */
    .stSidebar .stButton > button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Force all sidebar text to be larger */
    .stSidebar * {
        font-size: 1.1rem !important;
    }
    
    /* Specific targeting for selectbox and multiselect labels */
    .stSidebar div[data-testid="stSelectbox"] label,
    .stSidebar div[data-testid="stMultiSelect"] label {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #262730 !important;
    }
    
    /* ========== FORCE SIDEBAR VISIBILITY ========== */
    /* Force sidebar to always be visible even when closed */
    
    /* Force sidebar to always show */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 300px !important;
        min-width: 300px !important;
    }
    
    /* Force sidebar content to be visible */
    .stSidebar .stMarkdown,
    .stSidebar .stSelectbox,
    .stSidebar .stMultiSelect,
    .stSidebar .stButton {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Ensure sidebar doesn't get hidden */
    .stSidebar {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Force sidebar to stay open */
    .css-1d391kg {
        display: block !important;
        visibility: visible !important;
    }
    
    /* First element in any container */
    .element-container:first-child, 
    .css-1wrcr25:first-child {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    
    /* Force all top-level elements to start from top */
    .css-1wrcr25, .element-container {
        margin-top: 0rem !important;
    }
    
    /* Prevent text truncation in tables and dataframes */
    .dataframe {
        font-size: 0.8rem;
        white-space: nowrap;
        overflow: visible;
    }
    
    /* Ensure long text in cells is not truncated */
    .dataframe td {
        white-space: nowrap;
        overflow: visible;
        text-overflow: unset;
        max-width: none;
    }
    
    /* Optimize metric containers */
    .metric-container {
        font-size: 0.8rem;
    }
    
    /* Optimize chart titles */
    .plotly .gtitle {
        font-size: 1rem !important;
    }
    
    /* Optimize button sizes */
    .stButton > button {
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
    }
    
    /* Optimize selectbox and input sizes */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        font-size: 0.85rem;
    }
    
    /* Optimize expander headers */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
    }
    
    /* Optimize alert containers */
    .alert-container {
        font-size: 0.8rem;
    }
    
    /* Prevent text truncation in client names and MAC addresses */
    .client-name, .mac-address {
        white-space: nowrap;
        overflow: visible;
        text-overflow: unset;
        max-width: none;
        font-size: 0.85rem;
    }
    
    /* Optimize sidebar spacing */
    .sidebar .sidebar-content {
        padding: 1rem 0.5rem;
    }
    
    /* Optimize sidebar header spacing */
    .sidebar .sidebar-content .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Login system with persistent session
SESSION_FILE = Path.home() / ".meraki_dashboard_session.json"

def save_login_session(username):
    """Save login session to file"""
    try:
        session_data = {
            'username': username,
            'logged_in': True,
            'timestamp': datetime.now().isoformat(),
            'token': hashlib.sha256(f"{username}{datetime.now().date()}".encode()).hexdigest()
        }
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f)
        print(f"✅ 세션 저장됨: {SESSION_FILE}")
    except Exception as e:
        print(f"⚠️ 세션 저장 실패: {e}")

def load_login_session():
    """Load login session from file"""
    try:
        if SESSION_FILE.exists():
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is still valid (created today)
            session_date = datetime.fromisoformat(session_data['timestamp']).date()
            if session_date == datetime.now().date():
                print(f"✅ 저장된 세션 복원: {session_data['username']}")
                return session_data
            else:
                print(f"⚠️ 세션 만료됨 (날짜: {session_date})")
                SESSION_FILE.unlink()  # Delete expired session
        return None
    except Exception as e:
        print(f"⚠️ 세션 로드 실패: {e}")
        return None

def clear_login_session():
    """Clear login session file"""
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
            print(f"✅ 세션 삭제됨")
    except Exception as e:
        print(f"⚠️ 세션 삭제 실패: {e}")

def check_login():
    """Check if user is logged in"""
    # First check session state
    if st.session_state.get('logged_in', False):
        return True
    
    # If not in session state, try to load from file
    saved_session = load_login_session()
    if saved_session and saved_session.get('logged_in'):
        # Restore session to session state
        st.session_state.logged_in = True
        st.session_state.username = saved_session.get('username')
        print(f"✅ 자동 로그인: {saved_session.get('username')}")
        return True
    
    return False

def login_page():
    """Display login page"""
    # Create centered container using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Application branding
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;">
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #1f2937; font-size: 2.5rem; font-weight: bold; font-family: Arial, sans-serif;">
                        🌐 Meraki Dashboard
                    </span>
                </div>
                    <p style="color: #666; font-size: 0.9rem; margin: 0; font-family: Arial, sans-serif;">
                    Network Analytics & Management Platform
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        # Login form title and description
        st.markdown(
            '<h2 style="display:inline-block; font-weight:bold;">🌐  Meraki Network Analytics Dashboard</h2>',
            unsafe_allow_html=True
        )
        st.markdown("**로그인하여 네트워크 관리 시스템에 접속하세요**")
        st.markdown("")
        
        with st.form("login_form"):
            st.markdown("#### 🔐 로그인")
            username = st.text_input("사용자명", placeholder="사용자명을 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            
            st.markdown("")
            submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")
        
        if submitted:
            # Load credentials from config
            try:
                from config import LOGIN_USERNAME, LOGIN_PASSWORD
                if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    # Save login session to file for persistence
                    save_login_session(username)
                    st.success("✅ 로그인 성공! 세션이 저장되었습니다.")
                    time.sleep(0.5)  # Brief pause to show success message
                    st.rerun()
                else:
                    st.error("잘못된 사용자명 또는 비밀번호입니다.")
            except ImportError:
                st.error("로그인 설정이 구성되지 않았습니다. config.py 파일을 확인하세요.")
    
    # Add some bottom spacing
    st.markdown("<br><br>", unsafe_allow_html=True)

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    # Clear saved session file
    clear_login_session()
    st.rerun()

# Check login first
if not check_login():
    login_page()
    st.stop()

# Sidebar: Application Logo
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <span style="color: #1f2937; font-size: 1.8rem; font-weight: bold; font-family: Arial, sans-serif;">
        🌐 Meraki Dashboard
    </span>
    <p style="color: #666; margin: 0; font-size: 0.8rem; font-family: Arial, sans-serif;">
        Network Analytics Platform
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Sidebar: User info with clickable logout hyperlink
username = st.session_state.get('username', 'User')

# Create clickable logout using form submission
with st.sidebar:
    # Create a form that submits when the link is clicked
    with st.form(key="logout_form", clear_on_submit=True):
        st.markdown(f"""
        <div style="margin-bottom: 0;">
            <span style="color: #374151; font-weight: 500;">사용자: </span>
            <span style="color: #1f2937; font-weight: 600;">{username}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden submit button that gets triggered by JavaScript
        logout_submitted = st.form_submit_button("🔓로그아웃")
        
        if logout_submitted:
            logout()

# Hide the submit button with CSS and add JavaScript functionality
st.sidebar.markdown("""
<style>
/* Hide the logout form submit button */
form[data-testid="form"] button[kind="formSubmit"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    function setupLogoutClick() {
        // Find the logout text and make it clickable
        const logoutLink = document.getElementById('logout-link');
        if (logoutLink) {
            logoutLink.addEventListener('click', function() {
                // Find and click the hidden submit button
                const form = logoutLink.closest('form');
                if (form) {
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.click();
                    }
                }
            });
        }
    }
    
    // Setup immediately and also after a short delay for dynamic content
    setupLogoutClick();
    setTimeout(setupLogoutClick, 100);
    setTimeout(setupLogoutClick, 500);
});
</script>
""", unsafe_allow_html=True)

# Sidebar: API configuration - Hidden for cleaner UI
# st.sidebar.header("🔑 Meraki API 설정")
# api_key = st.sidebar.text_input("API 키", value=MERAKI_API_KEY, type="password", disabled=True, help="API 키는 config.py에서 로드됩니다")
# st.sidebar.info(f"🔑 API 키 로드됨: {MERAKI_API_KEY[:10]}...{MERAKI_API_KEY[-4:]}")

# Set api_key for internal use (hidden from UI)
api_key = MERAKI_API_KEY

# API Version and Status - Hidden for cleaner UI
# st.sidebar.markdown("### 📡 API Status")
# st.sidebar.success("✅ API v1.62.0 Connected")
# st.sidebar.markdown("**Base URL:** api.meraki.com/api/v1")
# st.sidebar.markdown("**Last Updated:** Sep 3, 2025")
# st.sidebar.markdown("**Authentication:** X-Cisco-Meraki-API-Key")

# API Capabilities - Hidden for cleaner UI
# st.sidebar.markdown("### 🚀 API Capabilities")
# capabilities = [
#     "🌐 Network Management",
#     "📱 Device Configuration", 
#     "🔒 Security Monitoring",
#     "📊 Analytics & Insights",
#     "📶 Wireless Management",
#     "⚡ Automation Tools",
#     "🔧 Bulk Operations",
#     "📈 Performance Monitoring"
# ]
# for cap in capabilities:
#     st.sidebar.markdown(f"• {cap}")
# Sidebar: Navigation
#st.sidebar.header("📊 메뉴")

# Initialize current_page in session state if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "메인화면"

# Navigation options
nav_options = [
    ("📊 메인화면", "메인화면"),
    ("🌐 트래픽 분석", "트래픽 분석"),
    ("👥 클라이언트 분석", "클라이언트 분석"),
    ("🔌 스위치 포트", "스위치 포트"),
    ("🚨 디바이스 상태 알림", "디바이스 상태 알림"),
    ("📄 라이센스 정보", "라이센스 정보")
]

# Create navigation buttons
for icon_name, page_key in nav_options:
    if st.sidebar.button(
        icon_name,
        key=f"nav_{page_key}",
        use_container_width=True,
        type="primary" if st.session_state.current_page == page_key else "secondary"
    ):
        st.session_state.current_page = page_key
        st.rerun()



st.sidebar.markdown("---")

# Sidebar: Analysis settings
st.sidebar.header("📊 분석 설정")
time_ranges = {
    "지난 1시간": 3600,
    "지난 2시간": 7200,
    "지난 24시간": 86400,
    "지난 3일": 259200,
    "지난 1주": 604800,
    "지난 1개월": 2592000
}

# Initialize timespan in session state if not exists
if 'selected_timespan' not in st.session_state:
    st.session_state.selected_timespan = DEFAULT_TIMESPAN if DEFAULT_TIMESPAN in time_ranges else "지난 24시간"

selected_timespan = st.sidebar.selectbox(
    "시간 범위", 
    list(time_ranges.keys()), 
    index=list(time_ranges.keys()).index(st.session_state.selected_timespan),
    key="timespan_selectbox"
)
timespan = time_ranges[selected_timespan]

# Update session state when timespan changes
if selected_timespan != st.session_state.selected_timespan:
    st.session_state.selected_timespan = selected_timespan

resolution_options = {
    "1분 간격": 60,
    "5분 간격": 300,
    "15분 간격": 900,
    "1시간 간격": 3600,
    "1일 간격": 86400
}

# Initialize resolution in session state if not exists
if 'selected_resolution' not in st.session_state:
    st.session_state.selected_resolution = DEFAULT_RESOLUTION if DEFAULT_RESOLUTION in resolution_options else "5분 간격"

selected_resolution = st.sidebar.selectbox(
    "데이터 수집 간격", 
    list(resolution_options.keys()), 
    index=list(resolution_options.keys()).index(st.session_state.selected_resolution),
    key="resolution_selectbox"
)
resolution = resolution_options[selected_resolution]

# Update session state when resolution changes
if selected_resolution != st.session_state.selected_resolution:
    st.session_state.selected_resolution = selected_resolution

st.sidebar.markdown("---")

# Real-time data load time tracking in sidebar
from datetime import datetime

# Initialize data load time in session state if not exists
if 'data_load_time' not in st.session_state:
    st.session_state.data_load_time = datetime.now()

# Calculate elapsed time since data was loaded
current_time = datetime.now()
elapsed_time = current_time - st.session_state.data_load_time

# Format elapsed time - always HH:MM:SS format
total_seconds = int(elapsed_time.total_seconds())
hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

# Always display in HH:MM:SS format
elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Color coding based on elapsed time
if total_seconds > 300:  # 5 minutes
    delta_color = "inverse"
    status_text = "새로고침 권장"
elif total_seconds > 180:  # 3 minutes
    delta_color = "normal"
    status_text = "정상"
else:
    delta_color = "normal"
    status_text = "최신"

# Get the initial elapsed time for JavaScript
initial_elapsed = (datetime.now() - st.session_state.data_load_time).total_seconds()

# Display elapsed time in sidebar with real-time update
st.sidebar.markdown("### ⏱️ 데이터 경과시간")

# JavaScript-based real-time counter for sidebar
st.sidebar.markdown(f"""
<script>
// Store the initial elapsed time when page loads
let initialElapsed = {initial_elapsed};
let startTime = new Date().getTime() / 1000;

function updateSidebarTimer() {{
    // Calculate current elapsed time
    let currentTime = new Date().getTime() / 1000;
    let totalElapsed = initialElapsed + (currentTime - startTime);
    
    // Format as HH:MM:SS
    let hours = Math.floor(totalElapsed / 3600);
    let minutes = Math.floor((totalElapsed % 3600) / 60);
    let seconds = Math.floor(totalElapsed % 60);
    
    let timeStr = String(hours).padStart(2, '0') + ':' + 
                 String(minutes).padStart(2, '0') + ':' + 
                 String(seconds).padStart(2, '0');
    
    // Update the sidebar timer display
    let sidebarTimerElement = document.getElementById('sidebar-elapsed-timer');
    if (sidebarTimerElement) {{
        sidebarTimerElement.textContent = timeStr;
    }}
    
    // Update status based on elapsed time
    let statusElement = document.getElementById('sidebar-timer-status');
    if (statusElement) {{
        if (totalElapsed > 300) {{
            statusElement.textContent = '새로고침 권장';
            statusElement.style.color = '#dc2626';
        }} else if (totalElapsed > 180) {{
            statusElement.textContent = '정상';
            statusElement.style.color = '#059669';
        }} else {{
            statusElement.textContent = '최신';
            statusElement.style.color = '#059669';
        }}
    }}
}}

// Update timer every second
setInterval(updateSidebarTimer, 1000);

// Update immediately
updateSidebarTimer();
</script>

<div style="text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e5e7eb;">
    <div id="sidebar-elapsed-timer" style="font-size: 1.5rem; font-weight: 700; color: #1f2937; margin-bottom: 5px;">{elapsed_str}</div>
    <div id="sidebar-timer-status" style="font-size: 0.8rem; font-weight: 500;">{status_text}</div>
</div>
""", unsafe_allow_html=True)
# Sidebar: Feature toggles (hidden)
enable_traffic = True
enable_clients = True
enable_switch_ports = True
enable_bandwidth = True
enable_alerts = True

# Initialize API
@st.cache_resource
def init_api(key):
    if not key:
        return None
    try:
        return meraki.DashboardAPI(key, suppress_logging=True)
    except Exception as e:
        st.error(f"Failed to initialize Meraki API: {e}")
        return None

# Parallel processing helper functions
def suppress_streamlit_warnings():
    """Suppress Streamlit warnings in parallel threads"""
    import warnings
    import logging
    
    # Suppress specific warnings
    warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")
    warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="streamlit")
    
    # Suppress logging warnings
    logging.getLogger("streamlit.runtime.scriptrunner.script_runner").setLevel(logging.ERROR)
    logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)

def safe_api_call(func, *args, **kwargs):
    """Safely execute API call with error handling"""
    try:
        # Setup thread-specific warning suppression
        setup_thread_warnings()
        suppress_streamlit_warnings()
        return func(*args, **kwargs)
    except Exception as e:
        if SHOW_DEBUG_INFO:
            print(f"API call failed: {func.__name__} - {e}")
        return None

def parallel_api_calls(api_calls, max_workers=100):  # EXTREME workers for 10-second target
    """Execute multiple API calls in parallel with EXTREME worker count for 10-second target"""
    results = {}
    
    # Suppress warnings at the start of parallel execution
    suppress_streamlit_warnings()
    
    # EXTREME optimize worker count for 10-second target
    if len(api_calls) < max_workers:
        max_workers = len(api_calls)
    
    # EXTREME max workers for fastest processing
    max_workers = min(max_workers, 200)  # Increased to 200 for maximum speed
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_key = {
            executor.submit(safe_api_call, call['func'], *call.get('args', []), **call.get('kwargs', {})): call['key']
            for call in api_calls
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                result = future.result()
                results[key] = result
            except Exception as e:
                if SHOW_DEBUG_INFO:
                    print(f"Failed to get result for {key}: {e}")
                results[key] = None
    
    return results

def parallel_data_loading(load_functions, api_key, **common_params):
    """Load multiple data types in parallel"""
    api_calls = []
    
    for func_name, func in load_functions.items():
        # Prepare function arguments
        args = [api_key]
        if 'org_id' in common_params:
            args.append(common_params['org_id'])
        if 'network_id' in common_params:
            args.append(common_params['network_id'])
        if 'timespan' in common_params:
            args.append(common_params['timespan'])
        if 'resolution' in common_params:
            args.append(common_params['resolution'])
        
        api_calls.append({
            'key': func_name,
            'func': func,
            'args': args
        })
    
    return parallel_api_calls(api_calls)


# Get all organizations without filtering (filtering will be done at network level)
@st.cache_data(ttl=300, show_spinner="조직 정보 로딩 중...")  # Cache for 5 minutes
def get_all_organizations(key):
    """Get list of all organizations without filtering"""
    try:
        from datetime import datetime
        
        print("=" * 60)
        print("LOADING ALL ORGANIZATIONS (NO FILTERING)")
        print("=" * 60)
        
        start_time = datetime.now()
        
        api = init_api(key)
        if not api:
            print("❌ Failed to initialize API")
            print("=" * 60)
            # Don't cache failed results
            raise Exception("Failed to initialize Meraki API")
        
        # Get all organizations
        print("📋 Getting all organizations...")
        print(f"🔑 API Key: {key[:10]}...{key[-4:]}")
        
        try:
            organizations = api.organizations.getOrganizations()
            print(f"📊 Found {len(organizations)} total organizations")
            
            if not organizations or len(organizations) == 0:
                print("❌ No organizations returned from API")
                print("=" * 60)
                # Don't cache empty results
                raise Exception("No organizations found - API returned empty list")
                
        except Exception as api_error:
            print(f"❌ API Call Failed: {str(api_error)}")
            print(f"❌ Error Type: {type(api_error).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            print("=" * 60)
            # Re-raise to prevent caching
            raise
        
        # Convert to simple list format
        org_list = []
        for org in organizations:
            org_list.append({
                'id': org.get('id'),
                'name': org.get('name', 'Unknown')
            })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("ORGANIZATION LOADING SUMMARY")
        print("=" * 60)
        print(f"Total organizations: {len(org_list)}")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print("=" * 60)
        
        return org_list
        
    except Exception as e:
        print(f"💥 Error in get_all_organizations: {e}")
        print(f"💥 Error Type: {type(e).__name__}")
        import traceback
        print(f"💥 Full Traceback:")
        print(traceback.format_exc())
        print("=" * 60)
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to get organizations: {e}")
        # Re-raise to prevent caching failed results
        raise


# Load all organizations (no filtering at organization level) - Optimized for speed
@st.cache_data(ttl=300, show_spinner="조직 목록 로딩 중...")  # Reduced TTL
def load_orgs(key):
    """Load all organizations - filtering will be done at network level"""
    try:
        print("=" * 60)
        print("LOADING ORGANIZATIONS (NO FILTERING)")
        print("=" * 60)
        
        # Get all organizations
        all_orgs = get_all_organizations(key)
        
        print(f"📋 Final organization list: {len(all_orgs)} organizations")
        for i, org in enumerate(all_orgs, 1):
            print(f"  {i}. {org['name']} ({org['id']})")
        
        print("=" * 60)
        return all_orgs
    except Exception as e:
        print(f"💥 Error in load_orgs: {e}")
        print("=" * 60)
        st.error(f"Failed to load organizations: {e}")
        # Re-raise to prevent caching
        raise

# Ultra-fast critical data loading for immediate display
@st.cache_data(ttl=15, show_spinner="중요 데이터 로딩 중...")  # Ultra-short TTL
def load_critical_data_fast(key, org_id):
    """Load only critical data for immediate display"""
    try:
        print("🚀 Loading critical data for immediate display...")
        start_time = datetime.now()
        
        # Load only the most essential data
        devices = load_devices(key, org_id)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⚡ Critical data loaded in {duration:.2f} seconds")
        return devices
        
    except Exception as e:
        print(f"💥 Error loading critical data: {e}")
        return []

# EXTREME SPEED: Minimal data loading for 10-second target
@st.cache_data(ttl=5, show_spinner="초고속 로딩 중...")  # Ultra-minimal TTL
def load_dashboard_data_parallel(key, org_id, network_ids, timespan, resolution):
    """Load ONLY essential data for 10-second target"""
    try:
        print("=" * 60)
        print("EXTREME SPEED LOADING - 10 SECOND TARGET")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # ONLY load absolutely essential data - NO optional data
        essential_functions = {
            'devices': load_devices
            # Removed ALL other functions for maximum speed
        }
        
        # Load ONLY essential data
        print("🚀 Loading ONLY essential data...")
        org_results = parallel_data_loading(essential_functions, key, org_id=org_id)
        
        # Skip network data loading for speed - only load if absolutely necessary
        network_results = {}
        for network_id in network_ids:
            network_results[network_id] = {
                'clients_overview': {},
                'clients': [],
                'traffic': {},
                'bandwidth': [],
                'limits': [],
                'wan_bandwidth': []
            }
        
        # Skip switch ports for speed
        switch_ports = {}
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⚡ EXTREME SPEED loading completed in {duration:.2f} seconds")
        print(f"📊 Performance: {len(network_ids)} networks, {len(essential_functions)} essential functions")
        print(f"🎯 Target: 10 seconds | Actual: {duration:.2f} seconds | {'✅ SUCCESS' if duration <= 10 else '❌ NEEDS OPTIMIZATION'}")
        print("=" * 60)
        
        return {
            'org_data': org_results,
            'network_data': network_results,
            'switch_ports': switch_ports,
            'load_time': duration,
            'performance_metrics': {
                'networks_processed': len(network_ids),
                'essential_functions_processed': len(essential_functions),
                'total_api_calls': len(essential_functions),  # Only 1 API call!
                'avg_time_per_call': duration / len(essential_functions) if len(essential_functions) > 0 else 0
            }
        }
        
    except Exception as e:
        print(f"💥 Error in extreme speed loading: {e}")
        print("=" * 60)
        st.error(f"Failed to load dashboard data: {e}")
        return {
            'org_data': {},
            'network_data': {},
            'switch_ports': {},
            'load_time': 0,
            'performance_metrics': {}
        }

# Load organization licensing entitlements
@st.cache_data(ttl=3600)
def load_licensing_entitlements(key):
    """Load available licensing entitlements"""
    try:
        api = init_api(key)
        if not api:
            return []
        
        entitlements = api.organizations.getOrganizationLicensingSubscriptionEntitlements()
        return entitlements
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.write(f"Could not load licensing entitlements: {e}")
        return []

# Load organization subscriptions
@st.cache_data(ttl=3600)
def load_licensing_subscriptions(key):
    """Load organization subscriptions"""
    try:
        api = init_api(key)
        if not api:
            return []
        
        subscriptions = api.organizations.getOrganizationLicensingSubscriptionSubscriptions()
        return subscriptions
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.write(f"Could not load subscriptions: {e}")
        return []

# Load networks without filtering
@st.cache_data(ttl=300)
def load_networks(key, org_id):
    """Load all networks without filtering"""
    try:
        print("=" * 60)
        print("NETWORK LOADING PROCESS START (NO FILTERING)")
        print("=" * 60)
        
        api = init_api(key)
        if not api:
            print("❌ Failed to initialize API")
            print("=" * 60)
            return []
        
        # Get all networks
        print("📋 Getting all networks...")
        all_networks = api.organizations.getOrganizationNetworks(org_id)
        print(f"📊 Found {len(all_networks)} total networks")
        
        print("\n" + "=" * 60)
        print("NETWORK LOADING SUMMARY (NO FILTERING)")
        print("=" * 60)
        print(f"Total networks: {len(all_networks)}")
        print("=" * 60)
        
        return all_networks
        
    except Exception as e:
        print(f"💥 Error in load_networks: {e}")
        print("=" * 60)
        st.error(f"Failed to load networks: {e}")
        return []

# Load device statuses with full pagination support
@st.cache_data(ttl=180)
def load_devices(key, org_id):
    try:
        api = init_api(key)
        if not api:
            return []
        
        all_devices = []
        
        # First request with perPage=1000 (maximum allowed)
        devices = api.organizations.getOrganizationDevicesStatuses(org_id, perPage=1000)
        all_devices.extend(devices)
        
        # If we got exactly 1000 devices, there might be more - implement pagination
        while len(devices) == 1000:
            try:
                # Get next page using the last device as starting point
                last_device_serial = devices[-1].get('serial', '')
                devices = api.organizations.getOrganizationDevicesStatuses(
                    org_id, 
                    perPage=1000,
                    startingAfter=last_device_serial
                )
                if devices:
                    all_devices.extend(devices)
                else:
                    break
            except Exception as pagination_error:
                # If pagination fails, just use what we have
                if SHOW_DEBUG_INFO:
                    st.warning(f"Pagination failed, using {len(all_devices)} devices: {pagination_error}")
                break
        
        if SHOW_DEBUG_INFO:
            st.info(f"Loaded {len(all_devices)} total devices from organization")
        
        return all_devices
        
    except Exception as e:
        st.error(f"Failed to load devices: {e}")
        return []

# ULTRA-FAST device details loading - optimized for speed
@st.cache_data(ttl=60)  # Reduced TTL for faster updates
def load_device_details(key, org_id):
    """Load device details with minimal API calls for maximum speed"""
    try:
        print("🚀 ULTRA-FAST device details loading...")
        start_time = datetime.now()
        
        api = init_api(key)
        if not api:
            return []
        
        # ONLY get device statuses (includes most essential info)
        # Skip getOrganizationDevices call to save time
        device_statuses = api.organizations.getOrganizationDevicesStatuses(org_id, perPage=1000)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⚡ Device details loaded in {duration:.2f} seconds ({len(device_statuses)} devices)")
        
        return device_statuses
    except Exception as e:
        print(f"💥 Error loading device details: {e}")
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load device details: {e}")
        return []

# ULTRA-FAST device firmware loading - optimized for speed
@st.cache_data(ttl=300)  # Reduced TTL for faster updates
def load_device_firmware(key, org_id):
    """Load device firmware information with minimal API calls"""
    try:
        print("🚀 ULTRA-FAST firmware loading...")
        start_time = datetime.now()
        
        api = init_api(key)
        if not api:
            return {}
        
        # Get firmware information for all devices
        firmware_info = api.organizations.getOrganizationFirmwareUpgrades(org_id)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⚡ Firmware loaded in {duration:.2f} seconds")
        
        return firmware_info
    except Exception as e:
        print(f"💥 Error loading firmware: {e}")
        if SHOW_DEBUG_INFO:
            st.write(f"Could not load firmware info: {e}")
        return {}

# Load device performance metrics
@st.cache_data(ttl=300)
def load_device_performance(key, org_id, device_serial):
    """Load performance metrics for a specific device"""
    try:
        api = init_api(key)
        if not api:
            return {}
        
        # Get device performance data
        performance = api.organizations.getOrganizationDevicesUplinksLossAndLatency(
            organizationId=org_id,
            serials=[device_serial],
            timespan=3600  # Last hour
        )
        return performance
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.write(f"Could not load performance for {device_serial}: {e}")
        return {}

# Load network traffic data - Using actual Meraki API endpoints
@st.cache_data(ttl=300)
def load_traffic(key, network_id, timespan):
    """Load network traffic data using actual Meraki API"""
    try:
        api = init_api(key)
        if api:
            # Use the actual Meraki API endpoint for network traffic
            return api.networks.getNetworkTraffic(network_id, timespan=timespan)
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load traffic data: {e}")
        return []

# Load comprehensive traffic data from all device types
@st.cache_data(ttl=300)
def load_comprehensive_traffic(key, network_id, timespan):
    """Load traffic data from all device types and combine them"""
    try:
        api = init_api(key)
        if not api:
            return {}
        
        # Check if timespan exceeds Meraki API limits (30 days = 2592000 seconds)
        max_timespan = 2592000  # 30 days in seconds
        if timespan > max_timespan:
            if SHOW_DEBUG_INFO:
                st.warning(f"⚠️ 요청된 시간 범위({timespan/86400:.1f}일)가 Meraki API 최대 제한(30일)을 초과합니다. 30일로 제한합니다.")
            timespan = max_timespan
        
        device_types = ['combined', 'wireless', 'switch', 'appliance']
        traffic_data = {}
        
        for device_type in device_types:
            try:
                # Get traffic data for each device type
                data = api.networks.getNetworkTraffic(
                    network_id, 
                    timespan=timespan,
                    deviceType=device_type
                )
                traffic_data[device_type] = data if data else []
                
                if SHOW_DEBUG_INFO:
                    st.write(f"📊 {device_type.upper()}: {len(data) if data else 0} applications")
                    
            except Exception as e:
                if SHOW_DEBUG_INFO:
                    st.error(f"Failed to load {device_type} traffic: {e}")
                traffic_data[device_type] = []
        
        # If no data from any device type, try alternative approach
        if not any(traffic_data.values()):
            if SHOW_DEBUG_INFO:
                st.warning("⚠️ 모든 디바이스 타입에서 데이터를 가져올 수 없습니다. 대체 방법을 시도합니다.")
            
            # Try with shorter timespan for 30-day requests
            if timespan >= 2592000:  # 30 days
                shorter_timespan = 604800  # 7 days
                if SHOW_DEBUG_INFO:
                    st.info(f"🔄 7일 데이터로 재시도합니다...")
                
                for device_type in device_types:
                    try:
                        data = api.networks.getNetworkTraffic(
                            network_id, 
                            timespan=shorter_timespan,
                            deviceType=device_type
                        )
                        traffic_data[device_type] = data if data else []
                        
                        if SHOW_DEBUG_INFO:
                            st.write(f"📊 {device_type.upper()} (7일): {len(data) if data else 0} applications")
                            
                    except Exception as e:
                        if SHOW_DEBUG_INFO:
                            st.error(f"Failed to load {device_type} traffic (7일): {e}")
                        traffic_data[device_type] = []
        
        return traffic_data
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load comprehensive traffic data: {e}")
        return {}

# Parallel traffic analysis data loading - Ultra-fast TTL
@st.cache_data(ttl=10, show_spinner="트래픽 데이터 로딩 중...")
def load_traffic_analysis_data_parallel(key, network_ids, timespan, resolution):
    """Load all traffic analysis data in parallel"""
    try:
        print("=" * 60)
        print("PARALLEL TRAFFIC ANALYSIS DATA LOADING START")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Prepare API calls for all networks
        api_calls = []
        
        for network_id in network_ids:
            # Traffic data calls
            api_calls.extend([
                {
                    'key': f'traffic_{network_id}',
                    'func': load_comprehensive_traffic,
                    'args': [key, network_id, timespan]
                },
                {
                    'key': f'app_traffic_{network_id}',
                    'func': load_app_traffic,
                    'args': [key, network_id, timespan]
                },
                {
                    'key': f'bandwidth_{network_id}',
                    'func': load_net_bw,
                    'args': [key, network_id, timespan, resolution]
                },
                {
                    'key': f'wan_bandwidth_{network_id}',
                    'func': load_wan_bandwidth,
                    'args': [key, network_id, timespan, resolution]
                },
                {
                    'key': f'limits_{network_id}',
                    'func': load_limits,
                    'args': [key, network_id]
                }
            ])
        
        # Execute all calls in parallel with maximum workers for speed
        results = parallel_api_calls(api_calls, max_workers=100)
        
        # Organize results by network
        organized_results = {}
        for network_id in network_ids:
            organized_results[network_id] = {
                'traffic': results.get(f'traffic_{network_id}', {}),
                'app_traffic': results.get(f'app_traffic_{network_id}', []),
                'bandwidth': results.get(f'bandwidth_{network_id}', []),
                'wan_bandwidth': results.get(f'wan_bandwidth_{network_id}', []),
                'limits': results.get(f'limits_{network_id}', [])
            }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Traffic analysis parallel loading completed in {duration:.2f} seconds")
        print("=" * 60)
        
        return {
            'network_data': organized_results,
            'load_time': duration
        }
        
    except Exception as e:
        print(f"💥 Error in parallel traffic analysis loading: {e}")
        print("=" * 60)
        st.error(f"Failed to load traffic analysis data: {e}")
        return {
            'network_data': {},
            'load_time': 0
        }

# Combine traffic data from all device types
def combine_traffic_data(traffic_data):
    """Combine traffic data from all device types into a single dataset"""
    if not traffic_data:
        return pd.DataFrame()

    combined_data = []

    for device_type, data in traffic_data.items():
        if data:
            for item in data:
                # Add device type to each item
                item_copy = item.copy()
                item_copy['deviceType'] = device_type
                combined_data.append(item_copy)

    if not combined_data:
        return pd.DataFrame()

    try:
        # Convert to DataFrame and aggregate by application
        df = pd.DataFrame(combined_data)
        
        # Check if we have the required columns
        required_columns = ['application', 'sent', 'recv', 'numClients']
        if not all(col in df.columns for col in required_columns):
            return pd.DataFrame()
        
        # Group by application and sum the values with error handling
        agg_dict = {
            'sent': 'sum',
            'recv': 'sum', 
            'numClients': 'sum'
        }
        
        if 'activeTime' in df.columns:
            agg_dict['activeTime'] = 'sum'
        if 'flows' in df.columns:
            agg_dict['flows'] = 'sum'
        if 'deviceType' in df.columns:
            agg_dict['deviceType'] = lambda x: ', '.join(sorted([str(v) for v in x.unique() if v is not None and str(v) != 'nan']))
        if 'protocol' in df.columns:
            agg_dict['protocol'] = lambda x: ', '.join(sorted([str(v) for v in x.unique() if v is not None and str(v) != 'nan']))
        if 'port' in df.columns:
            agg_dict['port'] = lambda x: ', '.join(map(str, sorted([v for v in x.unique() if v is not None and str(v) != 'nan'])))
        if 'destination' in df.columns:
            agg_dict['destination'] = lambda x: ', '.join(sorted([str(v) for v in x.unique() if v is not None and str(v) != 'nan']))
        
        aggregated = df.groupby('application').agg(agg_dict).reset_index()
        
        return aggregated
        
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Error in combine_traffic_data: {e}")
        return pd.DataFrame()

# Load network bandwidth usage history
@st.cache_data(ttl=300)
def load_network_bandwidth(key, network_id, timespan):
    """Load network bandwidth usage history"""
    try:
        api = init_api(key)
        if api:
            # Use network bandwidth usage history API
            return api.networks.getNetworkClientsBandwidthUsageHistory(
                network_id, 
                timespan=timespan, 
                resolution=300  # 5-minute resolution
            )
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load bandwidth data: {e}")
        return []

# Load application traffic (separate function for app-specific analysis)
@st.cache_data(ttl=300)
def load_app_traffic(key, network_id, timespan):
    """Load application-specific traffic data"""
    try:
        api = init_api(key)
        if api:
            return api.networks.getNetworkTraffic(network_id, timespan=timespan)
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load application traffic data: {e}")
        return []

# Load network clients with usage data
@st.cache_data(ttl=300)
def load_network_clients(key, network_id):
    """Load network clients with usage information - fetches all clients (up to 5000)"""
    try:
        api = init_api(key)
        if api:
            # Use perPage=5000 to get all clients instead of default 10
            return api.networks.getNetworkClients(network_id, perPage=5000)
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load network clients: {e}")
        return []

# Parallel client analysis data loading - Ultra-fast TTL
@st.cache_data(ttl=10, show_spinner="클라이언트 데이터 로딩 중...")
def load_client_analysis_data_parallel(key, network_ids, timespan, resolution):
    """Load all client analysis data in parallel"""
    try:
        print("=" * 60)
        print("PARALLEL CLIENT ANALYSIS DATA LOADING START")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Prepare API calls for all networks
        api_calls = []
        
        for network_id in network_ids:
            # Client data calls
            api_calls.extend([
                {
                    'key': f'clients_{network_id}',
                    'func': load_network_clients,
                    'args': [key, network_id]
                },
                {
                    'key': f'clients_overview_{network_id}',
                    'func': load_network_clients_overview,
                    'args': [key, network_id]
                },
                {
                    'key': f'bandwidth_{network_id}',
                    'func': load_net_bw,
                    'args': [key, network_id, timespan, resolution]
                }
            ])
        
        # Execute all calls in parallel with maximum workers for speed
        results = parallel_api_calls(api_calls, max_workers=100)
        
        # Organize results by network
        organized_results = {}
        for network_id in network_ids:
            organized_results[network_id] = {
                'clients': results.get(f'clients_{network_id}', []),
                'clients_overview': results.get(f'clients_overview_{network_id}', {}),
                'bandwidth': results.get(f'bandwidth_{network_id}', [])
            }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Client analysis parallel loading completed in {duration:.2f} seconds")
        print("=" * 60)
        
        return {
            'network_data': organized_results,
            'load_time': duration
        }
        
    except Exception as e:
        print(f"💥 Error in parallel client analysis loading: {e}")
        print("=" * 60)
        st.error(f"Failed to load client analysis data: {e}")
        return {
            'network_data': {},
            'load_time': 0
        }

# Load network clients overview for total count
@st.cache_data(ttl=300)
def load_network_clients_overview(key, network_id):
    """Load network clients overview for total count and summary"""
    try:
        api = init_api(key)
        if api:
            return api.networks.getNetworkClientsOverview(network_id)
        return {}
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load network clients overview: {e}")
        return {}

# Load network bandwidth history
@st.cache_data(ttl=300)
def load_net_bw(key, network_id, timespan, resolution):
    try:
        api = init_api(key)
        if api:
            return api.networks.getNetworkClientsBandwidthUsageHistory(
                network_id, timespan=timespan, resolution=resolution
            )
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load bandwidth data: {e}")
        return []

# Load traffic shaping limits
@st.cache_data(ttl=300)
def load_limits(key, network_id):
    try:
        api = init_api(key)
        if api:
            return api.networks.getNetworkApplianceTrafficShapingUplinkBandwidth(network_id)
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load traffic limits: {e}")
        return []

# Load switch port data
@st.cache_data(ttl=300)
def load_switch_ports(key, org_id):
    try:
        dash = init_api(key)
        if not dash:
            return {}
        
        devices = dash.organizations.getOrganizationDevices(org_id)
        switches = [d for d in devices if d.get("productType") == "switch"]
        out = {}
        
        for sw in switches:
            try:
                ports = dash.switch.getDeviceSwitchPorts(sw["serial"])
                statuses = dash.switch.getDeviceSwitchPortsStatuses(sw["serial"])
                combined = []
                
                for p in ports:
                    sid = p["portId"]
                    info = next((s for s in statuses if s["portId"] == sid), {})
                    combined.append({**p, **info})
                
                out[sw["name"]] = combined
            except Exception as e:
                if SHOW_DEBUG_INFO:
                    st.warning(f"Failed to load ports for switch {sw['name']}: {e}")
                continue
                
        return out
    except Exception as e:
        st.error(f"Failed to load switch ports: {e}")
        return {}

# Load WAN uplink bandwidth data
@st.cache_data(ttl=300)
def load_wan_bandwidth(key, network_id, timespan, resolution):
    try:
        api = init_api(key)
        if not api:
            return []
        
        # Get WAN uplink bandwidth data
        bandwidth_data = api.networks.getNetworkUplinkBandwidthUsage(network_id, timespan=timespan, resolution=resolution)
        
        if SHOW_DEBUG_INFO:
            st.write(f"🔍 Debug: Bandwidth Data Structure")
            st.write(f"Data entries: {len(bandwidth_data)}")
            if bandwidth_data:
                st.write(f"First entry structure: {list(bandwidth_data[0].keys())}")
        
        return bandwidth_data
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load WAN bandwidth data: {e}")
        return []

# Load device status events and alerts
@st.cache_data(ttl=300)
def load_device_alerts(key, org_id, device_serial, timespan=86400):
    """Load detailed alert information for a specific device"""
    try:
        api = init_api(key)
        if not api:
            return {}
        
        alerts = {}
        
        # Get device status events (last 24 hours by default)
        try:
            events = api.organizations.getOrganizationDevicesStatusesHistory(
                organizationId=org_id,
                serials=[device_serial],
                timespan=timespan
            )
            if events:
                alerts['status_events'] = events
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load status events: {e}")
        
        # Get device performance metrics
        try:
            performance = api.organizations.getOrganizationDevicesUplinksLossAndLatency(
                organizationId=org_id,
                serials=[device_serial],
                timespan=timespan
            )
            if performance:
                alerts['performance'] = performance
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load performance data: {e}")
        
        # Get device security events (if available)
        try:
            security = api.organizations.getOrganizationDevicesSecurityEvents(
                organizationId=org_id,
                serials=[device_serial],
            )
            if security:
                alerts['security'] = security
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load security events: {e}")
        
        return alerts
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load device alerts: {e}")
        return {}

# Parallel device alerts data loading - Ultra-fast TTL
@st.cache_data(ttl=10, show_spinner="디바이스 알림 데이터 로딩 중...")
def load_device_alerts_data_parallel(key, org_id, device_serials, timespan=86400):
    """Load device alerts data for multiple devices in parallel"""
    try:
        print("=" * 60)
        print("PARALLEL DEVICE ALERTS DATA LOADING START")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Prepare API calls for all devices
        api_calls = []
        
        for device_serial in device_serials:
            # Device-specific alert calls
            api_calls.extend([
                {
                    'key': f'status_events_{device_serial}',
                    'func': lambda api, org_id, serial, timespan: api.organizations.getOrganizationDevicesStatusesHistory(
                        organizationId=org_id,
                        serials=[serial],
                        timespan=timespan
                    ),
                    'args': [key, org_id, device_serial, timespan]
                },
                {
                    'key': f'performance_{device_serial}',
                    'func': lambda api, org_id, serial, timespan: api.organizations.getOrganizationDevicesUplinksLossAndLatency(
                        organizationId=org_id,
                        serials=[serial],
                        timespan=timespan
                    ),
                    'args': [key, org_id, device_serial, timespan]
                },
                {
                    'key': f'security_{device_serial}',
                    'func': lambda api, org_id, serial: api.organizations.getOrganizationDevicesSecurityEvents(
                        organizationId=org_id,
                        serials=[serial]
                    ),
                    'args': [key, org_id, device_serial]
                }
            ])
        
        # Execute all calls in parallel with maximum workers for speed
        results = parallel_api_calls(api_calls, max_workers=100)
        
        # Organize results by device
        organized_results = {}
        for device_serial in device_serials:
            organized_results[device_serial] = {
                'status_events': results.get(f'status_events_{device_serial}', []),
                'performance': results.get(f'performance_{device_serial}', []),
                'security': results.get(f'security_{device_serial}', [])
            }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Device alerts parallel loading completed in {duration:.2f} seconds")
        print("=" * 60)
        
        return {
            'device_data': organized_results,
            'load_time': duration
        }
        
    except Exception as e:
        print(f"💥 Error in parallel device alerts loading: {e}")
        print("=" * 60)
        st.error(f"Failed to load device alerts data: {e}")
        return {
            'device_data': {},
            'load_time': 0
        }

# Load organization configuration changes
@st.cache_data(ttl=300)
def load_configuration_changes(key, org_id, per_page=100):
    """Load organization configuration changes"""
    try:
        api = init_api(key)
        if not api:
            return {}
        
        # Get configuration changes
        try:
            changes = api.organizations.getOrganizationConfigurationChanges(
                organizationId=org_id,
                perPage=per_page
            )
            return changes
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load configuration changes: {e}")
            return {}
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load configuration changes: {e}")
        return {}

# Load organization license overview - Enhanced with better error handling
@st.cache_data(ttl=60)  # Reduced TTL for faster updates
def load_license_overview(key, org_id):
    """Load organization license overview with enhanced error handling"""
    try:
        print("=" * 60)
        print("LICENSE OVERVIEW LOADING START")
        print("=" * 60)
        print(f"Organization ID: {org_id}")
        
        api = init_api(key)
        if not api:
            print("❌ Failed to initialize API")
            return {}
        
        # Try multiple API endpoints for license information
        license_data = {}
        
        # Method 1: Try getOrganizationLicensesOverview
        try:
            print("🔍 Trying getOrganizationLicensesOverview...")
            overview = api.organizations.getOrganizationLicensesOverview(organizationId=org_id)
            if overview:
                license_data.update(overview)
                print("✅ getOrganizationLicensesOverview successful")
            else:
                print("⚠️ getOrganizationLicensesOverview returned empty")
        except Exception as e:
            print(f"❌ getOrganizationLicensesOverview failed: {e}")
        
        # Method 2: Try getOrganizationLicensingCotermLicenses
        try:
            print("🔍 Trying getOrganizationLicensingCotermLicenses...")
            coterm_licenses = api.organizations.getOrganizationLicensingCotermLicenses(organizationId=org_id)
            if coterm_licenses:
                license_data['coterm_licenses'] = coterm_licenses
                print("✅ getOrganizationLicensingCotermLicenses successful")
            else:
                print("⚠️ getOrganizationLicensingCotermLicenses returned empty")
        except Exception as e:
            print(f"❌ getOrganizationLicensingCotermLicenses failed: {e}")
        
        # Method 3: Try getOrganizationLicensingCotermLicensesOverview
        try:
            print("🔍 Trying getOrganizationLicensingCotermLicensesOverview...")
            coterm_overview = api.organizations.getOrganizationLicensingCotermLicensesOverview(organizationId=org_id)
            if coterm_overview:
                license_data.update(coterm_overview)
                print("✅ getOrganizationLicensingCotermLicensesOverview successful")
            else:
                print("⚠️ getOrganizationLicensingCotermLicensesOverview returned empty")
        except Exception as e:
            print(f"❌ getOrganizationLicensingCotermLicensesOverview failed: {e}")
        
        print("=" * 60)
        print("LICENSE OVERVIEW LOADING COMPLETE")
        print("=" * 60)
        print(f"Final license data: {license_data}")
        print("=" * 60)
        
        return license_data
        
    except Exception as e:
        print(f"💥 Error in load_license_overview: {e}")
        print("=" * 60)
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load license overview: {e}")
        return {}


# Helper function to parse date format
def parse_date(date_string):
    """Parse ISO 8601 date string and return readable format"""
    if not date_string or date_string == 'N/A':
        return 'N/A'
    
    try:
        from datetime import datetime
        # Parse ISO 8601 format (2016-01-07T20:35:14Z)
        if 'T' in date_string and date_string.endswith('Z'):
            # Remove Z and parse
            date_string = date_string[:-1]
            dt = datetime.fromisoformat(date_string)
            # Return formatted date (YYYY-MM-DD HH:MM:SS)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return date_string
    except Exception:
        return date_string

# Load organization detailed licenses
@st.cache_data(ttl=300)
def load_detailed_licenses(key, org_id, per_page=100):
    """Load organization detailed license information"""
    try:
        api = init_api(key)
        if not api:
            return []
        
        # Get detailed licenses using direct HTTP request
        try:
            import requests
            
            # API endpoint and headers
            url = f"https://api.meraki.com/api/v1/organizations/{org_id}/licensing/coterm/licenses"
            headers = {
                'X-Cisco-Meraki-API-Key': key,
                'Accept': 'application/json'
            }
            params = {
                'perPage': per_page
            }
            
            # CLI Debug output for API call
            print("=" * 50)
            print("LICENSE API CALL DEBUG")
            print("=" * 50)
            print(f"API URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print("=" * 50)
            
            # Make HTTP request
            response = requests.get(url, headers=headers, params=params)
            
            # CLI Debug output for response
            print("=" * 50)
            print("LICENSE API RESPONSE DEBUG")
            print("=" * 50)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Type: {type(response.json()) if response.status_code == 200 else 'Error'}")
            
            if response.status_code == 200:
                licenses = response.json()
                print(f"Response Length: {len(licenses) if licenses else 'None'}")
                print("\nFull API Response:")
                print(licenses)
                print("=" * 50)
                return licenses
            else:
                print(f"Error Response: {response.text}")
                print("=" * 50)
                return []
                
        except Exception as e:
            print("=" * 50)
            print("LICENSE API ERROR DEBUG")
            print("=" * 50)
            print(f"Organization ID: {org_id}")
            print(f"Per Page: {per_page}")
            print(f"Error: {e}")
            print(f"Error Type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            print("=" * 50)
            
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load detailed licenses: {e}")
                st.write(f"Error type: {type(e)}")
                st.write(f"Traceback: {traceback.format_exc()}")
            return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load detailed licenses: {e}")
        return []

# Load network-wide alerts
@st.cache_data(ttl=300)
def load_network_alerts(key, network_id, timespan=86400):
    """Load network-wide alerts and events"""
    try:
        api = init_api(key)
        if not api:
            return {}
        
        alerts = {}
        
        # Get network events
        try:
            events = api.networks.getNetworkEvents(
                networkId=network_id,
                timespan=timespan,
                eventTypes=['alert', 'warning', 'error']
            )
            if events:
                alerts['network_events'] = events
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load network events: {e}")
        
        # Get network health alerts
        try:
            health = api.networks.getNetworkHealthAlerts(networkId=network_id)
            if health:
                alerts['health_alerts'] = health
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.write(f"Could not load health alerts: {e}")
        
        return alerts
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load network alerts: {e}")
        return {}

# Load all network clients
@st.cache_data(ttl=300)
def get_all_network_clients(key, network_id):
    """Load all network clients with perPage=5000 to get complete list"""
    try:
        api = init_api(key)
        if api:
            # Use perPage=5000 to get all clients instead of default 10
            return api.networks.getNetworkClients(network_id, perPage=5000)
        return []
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load network clients: {e}")
        return []

# Load client usage histories for all clients
@st.cache_data(ttl=300)
def get_clients_usage_histories(key, network_id, timespan, resolution):
    try:
        api = init_api(key)
        if not api:
            return []
        
        # Get all clients first
        clients = get_all_network_clients(key, network_id)
        if not clients:
            return []
        
        # Extract MAC addresses
        mac_addresses = [client['mac'] for client in clients if 'mac' in client]
        
        if not mac_addresses:
            return []
        
        # Process in chunks of 50 (Meraki API limit)
        chunk_size = 50
        all_results = []
        
        for i in range(0, len(mac_addresses), chunk_size):
            chunk = mac_addresses[i:i + chunk_size]
            try:
                chunk_results = api.networks.getNetworkClientsBandwidthUsageHistory(
                    network_id, 
                    timespan=timespan, 
                    resolution=resolution,
                    macs=chunk
                )
                all_results.extend(chunk_results)
            except Exception as e:
                if SHOW_DEBUG_INFO:
                    st.warning(f"Failed to load bandwidth history for chunk {i//chunk_size + 1}: {e}")
                continue
        
        return all_results
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load client usage histories: {e}")
        return []

# Load device system information (OS version, power status, CPU)
@st.cache_data(ttl=300)
def load_device_system_info(key, network_id, device_serial):
    """Load detailed system information for a specific device"""
    try:
        api = init_api(key)
        if not api:
            return {}
        
        system_info = {}
        
        # Try to get device status (includes power and basic info)
        try:
            device_status = api.devices.getDeviceStatus(device_serial)
            system_info['status'] = device_status
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.warning(f"Could not load device status for {device_serial}: {e}")
        
        # Try to get device management interface (includes OS version)
        try:
            mgmt_interface = api.devices.getDeviceManagementInterface(device_serial)
            system_info['management'] = mgmt_interface
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.warning(f"Could not load management interface for {device_serial}: {e}")
        
        # Try to get device performance (includes CPU if available)
        try:
            performance = api.devices.getDevicePerformance(device_serial)
            system_info['performance'] = performance
        except Exception as e:
            if SHOW_DEBUG_INFO:
                st.warning(f"Could not load performance data for {device_serial}: {e}")
        
        return system_info
        
    except Exception as e:
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load device system info for {device_serial}: {e}")
        return {}

# Load device events for event log
@st.cache_data(ttl=60)  # Shorter cache for events
def load_device_events(key, network_id, device_serial, product_type=None, timespan=86400):
    """Load events for a specific device"""
    try:
        api = init_api(key)
        if not api:
            print(f"❌ API 초기화 실패 - device_serial: {device_serial}")
            return []
        
        # Get network events filtered by device serial and product type
        # API 형식: /networks/:networkId/events?productType={{productType}}&deviceSerial={{deviceSerial}}&perPage={{perPage}}
        params = {
            'deviceSerial': device_serial,  # deviceSerical이 아닌 deviceSerial
            'perPage': 1000  # Get up to 1000 events
        }
        
        # Add product type if available (first parameter in your format)
        if product_type:
            params['productType'] = product_type
        
        # Add timespan (24 hours default)
        params['timespan'] = timespan
        
        # Print API call information to console
        print(f"\n🔍 이벤트 로그 API 호출:")
        print(f"   📡 API URL: https://api.meraki.com/api/v1/networks/{network_id}/events")
        print(f"   📋 Parameters (순서: productType, deviceSerial, perPage):")
        if 'productType' in params:
            print(f"      - productType: {params['productType']}")
        print(f"      - deviceSerial: {params['deviceSerial']}")
        print(f"      - perPage: {params['perPage']}")
        print(f"      - timespan: {params['timespan']}")
        print(f"   🌐 Network ID: {network_id}")
        print(f"   🔧 Device Serial: {device_serial}")
        print(f"   📱 Product Type: {product_type}")
        print(f"   ⏱️ Timespan: {timespan} seconds ({timespan/3600:.1f} hours)")
        
        # Construct full URL for debugging
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"https://api.meraki.com/api/v1/networks/{network_id}/events?{param_string}"
        print(f"   🔗 Full URL: {full_url}")
        
        # Make the API call
        print(f"   🚀 API 호출 중...")
        events = api.networks.getNetworkEvents(network_id, **params)
        
        # Print response information
        if events is None:
            print(f"   ❌ API 응답: None")
            print(f"   🔄 대체 방법 시도: deviceSerial 없이 호출...")
            
            # Try without deviceSerial filter as fallback
            try:
                fallback_params = {'timespan': timespan, 'perPage': 1000}
                if product_type:
                    fallback_params['productType'] = product_type
                print(f"   📋 대체 Parameters: {fallback_params}")
                
                events = api.networks.getNetworkEvents(network_id, **fallback_params)
                if events:
                    if isinstance(events, list):
                        # Filter by device serial manually
                        filtered_events = [e for e in events if isinstance(e, dict) and e.get('deviceSerial') == device_serial]
                        print(f"   ✅ 대체 호출 성공: 전체 {len(events)}개 중 {len(filtered_events)}개 필터링됨")
                        return filtered_events
                    elif isinstance(events, dict) and 'events' in events:
                        # Extract events from dict response
                        events_list = events['events']
                        if isinstance(events_list, list):
                            filtered_events = [e for e in events_list if isinstance(e, dict) and e.get('deviceSerial') == device_serial]
                            print(f"   ✅ 대체 호출 성공 (Dict): 전체 {len(events_list)}개 중 {len(filtered_events)}개 필터링됨")
                            return filtered_events
                        else:
                            print(f"   ❌ 대체 호출: events 키의 값이 리스트가 아님")
                            return []
                    else:
                        print(f"   ❌ 대체 호출: 예상치 못한 응답 타입 {type(events)}")
                        return []
                else:
                    print(f"   ❌ 대체 호출도 실패: 응답 없음")
                    return []
            except Exception as fallback_error:
                print(f"   💥 대체 호출 실패: {fallback_error}")
                return []
            
        elif isinstance(events, list):
            print(f"   ✅ API 응답: {len(events)}개 이벤트 반환")
            if len(events) > 0:
                print(f"   📄 첫 번째 이벤트 샘플:")
                first_event = events[0]
                if isinstance(first_event, dict):
                    for key, value in list(first_event.items())[:5]:  # First 5 keys
                        print(f"      - {key}: {value}")
                    if len(first_event) > 5:
                        print(f"      ... (총 {len(first_event)}개 필드)")
                    
                    # Check if events are actually for this device
                    device_match = first_event.get('deviceSerial') == device_serial
                    print(f"   🎯 디바이스 매칭: {device_match} (찾는 시리얼: {device_serial}, 실제: {first_event.get('deviceSerial', 'N/A')})")
                else:
                    print(f"      타입: {type(first_event)}, 값: {str(first_event)[:100]}")
            return events
        elif isinstance(events, dict):
            print(f"   📦 API 응답: Dict 형태 (Meraki API v1 형식)")
            print(f"   🔍 응답 구조:")
            for key, value in events.items():
                if key == 'events':
                    if isinstance(value, list):
                        print(f"      - {key}: {len(value)}개 이벤트 (리스트)")
                    else:
                        print(f"      - {key}: {type(value)} (예상: 리스트)")
                else:
                    print(f"      - {key}: {str(value)[:50]}...")
            
            # Extract events list from the response
            events_list = events.get('events', [])
            if isinstance(events_list, list):
                print(f"   ✅ events 키에서 {len(events_list)}개 이벤트 추출")
                if len(events_list) > 0:
                    print(f"   📄 첫 번째 이벤트 샘플:")
                    first_event = events_list[0]
                    if isinstance(first_event, dict):
                        for key, value in list(first_event.items())[:5]:  # First 5 keys
                            print(f"      - {key}: {value}")
                        if len(first_event) > 5:
                            print(f"      ... (총 {len(first_event)}개 필드)")
                        
                        # Check if events are actually for this device
                        device_match = first_event.get('deviceSerial') == device_serial
                        print(f"   🎯 디바이스 매칭: {device_match} (찾는 시리얼: {device_serial}, 실제: {first_event.get('deviceSerial', 'N/A')})")
                return events_list
            else:
                print(f"   ❌ events 키의 값이 리스트가 아님: {type(events_list)}")
                return []
        else:
            print(f"   ⚠️ 예상치 못한 응답 타입: {type(events)}")
            print(f"   📝 응답 내용: {str(events)[:200]}")
            if SHOW_DEBUG_INFO:
                st.warning(f"Unexpected events data type: {type(events)} for device {device_serial}")
            return []
        
    except Exception as e:
        print(f"   💥 API 호출 실패: {str(e)}")
        print(f"   🔍 오류 타입: {type(e).__name__}")
        if SHOW_DEBUG_INFO:
            st.error(f"Failed to load device events for {device_serial}: {e}")
        return []

# Function to generate event log text file
def generate_event_log_text(events, device_serial):
    """Generate a text file content from device events"""
    # Check if events is valid and is a list
    if not events or not isinstance(events, list):
        return f"No events found for device {device_serial}\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "=" * 80 + "\n\nNo event data available."
    
    log_content = f"Event Log for Device: {device_serial}\n"
    log_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_content += "=" * 80 + "\n\n"
    
    for i, event in enumerate(events):
        # Ensure event is a dictionary
        if not isinstance(event, dict):
            log_content += f"Event {i+1}: Invalid event data format\n"
            log_content += "-" * 40 + "\n"
            continue
            
        timestamp = event.get('occurredAt', 'N/A')
        event_type = event.get('type', 'N/A')
        description = event.get('description', 'N/A')
        category = event.get('category', 'N/A')
        
        log_content += f"Event {i+1}:\n"
        log_content += f"Timestamp: {timestamp}\n"
        log_content += f"Type: {event_type}\n"
        log_content += f"Category: {category}\n"
        log_content += f"Description: {description}\n"
        log_content += "-" * 40 + "\n"
    
    return log_content

# Security Check: Validate API Key
if not MERAKI_API_KEY:
    st.error("🔐 **API 키가 설정되지 않았습니다!**")
    st.markdown("""
    ### 설정 방법:
    
    1. **config.py 파일 생성**:
       ```bash
       cp config_example.py config.py
       ```
    
    2. **API 키 설정**:
       ```python
       MERAKI_API_KEY = "your_actual_meraki_api_key_here"
       ```
    
    3. **Meraki API 키 발급**:
       - [Meraki Dashboard](https://dashboard.meraki.com) 로그인
       - Organization > Settings > API access
       - 새 API 키 생성
    
    ### 보안 주의사항:
    - ❌ **절대 코드에 API 키를 하드코딩하지 마세요**
    - ✅ **config.py 파일만 사용하세요**
    - ✅ **config.py는 .gitignore에 포함되어 있습니다**
    """)
    st.stop()

# Main title
st.title("🌐  Meraki Network Analytics Dashboard")

# API Version and Capabilities Info - Hidden for cleaner UI
# st.markdown("""
# <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
#     <h4 style="margin: 0; color: #1f2937;">📡 API Information</h4>
#     <p style="margin: 0.5rem 0 0 0; color: #6b7280;">
#         <strong>Version:</strong> 1.62.0 | <strong>Base URL:</strong> https://api.meraki.com/api/v1 | 
#         <strong>Last Updated:</strong> September 3, 2025
#     </p>
#     <p style="margin: 0.5rem 0 0 0; color: #6b7280;">
#         <strong>Capabilities:</strong> Network Management • Device Configuration • Security Monitoring • 
#         Analytics & Insights • Wireless Management • Automation Tools
#     </p>
# </div>
# """, unsafe_allow_html=True)

# Log user login and start loading organizations
print("=" * 80)
print("🚀 USER LOGGED IN - LOADING ORGANIZATIONS")
print("=" * 80)
print(f"User: {st.session_state.get('username', 'Unknown')}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Organization selection with enhanced management
try:
    orgs = load_orgs(api_key)
    print(f"✅ Organizations loaded successfully: {len(orgs)} organizations")
except Exception as e:
    st.error(f"❌ 조직 로딩 중 오류 발생")
    st.warning(f"오류 내용: {str(e)}")
    
    st.warning("💡 가능한 원인:")
    st.write("1. API 키가 유효하지 않을 수 있습니다")
    st.write("2. 네트워크 연결 문제가 있을 수 있습니다")
    st.write("3. Meraki Dashboard API 서비스에 문제가 있을 수 있습니다")
    st.write("4. 이전 캐시 데이터에 문제가 있을 수 있습니다")
    st.info(f"🔑 현재 API 키: {api_key[:10]}...{api_key[-4:]}")
    
    col1, col2 = st.columns(2)
    with col1:
        # Clear cache and retry button
        if st.button("🔄 캐시 클리어 후 재시도", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            print("✅ All caches cleared")
            st.success("캐시가 클리어되었습니다. 재시도 중...")
            time.sleep(1)
            st.rerun()
    
    with col2:
        # Just retry button
        if st.button("🔄 다시 시도", type="secondary", use_container_width=True):
            st.rerun()
    
    st.stop()

# Check if organizations were loaded
if not orgs or len(orgs) == 0:
    st.error("⚠️ 조직을 찾을 수 없습니다.")
    st.warning("캐시된 빈 결과일 수 있습니다. 캐시를 클리어해보세요.")
    
    if st.button("🔄 캐시 클리어 후 재시도", type="primary"):
        st.cache_data.clear()
        st.cache_resource.clear()
        print("✅ All caches cleared")
        st.rerun()
    
    st.stop()

# Organization filtering - Load from config or use all organizations
try:
    from config import ALLOWED_ORGANIZATION_IDS
except ImportError:
    # If no whitelist is configured, show all organizations
    ALLOWED_ORGANIZATION_IDS = None

# Organization display - with optional filtering
print("=" * 80)
print("ORGANIZATION LOADING")
print("=" * 80)
print(f"Total organizations from API: {len(orgs)}")

org_map = {}
filtered_out = []

for o in orgs:
    org_name = o.get('name', 'Unknown')
    org_id = o.get('id', '')
    org_url = o.get('url', '')
    
    # Apply filtering if whitelist is configured
    if ALLOWED_ORGANIZATION_IDS is not None:
        if org_id in ALLOWED_ORGANIZATION_IDS:
            display_name = org_name
            org_map[display_name] = org_id
            print(f"✅ Included: {org_name} (ID: {org_id})")
        else:
            filtered_out.append(org_name)
            print(f"❌ Filtered: {org_name} (ID: {org_id})")
    else:
        # No filtering - include all organizations
        display_name = org_name
        org_map[display_name] = org_id
        print(f"✅ Included: {org_name} (ID: {org_id})")

print("\n" + "=" * 80)
print("ORGANIZATION SUMMARY")
print("=" * 80)
print(f"Available organizations: {len(org_map)}")
if ALLOWED_ORGANIZATION_IDS is not None:
    print(f"Filtered out: {len(filtered_out)}")
    print("Note: Organization filtering is enabled via config")
else:
    print("Note: All organizations are shown (no filtering)")
print("=" * 80)

# Set default organization
default_org = None
default_index = 0

# Try to find default organization from config
if DEFAULT_ORGANIZATION and org_map:
    for i, org_name in enumerate(org_map.keys()):
        org_id_val = org_map[org_name]
        if org_id_val == DEFAULT_ORGANIZATION:
            default_org = org_name
            default_index = i
            break

# If default organization not found, use the first available
if not default_org and org_map:
    default_org = list(org_map.keys())[0]
    default_index = 0

# Ensure we have a valid default organization
if not org_map:
    st.error("사용 가능한 조직이 없습니다.")
    st.stop()

# Update accessible organization names for auto-switching
if 'accessible_org_names' not in st.session_state or not st.session_state.accessible_org_names:
    st.session_state.accessible_org_names = list(org_map.keys())

# Organization selection with enhanced UI
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    # Initialize organization in session state if not exists
    if 'selected_organization' not in st.session_state:
        st.session_state.selected_organization = default_org
    
    sel_org = st.selectbox(r"$\textsf{\Large 🏢 조직 선택}$", list(org_map.keys()), 
                       index=list(org_map.keys()).index(st.session_state.selected_organization) if st.session_state.selected_organization in org_map else default_index,
                           key="org_selection")
    
    # Update session state when organization changes
    if sel_org != st.session_state.selected_organization:
        st.session_state.selected_organization = sel_org

org_id = org_map[sel_org]

nets = load_networks(api_key, org_id)

# Debug: Show filtering results
print("=" * 80)
print("NETWORK FILTERING RESULTS")
print("=" * 80)
print(f"Total filtered networks: {len(nets)}")
for i, net in enumerate(nets, 1):
    net_name = net.get('name', 'Unknown')
    net_id = net.get('id', 'Unknown')
    device_count = net.get('device_count', 0)
    print(f"  {i}. {net_name} (ID: {net_id}) - {device_count} devices")
print("=" * 80)

if not nets:
    st.error("⚠️ 이 조직에서 디바이스가 있는 접근 가능한 네트워크를 찾을 수 없습니다.")
    st.info("💡 네트워크 필터링 과정에서 디바이스가 없거나 접근할 수 없는 네트워크가 제외되었습니다. 콘솔 로그를 확인하여 자세한 내용을 확인하세요.")
    st.stop()

# Enhanced network display with more details
net_map = {}
for n in nets:
    net_name = n.get('name', 'Unknown')
    net_id = n.get('id', '')
    net_type = n.get('type', 'Unknown')
    net_id_short = net_id[:8] + "..." if len(net_id) > 8 else net_id
    display_name = net_name
    net_map[display_name] = net_id

# Network selection with enhanced UI
col1, col2 = st.columns([3, 1])
with col1:
    # Initialize networks in session state if not exists
    if 'selected_networks' not in st.session_state:
        default_networks = list(net_map.keys())[:3] if len(net_map) > 3 else list(net_map.keys())
        st.session_state.selected_networks = default_networks
    
    # Validate that selected networks exist in current options
    current_network_options = list(net_map.keys())
    valid_selected_networks = [net for net in st.session_state.selected_networks if net in current_network_options]
    
    # If no valid networks or all networks are invalid, use default
    if not valid_selected_networks:
        valid_selected_networks = current_network_options[:3] if len(current_network_options) > 3 else current_network_options
        st.session_state.selected_networks = valid_selected_networks
    
    sel_nets_display = st.multiselect(r"$\textsf{\Large 🌐 네트워크 선택 (관리할 네트워크 선택)}$", current_network_options, 
                                     default=valid_selected_networks,
                                     key="network_selection")
    
    # Update session state when networks change
    if sel_nets_display != st.session_state.selected_networks:
        st.session_state.selected_networks = sel_nets_display
    
    sel_nets = [net_map[name] for name in sel_nets_display]

if not sel_nets:
    st.error("최소 하나의 네트워크를 선택하세요.")
    st.stop()

# Network management panel - DISABLED FOR CLEANER UI
# 네트워크 관리 패널을 숨김 처리 (UI 단순화를 위해)
# with st.expander("🌐 네트워크 관리", expanded=True):
#     col1, col2, col3 = st.columns(3)
#     
#     with col1:
#         st.markdown("**📊 네트워크 요약**")
#         st.write(f"**총 네트워크:** {len(nets)}")
#         st.write(f"**선택된 네트워크:** {len(sel_nets)}")
#         
#         # Network types breakdown
#         network_types = {}
#         for net in nets:
#             net_type = net.get('type', 'Unknown')
#             network_types[net_type] = network_types.get(net_type, 0) + 1
#         
#         st.write("**네트워크 유형:**")
#         for net_type, count in network_types.items():
#             st.write(f"- {net_type}: {count}")
#     
#     with col2:
#         st.markdown("**📈 선택된 네트워크**")
#         for net_id in sel_nets:
#             display_name = next((name for name, nid in net_map.items() if nid == net_id), f"Network_{net_id}")
#             # Extract network name without ID suffix for cleaner display
#             network_name = display_name.split(' (')[0] if ' (' in display_name else display_name
#             st.write(f"• {network_name} (ID: {net_id})")
# VLAN Management section removed - functionality not implemented

# Create selected_networks list with all required information
# sel_nets contains network IDs, so we need to find the corresponding display names
selected_networks = []
for net_id in sel_nets:
    # Find the display name for this network ID
    display_name = next((name for name, nid in net_map.items() if nid == net_id), f"Network_{net_id}")
    selected_networks.append((net_id, display_name, "", "", ""))

# Ultra-fast device loading with immediate display
print("=" * 60)
print("ULTRA-FAST DEVICE DATA LOADING")
print("=" * 60)

# Load critical data first for immediate display (fastest possible)
print("🚀 Loading critical device data for immediate display...")
devices = load_critical_data_fast(api_key, org_id)

# Filter devices for selected networks immediately
filtered = [d for d in devices if d["networkId"] in sel_nets]

print(f"✅ Critical devices loaded: {len(devices)} (filtered: {len(filtered)})")

# Show immediate results to user
if filtered:
    print("🎉 UI can now display device data immediately!")
else:
    print("⚠️ No devices found for selected networks")

# ULTRA-FAST device details loading with immediate display
print("⚡ ULTRA-FAST device details loading...")

# Load device details first (most important for UI)
print("🚀 Loading device details for immediate display...")
detailed_devices = load_device_details(api_key, org_id)

# Filter detailed devices immediately
filtered_detailed = [d for d in detailed_devices if d.get("networkId") in sel_nets]

print(f"✅ Device details loaded: {len(detailed_devices)} devices (filtered: {len(filtered_detailed)})")

# Load firmware in background (non-blocking)
print("🔄 Loading firmware in background...")
try:
    firmware_info = load_device_firmware(api_key, org_id)
    print(f"✅ Firmware loaded: {len(firmware_info) if isinstance(firmware_info, dict) else 'N/A'}")
except Exception as e:
    print(f"⚠️ Firmware loading failed: {e}")
    firmware_info = {}

dashboard_data = {'org_data': {}, 'network_data': {}, 'load_time': 0}

print("🎉 UI can now display device details immediately!")

print("=" * 60)

# Verify filtered devices
print("=" * 60)
print("DEVICE FILTERING VERIFICATION")
print("=" * 60)
print(f"Total devices in organization: {len(devices)}")
print(f"Total detailed devices in organization: {len(detailed_devices)}")
print(f"Selected networks count: {len(sel_nets)}")
print(f"Filtered devices for selected networks: {len(filtered)}")
print(f"Filtered detailed devices: {len(filtered_detailed)}")
print("=" * 60)

# Display content based on selected page from sidebar navigation
current_page = st.session_state.get('current_page', '메인화면')

if current_page == "메인화면":
    
    # Header with refresh button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header("📊 실시간 네트워크 상태")
    #with col2:
    #    st.markdown("")  # Add some spacing
    #    if st.button("🔄 새로고침", key="main_refresh", help="데이터를 새로고침하고 경과시간을 초기화합니다"):
    #        st.session_state.data_load_time = datetime.now()
    #        st.cache_data.clear()
    #        st.rerun()
    
    # Calculate metrics by product type
    total_n = len(sel_nets)
    total_d = len(filtered)
    
    # Group devices by product type
    product_stats = {}
    product_type_map = {
        'appliance': '🔒 Appliance',
        'switch': '🔌 Switch', 
        'wireless': '📶 Wireless AP',
        'camera': '📹 Camera',
        'sensor': '🌡️ Sensor',
        'cellularGateway': '📱 Cellular Gateway'
    }
    
    for device in filtered:
        product_type = device.get('productType', 'unknown')
        status = device.get('status', 'unknown')
        
        if product_type not in product_stats:
            product_stats[product_type] = {
                'online': 0,
                'offline': 0, 
                'alerting': 0,
                'dormant': 0,
                'total': 0
            }
        
        product_stats[product_type][status] = product_stats[product_type].get(status, 0) + 1
        product_stats[product_type]['total'] += 1
    
    # Display product-based device status

    
    if product_stats:
        # Define the desired display order
        display_order = ['appliance', 'switch', 'wireless', 'camera', 'sensor', 'cellularGateway']
        
        # Filter to only show product types that exist in the data
        available_products = [pt for pt in display_order if pt in product_stats]
        
        # Create columns based on number of available product types (max 4 columns)
        num_products = len(available_products)
        if num_products <= 4:
            cols = st.columns(num_products)
        else:
            # If more than 4 products, use 4 columns and wrap
            cols = st.columns(4)
        
        col_idx = 0
        for product_type in available_products:
            if product_type in product_stats:
                stats = product_stats[product_type]
            with cols[col_idx % len(cols)]:
                # Get product display name
                display_name = product_type_map.get(product_type, f"📱 {product_type.title()}")
                
                st.markdown(f"### {display_name}")
                
                # Display status counts with colors
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 8px; background: #f8fafc; border: 1px solid #e5e7eb;">
                    <div style="margin-bottom: 8px;">
                        <span style="color: #059669; font-weight: 600; font-size: 1.1rem;">온라인: {stats['online']}</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="color: #dc2626; font-weight: 600; font-size: 1.1rem;">오프라인: {stats['offline']}</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="color: #d97706; font-weight: 600; font-size: 1.1rem;">경고: {stats['alerting']}</span>
                    </div>
                    <div>
                        <span style="color: #6b7280; font-weight: 600; font-size: 1.1rem;">비활성: {stats['dormant']}</span>
                    </div>
                    <hr style="margin: 10px 0; border: 1px solid #e5e7eb;">
                    <div style="text-align: center;">
                        <strong>총 {stats['total']}대</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            col_idx += 1
    
    # Calculate overall metrics for alert logic (but don't display)
    online = sum(1 for d in filtered if d["status"] == "online")
    offline = sum(1 for d in filtered if d["status"] == "offline")
    alerting = sum(1 for d in filtered if d["status"] == "alerting")
    dormant = sum(1 for d in filtered if d["status"] == "dormant")
    
     # 지정된 메트릭들을 숨김 처리 (🏥 네트워크 상태, 🚨 중요 알림, 📡 상태)
    
    # Get devices with issues
    offline_devices = [d for d in filtered if d["status"] == "offline"]
    alerting_devices = [d for d in filtered if d["status"] == "alerting"]
    
    # Real-time Alert Dashboard - only show if there are alerts
    if offline_devices or alerting_devices:
        st.markdown("---")
        st.subheader("🚨 실시간 알림 대시보드")
        # Create alert cards
        col1, col2 = st.columns(2)
        
        with col1:
            if offline_devices:
                st.error(f"❌ **오프라인 디바이스: {len(offline_devices)}**")
                for device in offline_devices[:5]:  # Show first 5
                    network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                    st.write(f"• **{device.get('name', 'Unknown')}** ({network_name}) - {device.get('model', 'N/A')}")
                if len(offline_devices) > 5:
                    st.write(f"... 및 {len(offline_devices) - 5}개 더")
        
        with col2:
            if alerting_devices:
                st.warning(f"⚠️ **경고 디바이스: {len(alerting_devices)}**")
                for device in alerting_devices[:5]:  # Show first 5
                    network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                    st.write(f"• **{device.get('name', 'Unknown')}** ({network_name}) - {device.get('model', 'N/A')}")
                if len(alerting_devices) > 5:
                    st.write(f"... 및 {len(alerting_devices) - 5}개 더")
        
        # Quick action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 상태 새로고침", key="refresh_status"):
                st.session_state.data_load_time = datetime.now()
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("📊 모든 문제 보기", key="view_issues"):
                st.session_state.show_detailed_alerts = not st.session_state.get('show_detailed_alerts', False)
                st.rerun()
    
    # Show detailed alerts if requested
    if st.session_state.get('show_detailed_alerts', False):
        st.markdown("---")
        st.subheader("🚨 상세 알림 정보")
        
        # Get all devices with issues
        offline_devices = [d for d in filtered if d["status"] == "offline"]
        alerting_devices = [d for d in filtered if d["status"] == "alerting"]
        
        if offline_devices or alerting_devices:
            col1, col2 = st.columns(2)
            
            with col1:
                if offline_devices:
                    st.error(f"❌ **OFFLINE DEVICES: {len(offline_devices)}**")
                    for device in offline_devices:
                        network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                        with st.expander(f"🔴 {device.get('name', 'Unknown')} ({network_name})", expanded=True):
                            st.write(f"**Device Details:**")
                            st.write(f"- **Name:** {device.get('name', 'Unknown')}")
                            st.write(f"- **Model:** {device.get('model', 'N/A')}")
                            st.write(f"- **Serial:** {device.get('serial', 'N/A')}")
                            st.write(f"- **MAC:** {device.get('mac', 'N/A')}")
                            st.write(f"- **IP:** {device.get('lanIp', 'N/A')}")
                            st.write(f"- **Network:** {network_name}")
                            st.write(f"- **Status:** {device.get('status', 'N/A')}")
                            st.write(f"- **Last Seen:** {device.get('lastReportedAt', 'N/A')}")
                            
                            # Additional device information
                            if device.get('tags'):
                                st.write(f"- **Tags:** {', '.join(device.get('tags', []))}")
                            if device.get('address'):
                                st.write(f"- **Address:** {device.get('address', 'N/A')}")
                            if device.get('notes'):
                                st.write(f"- **Notes:** {device.get('notes', 'N/A')}")
            
            with col2:
                if alerting_devices:
                    st.warning(f"⚠️ **ALERTING DEVICES: {len(alerting_devices)}**")
                    for device in alerting_devices:
                        network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                        with st.expander(f"🟡 {device.get('name', 'Unknown')} ({network_name})", expanded=True):
                            st.write(f"**Device Details:**")
                            st.write(f"- **Name:** {device.get('name', 'Unknown')}")
                            st.write(f"- **Model:** {device.get('model', 'N/A')}")
                            st.write(f"- **Serial:** {device.get('serial', 'N/A')}")
                            st.write(f"- **MAC:** {device.get('mac', 'N/A')}")
                            st.write(f"- **IP:** {device.get('lanIp', 'N/A')}")
                            st.write(f"- **Network:** {network_name}")
                            st.write(f"- **Status:** {device.get('status', 'N/A')}")
                            st.write(f"- **Last Seen:** {device.get('lastReportedAt', 'N/A')}")
                            
                            # Additional device information
                            if device.get('tags'):
                                st.write(f"- **Tags:** {', '.join(device.get('tags', []))}")
                            if device.get('address'):
                                st.write(f"- **Address:** {device.get('address', 'N/A')}")
                            if device.get('notes'):
                                st.write(f"- **Notes:** {device.get('notes', 'N/A')}")
                            
                            # Load and display detailed alert information - HIDDEN (숨김 처리)
                            # st.markdown("---")
                            # st.subheader("🚨 Alert Details")
                            
                            # if device.get('serial'):
                            #     # Load device-specific alerts
                            #     device_alerts = load_device_alerts(api_key, org_id, device.get('serial'))
                            #     
                            #     if device_alerts:
                            #         # Display status events
                            #         if device_alerts.get('status_events'):
                            #             st.write("**📊 Status Events:**")
                            #             status_events = device_alerts['status_events']
                            #             # Safely handle the response - check if it's a list
                            #             if isinstance(status_events, list) and len(status_events) > 0:
                            #                 # Show last 5 events
                            #                 for event in status_events[-5:]:
                            #                     event_time = event.get('ts', 'N/A')
                            #                     event_status = event.get('status', 'N/A')
                            #                     st.write(f"- {event_time}: {event_status}")
                            #             else:
                            #                 st.info("Status events data format not as expected")
                            #         
                            #         # Display performance issues
                            #         if device_alerts.get('performance'):
                            #             st.write("**📈 Performance Issues:**")
                            #             performance_data = device_alerts['performance']
                            #             # Safely handle the response - check if it's a list
                            #             if isinstance(performance_data, list) and len(performance_data) > 0:
                            #                 # Show last 3 performance entries
                            #                 for perf in performance_data[-3:]:
                            #                     loss = perf.get('lossPercent', 'N/A')
                            #                     latency = perf.get('latencyMs', 'N/A')
                            #                     st.write(f"- Loss: {loss}%, Latency: {latency}ms")
                            #             else:
                            #                 st.info("Performance data format not as expected")
                            #         
                            #         # Display security events
                            #         if device_alerts.get('security'):
                            #             st.write("**🔒 Security Events:**")
                            #             security_data = device_alerts['security']
                            #             # Safely handle the response - check if it's a list
                            #             if isinstance(security_data, list) and len(security_data) > 0:
                            #                 # Show last 3 security events
                            #                 for sec in security_data[-3:]:
                            #                     event_type = sec.get('eventType', 'N/A')
                            #                     event_time = sec.get('occurredAt', 'N/A')
                            #                     st.write(f"- {event_time}: {event_type}")
                            #             else:
                            #                 st.info("Security events data format not as expected")
                            #         
                            #         if not any([device_alerts.get('status_events'), device_alerts.get('performance'), device_alerts.get('security')]):
                            #             st.info("No specific alert details available for this device")
                            #     else:
                            #         st.info("Loading alert details...")
                                
                                # Load network-wide alerts for this device's network - HIDDEN (숨김 처리)
                                # network_alerts = load_network_alerts(api_key, device["networkId"])
                                # if network_alerts:
                                #     st.markdown("---")
                                #     st.subheader("🌐 Network Alerts")
                                #     
                                #     if network_alerts.get('network_events'):
                                #         st.write("**📡 Network Events:**")
                                #         network_events = network_alerts['network_events']
                                #         # Safely handle the response - check if it's a list
                                #         if isinstance(network_events, list) and len(network_events) > 0:
                                #             # Show last 3 network events
                                #             for event in network_events[-3:]:
                                #                 event_type = event.get('type', 'N/A')
                                #                 event_time = event.get('occurredAt', 'N/A')
                                #                 event_desc = event.get('description', 'N/A')
                                #                 st.write(f"- {event_time}: {event_type} - {event_desc}")
                                #         else:
                                #             st.info("Network events data format not as expected")
                                #     
                                #     if network_alerts.get('health_alerts'):
                                #         st.write("**🏥 Health Alerts:**")
                                #         health_alerts = network_alerts['health_alerts']
                                #         # Safely handle the response - check if it's a list
                                #         if isinstance(health_alerts, list) and len(health_alerts) > 0:
                                #             # Show last 3 health alerts
                                #             for alert in health_alerts[-3:]:
                                #                 alert_type = alert.get('type', 'N/A')
                                #                 alert_time = alert.get('occurredAt', 'N/A')
                                #                 st.write(f"- {alert_time}: {alert_type}")
                                #         else:
                                #             st.info("Health alerts data format not as expected")
                                #     
                                #     if not any([network_alerts.get('network_events'), network_alerts.get('health_alerts')]):
                                #         st.info("No network alerts available")
                                # else:
                                #     st.info("Loading network alerts...")
                            # else:
                            #     st.warning("⚠️ Device serial number not available - cannot load detailed alerts")
            
            # Summary and actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 문제", len(offline_devices) + len(alerting_devices))
            with col2:
                st.metric("오프라인 디바이스", len(offline_devices))
            with col3:
                st.metric("경고 디바이스", len(alerting_devices))
            
            if st.button("🔒 상세 알림 숨기기", key="hide_alerts"):
                st.session_state.show_detailed_alerts = False
                st.rerun()
        else:
            st.success("✅ **중요한 문제가 발견되지 않았습니다!** 모든 디바이스가 정상 작동 중입니다.")
            if st.button("🔒 상세 알림 숨기기", key="hide_alerts"):
                st.session_state.show_detailed_alerts = False
                st.rerun()
    

    # 네트워크별 디바이스 세부사항만 유지 (col2 부분을 독립적으로 표시)
    if total_d > 0:
        st.subheader("🔍 디바이스 세부사항")
        if filtered:
            # Group devices by network
            network_devices = {}
            for device in filtered:
                network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                if network_name not in network_devices:
                    network_devices[network_name] = {"online": 0, "offline": 0, "alerting": 0, "dormant": 0}
                
                status = device.get("status", "unknown")
                if status == "online":
                    network_devices[network_name]["online"] += 1
                elif status == "offline":
                    network_devices[network_name]["offline"] += 1
                elif status == "alerting":
                    network_devices[network_name]["alerting"] += 1
                elif status == "dormant":
                    network_devices[network_name]["dormant"] += 1
            
            # Display network breakdown
            for network_idx, (network, counts) in enumerate(network_devices.items()):
                with st.expander(f"🌐 {network} ({sum(counts.values())} devices)", expanded=True):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("✅ 온라인", counts["online"])
                        with col2:
                            st.metric("❌ 오프라인", counts["offline"])
                        with col3:
                            st.metric("⚠️ 경고", counts["alerting"])
                        with col4:
                            st.metric("😴 비활성", counts["dormant"])
                        
                        # Show detailed device list for this network
                        network_device_list = [d for d in filtered if next((name for name, net_id in net_map.items() if net_id == d["networkId"]), "") == network]
                        if network_device_list:
                            st.markdown("**📋 디바이스 세부사항:**")
                            
                            # ULTRA-FAST device details - skip slow system info loading
                            device_details = []
                            for device in network_device_list:
                                # Skip slow system info loading for speed
                                # Use basic device info only
                                os_version = "N/A"  # Skip loading for speed
                                power_status = "N/A"  # Skip loading for speed
                                cpu_usage = "N/A"  # Skip loading for speed
                                
                                # Format status with colors for display
                                status = device.get("status", "Unknown")
                                if status == "online":
                                    status_display = "🟢 온라인"
                                elif status == "offline":
                                    status_display = "🔴 오프라인"
                                elif status == "alerting":
                                    status_display = "🟡 경고"
                                else:
                                    status_display = f"⚪ {status}"
                                
                                # Format power status with colors
                                if power_status == "on":
                                    power_display = "🟢 On"
                                elif power_status == "off":
                                    power_display = "🔴 Off"
                                else:
                                    power_display = power_status
                                
                                device_details.append({
                                    "번호": len(device_details) + 1,
                                    "디바이스명": device.get("name", "Unknown"),
                                    "모델": device.get("model", "N/A"),
                                    "시리얼": device.get("serial", "N/A"),
                                    "상태": status_display,
                                    "MAC": device.get("mac", "N/A"),
                                    "IP": device.get("lanIp", "N/A"),
                                    "OS 버전": os_version,
                                    "전원 상태": power_display,
                                    "CPU 사용률": cpu_usage
                                })
                            
                            # Create DataFrame and display
                            device_df = pd.DataFrame(device_details)
                            
                            # Display the enhanced table
                            st.dataframe(device_df, use_container_width=True, hide_index=True)
                            
                            # Add event log download with selectbox for better handling of many devices
                            st.markdown("**📄 이벤트 로그 다운로드:**")
                            
                            # Create device options for selectbox
                            device_options = []
                            for i, device in enumerate(network_device_list):
                                device_name = device.get("name", "Unknown")
                                device_serial = device.get("serial", "N/A")
                                device_options.append((f"{i+1}. {device_name} ({device_serial})", i))
                            
                            # Get network_id safely
                            network_id = ""
                            if network_device_list:
                                network_id = network_device_list[0].get("networkId", "")
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                selected_device_idx = st.selectbox(
                                    "디바이스를 선택하세요",
                                    options=[idx for _, idx in device_options],
                                    format_func=lambda x: device_options[x][0],
                                    key=f"event_log_select_{network_idx}_{network_id}_{len(network_device_list)}",
                                    help="이벤트 로그를 다운로드할 디바이스를 선택하세요"
                                )
                            
                            with col2:
                                st.markdown("&nbsp;")  # 빈 공간 (selectbox 라벨과 같은 높이)

                                selected_device = network_device_list[selected_device_idx]
                                device_name = selected_device.get("name", "Unknown")
                                device_serial = selected_device.get("serial", "N/A")
                                # network_id is already defined above
                                product_type = selected_device.get("productType", "")
                                
                                st.markdown(
                                    """
                                    <style>
                                    /* 이 버튼에만 margin-top 적용 */
                                    .generate-log-btn {
                                        margin-bottom: 0.5rem;
                                    }
                                    </style>
                                    """, unsafe_allow_html=True
                                )

                                if st.button("📄 로그 생성", key=f"generate_log_{network_idx}_{device_serial}_{network_id}", 
                                           help=f"{device_name}의 이벤트 로그 생성", 
                                           use_container_width=True):
                                    print(f"\n🔴 사용자가 로그 생성 버튼 클릭!")
                                    print(f"   👤 Device: {device_name}")
                                    print(f"   🔢 Serial: {device_serial}")
                                    print(f"   🌐 Network: {network_id}")
                                    print(f"   📱 Product Type: {product_type}")
                                    
                                    with st.spinner(f"{device_name} 이벤트 로그 생성 중..."):
                                        print(f"   📡 API 호출 시작...")
                                        events = load_device_events(api_key, network_id, device_serial, product_type)
                                        print(f"   📝 로그 텍스트 생성 중...")
                                        log_content = generate_event_log_text(events, device_serial)
                                        print(f"   ✅ 로그 생성 완료: {len(log_content)} 문자")
                                        
                                        # Store in session state for download
                                        st.session_state[f'log_content_{device_serial}'] = log_content
                                        st.session_state[f'log_filename_{device_serial}'] = f"{device_name}_{device_serial}_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                                        print(f"   💾 세션 상태에 저장 완료")
                                        st.rerun()
                            
                            # Show download button if log content is ready
                            if f'log_content_{device_serial}' in st.session_state:
                                st.download_button(
                                    label=f"📥 {device_name}_events.txt 다운로드",
                                    data=st.session_state[f'log_content_{device_serial}'],
                                    file_name=st.session_state[f'log_filename_{device_serial}'],
                                    mime="text/plain",
                                    key=f"download_btn_{network_idx}_{device_serial}_{network_id}",
                                    use_container_width=True
                                )
                                # Clear the session state after showing download button
                                del st.session_state[f'log_content_{device_serial}']
                                del st.session_state[f'log_filename_{device_serial}']
        else:
            st.warning("⚠️ 선택된 네트워크에서 디바이스를 찾을 수 없습니다.")
            st.info("💡 네트워크 필터링 과정에서 디바이스가 있는 네트워크만 표시되어야 합니다. 이 메시지가 표시되면 네트워크 필터링을 확인하세요.")
    
    # Add comprehensive device status table - MOVED OUTSIDE OF NETWORK LOOP
    if total_d > 0:
        st.markdown("---")
        st.subheader("📊 종합 디바이스 상태 테이블")
        
        if filtered:
            # Create comprehensive device table
            comprehensive_devices = []
            for device in filtered:
                network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                comprehensive_devices.append({
                    "네트워크": network_name,
                    "디바이스명": device.get("name", "Unknown"),
                    "모델": device.get("model", "N/A"),
                    "상태": device.get("status", "Unknown"),
                    "시리얼": device.get("serial", "N/A"),
                    "MAC": device.get("mac", "N/A"),
                    "IP": device.get("lanIp", "N/A"),
                    "펌웨어": device.get("firmware", "N/A"),
                    "마지막 확인": device.get("lastReportedAt", "N/A")
                })
            
            comprehensive_df = pd.DataFrame(comprehensive_devices)
            
            # Add status-based filtering
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("상태별 필터", ["전체", "online", "offline", "alerting", "dormant"], key="comprehensive_status_filter")
            with col2:
                network_filter = st.selectbox("네트워크별 필터", ["전체"] + list(net_map.keys()), key="comprehensive_network_filter")
            
            # Apply filters
            filtered_df = comprehensive_df.copy()
            if status_filter != "전체":
                filtered_df = filtered_df[filtered_df["상태"] == status_filter]
            if network_filter != "전체":
                filtered_df = filtered_df[filtered_df["네트워크"] == network_filter]
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            # Summary statistics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("총 디바이스", len(filtered_df))
            with col2:
                st.metric("온라인", len(filtered_df[filtered_df["상태"] == "online"]))
            with col3:
                st.metric("오프라인", len(filtered_df[filtered_df["상태"] == "offline"]))
            with col4:
                st.metric("경고", len(filtered_df[filtered_df["상태"] == "alerting"]))
            with col5:
                st.metric("비활성", len(filtered_df[filtered_df["상태"] == "dormant"]))
        else:
            st.info("선택된 네트워크에서 디바이스를 찾을 수 없습니다")
    else:
        st.warning("선택된 네트워크에서 디바이스를 찾을 수 없습니다")

elif current_page == "트래픽 분석":
    st.header("🌐 트래픽 분석 (네트워크 트래픽 패턴 및 애플리케이션 사용량)")
    
    if not enable_traffic:
        st.info("🔧 사이드바에서 트래픽 분석을 활성화하여 트래픽 데이터를 확인하세요")
    else:
        # Load traffic data only when user visits this page (on-demand loading)
        print("=" * 60)
        print("ON-DEMAND TRAFFIC ANALYSIS DATA LOADING")
        print("=" * 60)
        
        with st.spinner("트래픽 데이터 로딩 중..."):
            traffic_data = load_traffic_analysis_data_parallel(api_key, sel_nets, timespan, resolution)
        
        print(f"✅ Traffic analysis data loaded in {traffic_data['load_time']:.2f} seconds")
        print("=" * 60)
        
        for net_id in sel_nets:
            # Find the display name for this network ID
            display_name = next((name for name, nid in net_map.items() if nid == net_id), f"Network_{net_id}")
            
            # Extract data from parallel results
            network_data = traffic_data['network_data'].get(net_id, {})
            comprehensive_traffic = network_data.get('traffic', {})
            bandwidth_data = network_data.get('bandwidth', [])
            clients_data = network_data.get('clients', [])
            
            # Check if we have any traffic data
            has_traffic_data = any(data for data in comprehensive_traffic.values()) if comprehensive_traffic else False
            
            if not has_traffic_data and not bandwidth_data:
                # Skip networks with no data instead of showing warning
                continue
            
            # Get time range information for display
            timespan_hours = timespan / 3600 if timespan else 1
            time_range_text = f"{timespan_hours:.1f}시간" if timespan_hours < 24 else f"{timespan_hours/24:.1f}일"
            
            # Create a visually distinct card for each network
            st.markdown("""
            <div style="
                height: 3px;
                background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
                margin: 2rem 0;
                border-radius: 2px;
            "></div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                margin: 1rem 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <h2 style="
                    color: white;
                    margin: 0 0 0.5rem 0;
                    font-size: 1.8rem;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                ">🌐 {display_name}</h2>
                <p style="
                    color: rgba(255,255,255,0.9);
                    margin: 0;
                    font-size: 1.1rem;
                ">종합 트래픽 분석 (모든 디바이스 타입) • {time_range_text} 기준</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create content container for better organization
            with st.container():
                
                # Display device type breakdown
                if comprehensive_traffic:
                    st.markdown("### 📊 디바이스 타입별 데이터 현황")
                col1, col2, col3, col4 = st.columns(4)
                
                device_type_names = {
                    'combined': '🔄 통합',
                    'wireless': '📶 무선',
                    'switch': '🔌 스위치', 
                    'appliance': '🛡️ 어플라이언스'
                }
                
                for i, (device_type, data) in enumerate(comprehensive_traffic.items()):
                    with [col1, col2, col3, col4][i]:
                        app_count = len(data) if data else 0
                        st.metric(
                            device_type_names.get(device_type, device_type.upper()),
                            f"{app_count}",
                            help=f"{device_type} 디바이스 타입에서 감지된 애플리케이션 수"
                        )
            
            # Combine all traffic data from all device types
            all_apps = combine_traffic_data(comprehensive_traffic)
            top_apps = pd.DataFrame()
            
            # Initialize traffic metrics
            total_traffic_mb = 0
            total_traffic_gb = 0
            total_downstream_bytes = 0
            total_upstream_bytes = 0
            total_bytes = 0
            
            if not all_apps.empty:
                # Convert to MB for display
                all_apps["sent_MB"] = all_apps["sent"] / (1024 * 1024)
                all_apps["recv_MB"] = all_apps["recv"] / (1024 * 1024)
                all_apps["TotalMB"] = all_apps["sent_MB"] + all_apps["recv_MB"]
                
                # Sort by TotalMB descending and get top 15 for display only
                top_apps = all_apps.nlargest(15, "TotalMB").reset_index(drop=True)
                
                # Calculate total traffic from combined data
                total_sent_bytes = all_apps["sent"].sum()
                total_recv_bytes = all_apps["recv"].sum()
                total_bytes = total_sent_bytes + total_recv_bytes
                total_traffic_mb = total_bytes / (1024 * 1024)
                total_traffic_gb = total_traffic_mb / 1024
                total_downstream_bytes = total_recv_bytes
                total_upstream_bytes = total_sent_bytes
            else:
                # Show detailed information when no data is available
                st.warning(f"⚠️ {display_name}에서 애플리케이션 트래픽 데이터를 찾을 수 없습니다.")
                # Fallback to bandwidth data if no traffic data
                if bandwidth_data:
                    df = pd.DataFrame(bandwidth_data)
                    if len(df) > 0 and 'downstream' in df.columns and 'upstream' in df.columns:
                        # Convert Mbps to bytes (assuming Mbps values)
                        df["downstream_bytes"] = df["downstream"] * 1024 * 1024 / 8
                        df["upstream_bytes"] = df["upstream"] * 1024 * 1024 / 8
                        df["total_bytes"] = df["downstream_bytes"] + df["upstream_bytes"]
                        
                        total_downstream_bytes = df["downstream_bytes"].sum()
                        total_upstream_bytes = df["upstream_bytes"].sum()
                        total_bytes = total_downstream_bytes + total_upstream_bytes
                        total_traffic_mb = total_bytes / (1024 * 1024)
                        total_traffic_gb = total_traffic_mb / 1024
                else:
                    st.error("❌ 대체 데이터 소스도 사용할 수 없습니다.")
                    continue
                
                # Enhanced metrics display with time range information
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 총 트래픽", f"{total_traffic_mb:.2f} MB", 
                             help=f"지난 {time_range_text} 동안의 총 트래픽 볼륨 (업로드 + 다운로드)")
                    st.metric("📊 총 트래픽 (GB)", f"{total_traffic_gb:.3f} GB", 
                             help=f"지난 {time_range_text} 동안의 총 트래픽 볼륨 (GB 단위)")
            
            with col2:
                upload_mb = total_upstream_bytes / (1024 * 1024)
                download_mb = total_downstream_bytes / (1024 * 1024)
                st.metric("📤 총 업로드", f"{upload_mb:.2f} MB", 
                             help=f"지난 {time_range_text} 동안의 총 업로드 트래픽")
                st.metric("📥 총 다운로드", f"{download_mb:.2f} MB", 
                             help=f"지난 {time_range_text} 동안의 총 다운로드 트래픽")
            
            with col3:
                # Get accurate client count using multiple methods
                total_client_count = 0
                client_count_source = "N/A"
                
                # Method 1: Try to get from clients overview API (most accurate)
                try:
                    clients_overview = load_network_clients_overview(api_key, net_id)
                    if clients_overview and 'counts' in clients_overview:
                        counts = clients_overview['counts']
                        total_client_count = counts.get('total', 0)
                        client_count_source = "Overview API"
                    elif clients_overview and 'total' in clients_overview:
                        total_client_count = clients_overview['total']
                        client_count_source = "Overview API"
                except:
                    pass
                
                # Method 2: Fallback to actual connected clients count
                if total_client_count == 0 and clients_data:
                    total_client_count = len(clients_data)
                    client_count_source = "Connected Clients"
                
                # Method 3: Fallback to application data
                if total_client_count == 0 and len(all_apps) > 0:
                    total_client_count = all_apps["numClients"].max()  # Use max instead of sum
                    client_count_source = "Application Data (Max)"
                
                st.metric("👥 총 클라이언트", f"{total_client_count}", 
                         help=f"클라이언트 수 ({client_count_source}) - 최대 5000개까지 로드")
            
            with col4:
                # Get total application count (no limit)
                total_applications = len(all_apps) if len(all_apps) > 0 else 0
                st.metric("📱 총 애플리케이션", f"{total_applications}", 
                         help=f"지난 {time_range_text} 동안 감지된 모든 애플리케이션 수")
                
            # Enhanced traffic breakdown with time range context
            st.markdown("---")
            st.subheader(f"📊 트래픽 상세 분석 ({time_range_text} 기준)")
            
            # Time range context box
            st.info(f"⏰ **분석 기간**: 지난 {time_range_text} | **데이터 포인트**: {len(all_apps) if not all_apps.empty else 0}개 | **네트워크**: {display_name}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 트래픽 분포:**")
                upload_percentage = (total_upstream_bytes / total_bytes * 100) if total_bytes > 0 else 0
                download_percentage = (total_downstream_bytes / total_bytes * 100) if total_bytes > 0 else 0
                upload_mb = total_upstream_bytes / (1024 * 1024)
                download_mb = total_downstream_bytes / (1024 * 1024)
                st.write(f"• 업로드: {upload_mb:.2f} MB ({upload_percentage:.1f}%)")
                st.write(f"• 다운로드: {download_mb:.2f} MB ({download_percentage:.1f}%)")
                st.write(f"• 총 트래픽: {total_traffic_mb:.2f} MB")
                st.write(f"• 시간당 평균: {total_traffic_mb / timespan_hours:.2f} MB/h")
                
            with col2:
                st.markdown("**📊 데이터 품질:**")
                st.write(f"• 데이터 포인트: {len(all_apps) if not all_apps.empty else 0}개")
                st.write(f"• 애플리케이션 수: {total_applications}개")
                st.write(f"• 평균 앱당 트래픽: {total_traffic_mb / total_applications:.2f} MB" if total_applications > 0 else "• 평균 앱당 트래픽: N/A")
                st.write(f"• 클라이언트당 평균: {total_traffic_mb / total_client_count:.2f} MB" if total_client_count > 0 else "• 클라이언트당 평균: N/A")
            
            st.markdown("---")
            
            # Enhanced traffic visualization with time range
            st.subheader(f"📊 애플리케이션 트래픽 개요 ({time_range_text} 기준)")
            
            # Show comprehensive application statistics
            if len(all_apps) > 0:
                st.info(f"📊 **전체 통계**: {len(all_apps)}개 애플리케이션, 총 {total_client_count}명 클라이언트")
                
                # Show top applications chart
                if len(top_apps) > 0:
                    try:
                        # Validate data before creating chart
                        if not top_apps.empty and 'TotalMB' in top_apps.columns and 'application' in top_apps.columns:
                            # Create enhanced horizontal bar chart with better formatting
                            fig = px.bar(
                                top_apps,
                                x="TotalMB",
                                y="application",
                                orientation="h",
                                height=max(400, len(top_apps) * 30),  # Dynamic height based on number of apps
                                title=f"상위 {len(top_apps)}개 애플리케이션 트래픽 - {display_name} ({time_range_text})",
                                color="TotalMB",
                                color_continuous_scale="viridis",
                                text="TotalMB"
                            )
                            
                            # Format text labels
                            fig.update_traces(
                                texttemplate='%{text:.1f}MB',
                                textposition='outside',
                                hovertemplate='<b>%{y}</b><br>트래픽: %{x:.2f}MB<br>클라이언트: %{customdata[0]}<extra></extra>',
                                customdata=top_apps[['numClients']].values
                            )
                            
                            fig.update_layout(
                                xaxis_title="트래픽 볼륨 (MB)",
                                yaxis_title="애플리케이션",
                                showlegend=False,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                margin=dict(l=200)  # More space for app names
                            )
                            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                            fig.update_yaxes(showgrid=False)
                            st.plotly_chart(fig, use_container_width=True, key=f"traffic_chart_{net_id}")
                        else:
                            st.warning("차트 생성에 필요한 데이터가 부족합니다.")
                    except Exception as chart_error:
                        # Hide chart section when error occurs
                        pass
                
                # Additional traffic insights with time context
                st.markdown("---")
                st.subheader(f"📈 트래픽 인사이트 ({time_range_text} 기준)")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🔥 상위 5개 애플리케이션:**")
                    for i, (_, app) in enumerate(top_apps.head(5).iterrows(), 1):
                        percentage = (app['TotalMB'] / total_traffic_mb) * 100 if total_traffic_mb > 0 else 0
                        st.write(f"{i}. **{app['application']}**: {app['TotalMB']:.1f}MB ({percentage:.1f}%)")
                
                with col2:
                    st.markdown("**📊 전체 트래픽 통계:**")
                    if len(all_apps) > 0:
                        st.write(f"• 총 애플리케이션: {len(all_apps)}개")
                        st.write(f"• 최대 앱 트래픽: {all_apps['TotalMB'].max():.1f}MB")
                        st.write(f"• 평균 앱 트래픽: {all_apps['TotalMB'].mean():.1f}MB")
                        st.write(f"• 중간값 앱 트래픽: {all_apps['TotalMB'].median():.1f}MB")
                        st.write(f"• 상위 5개 앱 비율: {(top_apps.head(5)['TotalMB'].sum() / total_traffic_mb * 100):.1f}%" if total_traffic_mb > 0 else "• 상위 5개 앱 비율: 0%")
                        st.write(f"• 시간당 평균: {total_traffic_mb / timespan_hours:.2f} MB/h")
                
                # Show ALL applications table
                st.markdown("---")
                st.subheader(f"📋 모든 애플리케이션 목록 ({len(all_apps)}개)")
                
                if len(all_apps) > 0:
                    # Create comprehensive display table
                    display_apps = all_apps.copy()
                    display_apps['Percentage'] = (display_apps['TotalMB'] / total_traffic_mb * 100).round(2) if total_traffic_mb > 0 else 0
                    display_apps = display_apps.sort_values('TotalMB', ascending=False)
                    
                    # Format the display
                    display_apps['TotalMB'] = display_apps['TotalMB'].round(2)
                    display_apps['numClients'] = display_apps['numClients'].astype(int)
                    
                    st.dataframe(
                        display_apps[['application', 'TotalMB', 'numClients', 'deviceType', 'Percentage']].rename(columns={
                            'application': '애플리케이션',
                            'TotalMB': '트래픽 (MB)',
                            'numClients': '클라이언트 수',
                            'deviceType': '디바이스 타입',
                            'Percentage': '비율 (%)'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Close the content container for this network
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Add separator line after each network
                st.markdown("""
                <div style="
                    height: 2px;
                    background: linear-gradient(90deg, transparent, #667eea, transparent);
                    margin: 2rem 0;
                "></div>
                """, unsafe_allow_html=True)
                
                # Enhanced debug information with time context
                if SHOW_DEBUG_INFO:
                    with st.expander(f"🔍 Debug: Traffic Calculation & API Data ({time_range_text} 기준)", expanded=True):
                        st.write(f"**📊 트래픽 계산 상세:**")
                        st.write(f"- 분석 기간: {time_range_text} ({timespan}초)")
                        st.write(f"- 사용된 API: Network Traffic + Network Bandwidth")
                        st.write(f"- Traffic 데이터 포인트: {len(traffic_data) if traffic_data else 0}개")
                        st.write(f"- Bandwidth 데이터 포인트: {len(bandwidth_data) if bandwidth_data else 0}개")
                        st.write(f"- 클라이언트 데이터: {len(clients_data) if clients_data else 0}개")
                        st.write(f"- 총 업로드 바이트: {total_upstream_bytes:,} bytes")
                        st.write(f"- 총 다운로드 바이트: {total_downstream_bytes:,} bytes")
                        st.write(f"- 총 바이트: {total_bytes:,} bytes")
                        st.write(f"- 총 트래픽 (MB): {total_traffic_mb:.2f} MB")
                        st.write(f"- 총 트래픽 (GB): {total_traffic_gb:.3f} GB")
                        st.write(f"- 시간당 평균: {total_traffic_mb / timespan_hours:.2f} MB/h")
                        st.write(f"- 총 클라이언트: {total_client_count}")
                        st.write(f"- 총 애플리케이션: {total_applications}")
                        st.write(f"- 표시된 애플리케이션: {len(top_apps)}개 (상위 15개)")
                        
                        st.write("**📈 전체 데이터 품질 검증:**")
                        if len(all_apps) > 0:
                            st.write(f"- 평균 앱당 트래픽: {total_traffic_mb / len(all_apps):.2f} MB")
                            st.write(f"- 최대 앱 트래픽: {all_apps['TotalMB'].max():.2f} MB")
                            st.write(f"- 최소 앱 트래픽: {all_apps['TotalMB'].min():.2f} MB")
                            st.write(f"- 총 클라이언트 수 (모든 앱): {all_apps['numClients'].sum()}")
                        st.write(f"- 업로드 비율: {upload_percentage:.1f}%")
                        st.write(f"- 다운로드 비율: {download_percentage:.1f}%")
                        
                        st.write("**🔍 디바이스 타입별 API 데이터:**")
                        if comprehensive_traffic:
                            for device_type, data in comprehensive_traffic.items():
                                if data:
                                    st.write(f"**{device_type.upper()} ({len(data)}):**")
                                    st.json(data[0] if len(data) > 0 else {})
                                    st.write("---")
                        
                        st.write("**🔍 통합된 데이터 샘플:**")
                        if not all_apps.empty:
                            st.json(all_apps.iloc[0].to_dict())
                        
                        st.write("**📋 처리된 DataFrame 샘플:**")
                        st.dataframe(df.head())
                        
                        st.write("**📊 상위 애플리케이션 상세:**")
                        st.dataframe(top_apps.head(10))
            else:
                st.info("No application data available")
            
            # Detailed traffic table with intuitive format
            st.markdown("---")
            st.subheader("🔍 Application Traffic Details")
            
            if len(top_apps) > 0:
                # Create intuitive display format
                display_data = []
                for _, app in top_apps.iterrows():
                    app_name = app["application"]
                    total_mb = app["TotalMB"]
                    clients = app["numClients"]
                    
                    # Format: Application Name (TotalMB MB)
                    display_name = f"{app_name} ({total_mb:.1f}MB)"
                    display_data.append({
                        "Application": display_name,
                        "Traffic (MB)": f"{total_mb:.1f}",
                        "Clients": clients,
                        "Upload (MB)": f"{app['sent']/1024/1024:.1f}",
                        "Download (MB)": f"{app['recv']/1024/1024:.1f}"
                    })
                
                display_df = pd.DataFrame(display_data)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show raw data for debugging
                if SHOW_DEBUG_INFO:
                    with st.expander("🔍 Debug: Raw Application Data", expanded=True):
                        st.write("**Top Applications DataFrame:**")
                        st.dataframe(top_apps)
                        
                        st.write("**Data Processing Steps:**")
                        st.write("1. Group by application name")
                        st.write("2. Sum TotalMB (sent + received)")
                        st.write("3. Take max numClients per application")
                        st.write("4. Sort by TotalMB descending")
            else:
                st.info("No detailed traffic data available")
                
                # Close the content container for this network
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Add comprehensive traffic analysis table across all networks
        st.markdown("---")
        st.subheader("🌐 Cross-Network Traffic Analysis")
        
        # Collect traffic data from all networks
        all_network_traffic = []
        for net_id in sel_nets:
            # Find the display name for this network ID
            display_name = next((name for name, nid in net_map.items() if nid == net_id), f"Network_{net_id}")
            data = load_traffic(api_key, net_id, timespan)
            if data:
                df = pd.DataFrame(data)
                df["TotalMB"] = (df["sent"] + df["recv"]) / 1024 / 1024
                df["Network"] = display_name
                
                # Aggregate by application across network
                network_apps = df.groupby("application").agg({
                    "TotalMB": "sum",
                    "numClients": "max",
                    "sent": "sum",
                    "recv": "sum"
                }).reset_index()
                network_apps["Network"] = display_name
                all_network_traffic.append(network_apps)
        
        if all_network_traffic:
            # Combine all network data
            combined_traffic = pd.concat(all_network_traffic, ignore_index=True)
            
            # Create comprehensive analysis
            comprehensive_traffic = combined_traffic.groupby("application").agg({
                "TotalMB": "sum",
                "numClients": "max",
                "sent": "sum",
                "recv": "sum",
                "Network": lambda x: ", ".join(x.unique())
            }).reset_index()
            
            # Sort by total traffic
            comprehensive_traffic = comprehensive_traffic.sort_values("TotalMB", ascending=False)
            
            # Display comprehensive table
            st.markdown("**📊 All Networks - Application Traffic Summary**")
            
            # Add filtering options
            col1, col2 = st.columns(2)
            with col1:
                min_traffic = st.number_input("Minimum Traffic (MB)", min_value=0.0, value=1.0, step=0.1, key="traffic_min_filter")
            with col2:
                app_search = st.text_input("Search Applications", placeholder="Enter application name", key="traffic_app_search")
            
            # Apply filters
            filtered_traffic = comprehensive_traffic[comprehensive_traffic["TotalMB"] >= min_traffic]
            if app_search:
                filtered_traffic = filtered_traffic[filtered_traffic["application"].str.contains(app_search, case=False, na=False)]
            
            # Display filtered results
            if len(filtered_traffic) > 0:
                display_comprehensive = []
                for _, app in filtered_traffic.iterrows():
                    display_comprehensive.append({
                        "애플리케이션": app["application"],
                        "총 트래픽 (MB)": f"{app['TotalMB']:.2f}",
                        "총 트래픽 (GB)": f"{app['TotalMB']/1024:.3f}",
                        "최대 클라이언트": app["numClients"],
                        "업로드 (MB)": f"{app['sent']/1024/1024:.2f}",
                        "다운로드 (MB)": f"{app['recv']/1024/1024:.2f}",
                        "네트워크": app["Network"]
                    })
                
                comprehensive_df = pd.DataFrame(display_comprehensive)
                st.dataframe(comprehensive_df, use_container_width=True, hide_index=True)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("총 애플리케이션", len(filtered_traffic))
                with col2:
                    st.metric("총 트래픽", f"{filtered_traffic['TotalMB'].sum():.2f} MB")
                with col3:
                    st.metric("총 업로드", f"{filtered_traffic['sent'].sum()/1024/1024:.2f} MB")
                with col4:
                    st.metric("총 다운로드", f"{filtered_traffic['recv'].sum()/1024/1024:.2f} MB")
            else:
                st.info("현재 필터와 일치하는 애플리케이션이 없습니다")
        else:
            st.info("네트워크 전체에서 사용 가능한 트래픽 데이터가 없습니다")
            
    # Advanced Analytics and Insights section removed - functionality not implemented
    
# Traffic trends analysis section removed
    
# Application insights section removed
    
    # Performance optimization
    if st.session_state.get('show_performance_optimization', False):
        st.markdown("---")
        st.subheader("⚡ 성능 최적화 제안")
        
        # Performance optimization recommendations
        st.markdown("**🎯 최적화 제안:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 트래픽 최적화:**")
            st.write("• 대역폭 사용량이 높은 애플리케이션 식별")
            st.write("• QoS 정책 설정으로 중요 트래픽 우선순위 부여")
            st.write("• 불필요한 애플리케이션 차단 고려")
            st.write("• 트래픽 셰이핑으로 대역폭 분배 최적화")
        
        with col2:
            st.markdown("**🔧 네트워크 최적화:**")
            st.write("• VLAN 분할로 네트워크 세그멘테이션")
            st.write("• 무선 채널 최적화")
            st.write("• 디바이스 펌웨어 업데이트")
            st.write("• 보안 정책 강화")
        
        # Real-time performance metrics
        st.markdown("**📈 실시간 성능 지표:**")
        
        # Calculate real performance metrics
        total_devices = len(filtered)
        online_devices = len([d for d in filtered if d.get('status') == 'online'])
        offline_devices = len([d for d in filtered if d.get('status') == 'offline'])
        alerting_devices = len([d for d in filtered if d.get('status') == 'alerting'])
        
        # Calculate network efficiency
        if total_devices > 0:
            network_efficiency = (online_devices / total_devices) * 100
        else:
            network_efficiency = 0
        
        # Calculate bandwidth utilization (if traffic data available)
        bandwidth_utilization = 0
        if enable_traffic:
            total_traffic_mb = 0
            for net_id in sel_nets:
                try:
                    traffic_data = load_traffic(api_key, net_id, timespan)
                    if traffic_data:
                        df = pd.DataFrame(traffic_data)
                        total_traffic_mb += (df["sent"].sum() + df["recv"].sum()) / (1024 * 1024)
                except:
                    continue
            # Assume 1Gbps = 125MB/s, calculate utilization
            if total_traffic_mb > 0:
                bandwidth_utilization = min((total_traffic_mb / (125 * 3600)) * 100, 100)  # 1 hour period
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("네트워크 효율성", f"{network_efficiency:.1f}%", 
                     delta=f"{network_efficiency-85:.1f}%" if network_efficiency > 0 else None,
                     help="온라인 디바이스 비율")
        with col2:
            st.metric("대역폭 활용률", f"{bandwidth_utilization:.1f}%", 
                     delta=f"{bandwidth_utilization-72:.1f}%" if bandwidth_utilization > 0 else None,
                     help="실제 트래픽 기반 활용률")
        with col3:
            device_health = ((total_devices - offline_devices - alerting_devices) / total_devices * 100) if total_devices > 0 else 0
            st.metric("디바이스 상태", f"{device_health:.1f}%", 
                     delta=f"{device_health-98:.1f}%" if device_health > 0 else None,
                     help="정상 작동 디바이스 비율")
        with col4:
            # Security score based on device status
            security_score = max(0, 100 - (offline_devices + alerting_devices) * 10)
            st.metric("보안 점수", f"{security_score:.1f}%", 
                     delta=f"{security_score-92:.1f}%" if security_score > 0 else None,
                     help="디바이스 상태 기반 보안 점수")
            
            st.markdown("---")

elif current_page == "클라이언트 분석":
    st.header("👥 개별 클라이언트 분석 (특정 클라이언트의 상세 트래픽)")
    
    if not enable_clients:
        st.info("🔧 사이드바에서 클라이언트 분석을 활성화하여 클라이언트 데이터를 확인하세요")
    else:
        # Load client data only when user visits this page (on-demand loading)
        print("=" * 60)
        print("ON-DEMAND CLIENT ANALYSIS DATA LOADING")
        print("=" * 60)
        
        with st.spinner("클라이언트 데이터 로딩 중..."):
            client_data = load_client_analysis_data_parallel(api_key, sel_nets, timespan, resolution)
        
        print(f"✅ Client analysis data loaded in {client_data['load_time']:.2f} seconds")
        print("=" * 60)
        
        # 클라이언트 선택 섹션
        st.markdown("### 📋 클라이언트 선택")
        
        # Extract data from parallel results
        all_clients = []
        network_clients_map = {}
        total_clients_overview = 0
        
        for net_id in sel_nets:
            display_name = next((name for name, nid in net_map.items() if nid == net_id), f"Network_{net_id}")
            
            # Get data from parallel results
            network_data = client_data['network_data'].get(net_id, {})
            clients_data = network_data.get('clients', [])
            clients_overview = network_data.get('clients_overview', {})
            
            # Get total client count from overview
            if clients_overview and 'counts' in clients_overview:
                total_clients_overview += clients_overview['counts'].get('total', 0)
            elif clients_overview and 'total' in clients_overview:
                total_clients_overview += clients_overview['total']
            
            if clients_data:
                network_clients_map[net_id] = {
                    'display_name': display_name,
                    'clients': clients_data
                }
                for client in clients_data:
                    client['network_id'] = net_id
                    client['network_name'] = display_name
                    all_clients.append(client)
        
        if not all_clients:
            st.warning("선택된 네트워크에서 클라이언트를 찾을 수 없습니다.")
        else:
            # 클라이언트 선택 UI
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 클라이언트 선택 드롭다운
                client_options = []
                for i, client in enumerate(all_clients):
                    client_name = client.get('description', client.get('hostname', f"Client_{i}"))
                    client_mac = client.get('mac', 'Unknown')
                    network_name = client.get('network_name', 'Unknown')
                    client_id = f"{client_name} ({client_mac}) - {network_name}"
                    client_options.append((client_id, i))
                
                selected_client_idx = st.selectbox(
                    "클라이언트를 선택하세요",
                    options=[idx for _, idx in client_options],
                    format_func=lambda x: client_options[x][0],
                    help="분석할 클라이언트를 선택하세요"
                )
            
            
            # 선택된 클라이언트 정보
            selected_client = all_clients[selected_client_idx]
            client_name = selected_client.get('description', selected_client.get('hostname', 'Unknown'))
            client_mac = selected_client.get('mac', 'Unknown')
            client_ip = selected_client.get('ip', 'Unknown')
            client_vlan = selected_client.get('vlan', 'Unknown')
            client_network = selected_client.get('network_name', 'Unknown')
            
            st.markdown("---")
            st.subheader(f"👤 {client_name}")
            
            # 클라이언트 기본 정보
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**🖥️ 클라이언트명:**<br><span class='client-name'>{client_name}</span>", unsafe_allow_html=True)
                st.markdown(f"**🌐 네트워크:**<br><span class='client-name'>{client_network}</span>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**📡 MAC 주소:**<br><span class='mac-address'>{client_mac}</span>", unsafe_allow_html=True)
                st.markdown(f"**🔢 IP 주소:**<br><span class='mac-address'>{client_ip}</span>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"**🏷️ VLAN:**<br><span class='client-name'>{client_vlan}</span>", unsafe_allow_html=True)
                status_text = "온라인" if selected_client.get('status') == 'Online' else "오프라인"
                st.markdown(f"**📶 연결 상태:**<br><span class='client-name'>{status_text}</span>", unsafe_allow_html=True)
            
            with col4:
                # 클라이언트 사용량 정보
                usage = selected_client.get('usage', {})
                sent = usage.get('sent', 0)
                recv = usage.get('recv', 0)
                total_usage = sent + recv
                
                st.markdown(f"**📤 전송량:**<br><span class='client-name'>{sent / (1024*1024):.2f} MB</span>", unsafe_allow_html=True)
                st.markdown(f"**📥 수신량:**<br><span class='client-name'>{recv / (1024*1024):.2f} MB</span>", unsafe_allow_html=True)
            
            # 클라이언트별 트래픽 분석
            st.markdown("---")
            st.subheader("📊 클라이언트 트래픽 분석")
            
            # 클라이언트별 애플리케이션 트래픽 분석
            client_network_id = selected_client.get('network_id')
            
            # 해당 네트워크의 모든 디바이스 타입 트래픽 데이터 로드
            comprehensive_traffic = load_comprehensive_traffic(api_key, client_network_id, timespan)
            
            if comprehensive_traffic:
                # 클라이언트별 트래픽 필터링
                client_traffic = []
                for device_type, traffic_data in comprehensive_traffic.items():
                    if traffic_data:
                        for app in traffic_data:
                            # 클라이언트 MAC이나 IP로 필터링 (실제로는 더 정교한 매칭 필요)
                            if (client_mac in str(app.get('destination', '')) or 
                                client_ip in str(app.get('destination', '')) or
                                client_mac in str(app.get('source', '')) or
                                client_ip in str(app.get('source', ''))):
                                app_copy = app.copy()
                                app_copy['deviceType'] = device_type
                                client_traffic.append(app_copy)
                
            if client_traffic:
                # 클라이언트 트래픽 데이터프레임 생성
                client_df = pd.DataFrame(client_traffic)
                client_df["sent_MB"] = client_df["sent"] / (1024 * 1024)
                client_df["recv_MB"] = client_df["recv"] / (1024 * 1024)
                client_df["TotalMB"] = client_df["sent_MB"] + client_df["recv_MB"]
                
                # 클라이언트 트래픽 메트릭
                total_sent_mb = client_df["sent_MB"].sum()
                total_recv_mb = client_df["recv_MB"].sum()
                total_traffic_mb = total_sent_mb + total_recv_mb
                total_clients = client_df["numClients"].sum()
                        
                col1, col2, col3, col4 = st.columns(4)
                        
                with col1:
                    st.metric("📊 총 트래픽", f"{total_traffic_mb:.2f} MB")
                    st.metric("📤 업로드", f"{total_sent_mb:.2f} MB")
                        
                with col2:
                    st.metric("📥 다운로드", f"{total_recv_mb:.2f} MB")
                    st.metric("👥 관련 클라이언트", f"{total_clients}")
                        
                with col3:
                    # 상위 애플리케이션
                    top_apps = client_df.nlargest(5, "TotalMB")
                    st.metric("🔥 상위 앱", top_apps.iloc[0]["application"] if len(top_apps) > 0 else "N/A")
                    st.metric("📱 앱 수", f"{len(client_df)}개")
                        
                with col4:
                    # 디바이스 타입 분포
                    device_types = client_df["deviceType"].value_counts()
                    st.metric("🔌 주요 디바이스", device_types.index[0] if len(device_types) > 0 else "N/A")
                    st.metric("📊 디바이스 타입", f"{len(device_types)}개")
                
                # 클라이언트 애플리케이션 트래픽 차트
                st.markdown("---")
                st.subheader("📈 클라이언트 애플리케이션 트래픽")
                
                if len(client_df) > 0:
                    # 상위 10개 애플리케이션 차트
                    top_10_apps = client_df.nlargest(10, "TotalMB")
                    
                    # Use plotly graph objects directly to avoid narwhals compatibility issues
                    fig = go.Figure(data=[
                        go.Bar(
                            x=top_10_apps["TotalMB"],
                            y=top_10_apps["application"],
                            orientation='h',
                            text=top_10_apps["TotalMB"].round(1),
                            texttemplate='%{text:.1f}MB',
                            textposition='outside',
                            marker=dict(
                                color=top_10_apps["TotalMB"],
                                colorscale='Viridis',
                                showscale=True
                            )
                        )
                    ])
                    fig.update_layout(
                        title=f"{client_name} - 상위 애플리케이션 트래픽",
                        xaxis_title="Total MB",
                        yaxis_title="Application",
                        height=400
                    )
                    
                    fig.update_layout(
                        height=max(400, len(top_10_apps) * 30),
                        xaxis_title="트래픽 (MB)",
                        yaxis_title="애플리케이션",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                # 클라이언트 상세 테이블
                st.markdown("---")
                st.subheader("📋 클라이언트 상세 트래픽 테이블")
                
                display_df = client_df[['application', 'TotalMB', 'sent_MB', 'recv_MB', 'numClients', 'deviceType', 'protocol', 'port']].copy()
                display_df = display_df.sort_values('TotalMB', ascending=False)
                display_df['TotalMB'] = display_df['TotalMB'].round(2)
                display_df['sent_MB'] = display_df['sent_MB'].round(2)
                display_df['recv_MB'] = display_df['recv_MB'].round(2)
                        
                st.dataframe(
                    display_df.rename(columns={
                        'application': '애플리케이션',
                        'TotalMB': '총 트래픽 (MB)',
                        'sent_MB': '업로드 (MB)',
                        'recv_MB': '다운로드 (MB)',
                        'numClients': '클라이언트 수',
                        'deviceType': '디바이스 타입',
                        'protocol': '프로토콜',
                        'port': '포트'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        
 

elif current_page == "스위치 포트":
    st.header("🔌 스위치 포트 분석 (포트 상태,설정값) ")
    
    if not enable_switch_ports:
        st.info("🔧 Enable Switch Port Analysis in the sidebar to view port data")
    else:
        sw_data = load_switch_ports(api_key, org_id)
        
        if not sw_data:
            st.warning("⚠️ No switch data available")
        else:
            # Switch selection with better labels
            switch_options = []
            for switch_id, switch_ports in sw_data.items():
                # Try to get a meaningful name from the first port's device info
                if switch_ports and len(switch_ports) > 0:
                    first_port = switch_ports[0]
                    device_name = first_port.get("deviceName", "")
                    description = first_port.get("description", "")
                    
                    if device_name and device_name != "N/A":
                        label = f"{device_name} ({switch_id})"
                    elif description and description != "N/A":
                        label = f"{description} ({switch_id})"
                    else:
                        label = f"Switch {switch_id}"
                else:
                    label = f"Switch {switch_id}"
                
                switch_options.append((label, switch_id))
            
            # Create a mapping for display
            switch_display_map = {label: switch_id for label, switch_id in switch_options}
            
            if len(switch_options) > 1:
                sel_sw_label = st.selectbox("Select Switch", list(switch_display_map.keys()), key="switch_selection")
                sel_sw = switch_display_map[sel_sw_label]
            else:
                # If only one switch, show it directly
                sel_sw_label = switch_options[0][0]
                sel_sw = switch_options[0][1]
            
            ports = sw_data[sel_sw]
            
            if not ports:
                st.info(f"스위치의 포트 정보를 가져올수 없습니다. {sel_sw}")
            else:
                # Port metrics
                total_ports = len(ports)
                connected_ports = sum(1 for p in ports if p.get("status", "").lower() == "connected")
                disconnected_ports = sum(1 for p in ports if p.get("status", "").lower() == "disconnected")
                error_ports = sum(1 for p in ports if p.get("status", "").lower() in ["error", "alerting"])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🔌 총 포트", total_ports)
                with col2:
                    st.metric("✅ 연결됨", f"{connected_ports}/{total_ports}")
                with col3:
                    st.metric("❌ 연결 끊김", f"{disconnected_ports}/{total_ports}")
                with col4:
                    st.metric("⚠️ 오류", f"{error_ports}/{total_ports}")
                
                st.markdown("---")
                
                # Port status visualization - HIDDEN (숨김 처리)
                # col1, col2 = st.columns(2)
                  

               
                
                # Comprehensive Switch Port Analysis Table
                st.subheader("📊 포트 상세 설정정보")
                
                if ports:
                    # Create comprehensive port analysis data with colored status
                    port_analysis = []
                    for port in ports:
                        status = port.get("status", "N/A")
                        
                        # Add color coding to status based on port status
                        if status.lower() in ["connected", "up", "active"]:
                            colored_status = f'<span style="color: #059669; font-weight: 600;">🟢 {status}</span>'
                        elif status.lower() in ["disconnected", "down", "error", "failed"]:
                            colored_status = f'<span style="color: #dc2626; font-weight: 600;">🔴 {status}</span>'
                        elif status.lower() in ["warning", "degraded", "partial"]:
                            colored_status = f'<span style="color: #d97706; font-weight: 600;">🟡 {status}</span>'
                        elif status.lower() in ["disabled", "dormant", "inactive"]:
                            colored_status = f'<span style="color: #6b7280; font-weight: 600;">⚫ {status}</span>'
                        else:
                            colored_status = f'<span style="color: #6b7280; font-weight: 600;">⚪ {status}</span>'
                        
                        # Convert VLAN to int if it's a number, otherwise keep as is
                        vlan_value = port.get("vlan", "N/A")
                        if isinstance(vlan_value, (int, float)) and not pd.isna(vlan_value):
                            vlan_value = int(vlan_value)
                        elif vlan_value is None or pd.isna(vlan_value):
                            vlan_value = "N/A"
                        
                        port_analysis.append({
                            "Port ID": port.get("portId", "N/A"),
                            "Status": colored_status,
                            "Speed": port.get("speed", "Null") if port.get("speed") else "Null",
                            "Duplex": port.get("duplex", "N/A"),
                            "Enabled": port.get("enabled", "N/A"),
                            "Description": port.get("description", "N/A"),
                            "Type": port.get("type", "N/A"),
                            "VLAN": vlan_value,
                            "STP Guard": port.get("stpGuard", "N/A"),
                            "Device Name": port.get("deviceName", "N/A")
                        })
                    
                    port_analysis_df = pd.DataFrame(port_analysis)
                    
                    # Add filtering options for the comprehensive table
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        min_ports = st.number_input("Minimum Ports per Status", min_value=1, value=1, step=1, key="port_min_filter")
                    with col2:
                        status_search = st.text_input("Search by Status", placeholder="e.g., Connected, Error", key="port_status_search")
                    with col3:
                        speed_search = st.text_input("Search by Speed", placeholder="e.g., 1000, 100", key="port_speed_search")
                    
                    # Apply filters to comprehensive table
                    filtered_analysis = port_analysis_df.copy()
                    
                    if status_search:
                        filtered_analysis = filtered_analysis[filtered_analysis["Status"].str.contains(status_search, case=False, na=False)]
                    
                    if speed_search:
                        filtered_analysis = filtered_analysis[filtered_analysis["Speed"].str.contains(speed_search, case=False, na=False)]
                    
                    # Display filtered comprehensive table with HTML rendering
                    if len(filtered_analysis) > 0:
                        # Add CSS for clean table styling
                        st.markdown("""
                        <style>
                        .styled-table {
                            border-collapse: collapse;
                            margin: 15px 0;
                            font-size: 0.9em;
                            font-family: sans-serif;
                            width: 100%;
                            border: 1px solid #e5e7eb;
                        }
                        .styled-table thead tr {
                            background-color: #f8fafc;
                            color: #374151;
                            text-align: center;
                            font-weight: 600;
                        }
                        .styled-table th,
                        .styled-table td {
                            padding: 8px 12px;
                            border: 1px solid #e5e7eb;
                            text-align: center;
                        }
                        .styled-table tbody tr {
                            border-bottom: 1px solid #e5e7eb;
                        }
                        .styled-table tbody tr:nth-of-type(even) {
                            background-color: #fafafa;
                        }
                        .styled-table tbody tr:hover {
                            background-color: #f0f9ff;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Convert DataFrame to HTML to render colored status
                        html_table = filtered_analysis.to_html(escape=False, index=False, classes="styled-table")
                        st.markdown(html_table, unsafe_allow_html=True)
                        
                        # Summary metrics for comprehensive analysis - HIDDEN (숨김 처리)
                        # col1, col2, col3, col4 = st.columns(4)
                        # with col1:
                        #     st.metric("Total Ports", len(filtered_analysis))
                        # with col2:
                        #     connected_count = len(filtered_analysis[filtered_analysis["Status"] == "Connected"])
                        #     st.metric("Connected", connected_count)
                        # with col3:
                        #     error_count = len(filtered_analysis[filtered_analysis["Status"] == "Error"])
                        #     st.metric("Errors", error_count)
                        # with col4:
                        #     unique_speeds = filtered_analysis["Speed"].nunique()
                        #     st.metric("Speed Types", unique_speeds)
                        
                        # Port status summary by speed - HIDDEN (숨김 처리)
                        # st.markdown("**📈 Port Status by Speed:**")
                        # speed_status_summary = filtered_analysis.groupby(["Speed", "Status"]).size().unstack(fill_value=0)
                        # st.dataframe(speed_status_summary, use_container_width=True)
                        
                    else:
                        st.info("No ports match the comprehensive analysis filters")
                else:
                    st.info("No port data available for comprehensive analysis")
                


elif current_page == "디바이스 상태 알림":
    st.header("🚨 디바이스 상태 알림 (디바이스 상태 모니터링 및 오류 감지)")
    
    if not enable_alerts:
        st.info("🔧 알림 및 오류 분석을 위해 사이드바에서 활성화해주세요")
    else:
        # Load device alerts data only when user visits this page (on-demand loading)
        print("=" * 60)
        print("ON-DEMAND DEVICE ALERTS DATA LOADING")
        print("=" * 60)
        
        # Get device serials for parallel loading
        device_serials = [d.get('serial') for d in filtered if d.get('serial')]
        
        if device_serials:
            with st.spinner("디바이스 알림 데이터 로딩 중..."):
                alerts_data = load_device_alerts_data_parallel(api_key, org_id, device_serials)
            print(f"✅ Device alerts data loaded in {alerts_data['load_time']:.2f} seconds")
        else:
            alerts_data = {'device_data': {}, 'load_time': 0}
            print("⚠️ No device serials found for alerts loading")
        
        print("=" * 60)
        
        # Filter devices by status
        offline_devices = [d for d in filtered if d["status"] == "offline"]
        alerting_devices = [d for d in filtered if d["status"] == "alerting"]
        online_devices = [d for d in filtered if d["status"] == "online"]
        dormant_devices = [d for d in filtered if d["status"] == "dormant"]
        
        # Simple status summary
        total_devices = len(filtered)
        total_issues = len(offline_devices) + len(alerting_devices)
        
        if total_issues > 0:
            # Show critical issues
            st.error(f"🚨 **{total_issues} 디바이스에 문제가 있습니다**")
            
            # Device status breakdown
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Online", len(online_devices), delta_color="normal")
            with col2:
                st.metric("❌ Offline", len(offline_devices), delta_color="inverse")
            with col3:
                st.metric("⚠️ Alerting", len(alerting_devices), delta_color="inverse")
            with col4:
                st.metric("😴 Dormant", len(dormant_devices), delta_color="normal")
            
            st.markdown("---")
            
            # Show problematic devices
            if offline_devices:
                st.error("❌ **오프라인 디바이스**")
                for device in offline_devices:
                    network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                    st.write(f"• **{device.get('name', 'Unknown')}** ({network_name})")
                    st.write(f"  - Model: {device.get('model', 'N/A')}")
                    st.write(f"  - Serial: {device.get('serial', 'N/A')}")
                    st.write("---")
            
            if alerting_devices:
                st.warning("⚠️ **알림 디바이스**")
                for device in alerting_devices:
                    network_name = next((name for name, net_id in net_map.items() if net_id == device["networkId"]), "Unknown")
                    st.write(f"• **{device.get('name', 'Unknown')}** ({network_name})")
                    st.write(f"  - Model: {device.get('model', 'N/A')}")
                    st.write(f"  - Serial: {device.get('serial', 'N/A')}")
                    st.write("---")
        else:
            # All systems operational
            st.success("✅ **모든 시스템 정상 작동**")
            st.info("디바이스 상태 문제가 감지되지 않았습니다.")
            
            # Simple health summary
            if total_devices > 0:
                # Only decrease health for confirmed errors (offline, alerting)
                # Dormant devices don't affect health score
                confirmed_errors = len(offline_devices) + len(alerting_devices)
                if confirmed_errors == 0:
                    health_percentage = 100.0
                else:
                    health_percentage = ((total_devices - confirmed_errors) / total_devices) * 100
                
                st.metric("Network Health", f"{health_percentage:.1f}%", 
                         delta_color="normal" if health_percentage == 100 else "inverse")
    
    # Configuration Changes Section
    st.markdown("---")
    st.subheader("📋 설정 변경 내역 (조직 설정 변경 기록)")
    
    # Fixed per_page value
    per_page = 3000
    
    # Generate text report button
    if st.button("📄 Generate Text Report", key="generate_config_report", use_container_width=True):
        with st.spinner("Loading configuration changes..."):
            config_changes = load_configuration_changes(api_key, org_id, per_page)
            
            if config_changes:
                st.success(f"✅ Loaded {len(config_changes)} configuration changes")
                
                # Convert all data to text format without preprocessing
                text_content = "=== MERAKI CONFIGURATION CHANGES REPORT ===\n"
                text_content += f"Organization ID: {org_id}\n"
                text_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                text_content += f"Total Records: {len(config_changes)}\n"
                text_content += "=" * 50 + "\n\n"
                
                # Add each configuration change as raw text
                for i, change in enumerate(config_changes, 1):
                    text_content += f"--- Configuration Change #{i} ---\n"
                    text_content += f"Raw Data: {str(change)}\n"
                    text_content += "\n"
                
                # Store in session state for download
                st.session_state['config_changes_text'] = text_content
                st.session_state['config_changes_filename'] = f"meraki_config_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.rerun()
            else:
                st.warning("No configuration changes found or failed to load data")
    
    # Show download button if text content is ready
    if 'config_changes_text' in st.session_state:
        st.markdown("#### 📥 설정 변경 보고서 내보내기")
        st.download_button(
            label="📥 Download Configuration Changes as Text File",
            data=st.session_state['config_changes_text'],
            file_name=st.session_state['config_changes_filename'],
            mime="text/plain",
            key="download_config_changes",
            width='stretch'
        )
        
        # Clear the session state after showing download button
        if st.button("🗑️ 보고서 초기화", key="clear_config_report"):
            del st.session_state['config_changes_text']
            del st.session_state['config_changes_filename']
            st.rerun()

elif current_page == "라이센스 정보":
    st.header("📄 라이센스 정보 (조직 라이센스 현황 및 상세 정보)")
    
    # Load license data only when user visits this page (on-demand loading)
    print("=" * 60)
    print("ON-DEMAND LICENSE DATA LOADING")
    print("=" * 60)
    
    with st.spinner("라이센스 데이터 로딩 중..."):
        license_overview = load_license_overview(api_key, org_id)
    
    print(f"✅ License data loaded on-demand")
    print("=" * 60)
    
    # Add CSS to prevent text truncation in metrics and increase font size
    st.markdown("""
    <style>
    /* Prevent text truncation in metrics and increase font size */
    div[data-testid="stMetricValue"] {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricLabel"] {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    /* Increase column width for metrics */
    div[data-testid="column"] {
        min-width: 200px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # License Overview Section
    st.subheader("📊 라이센스 개요")
    
    
    if license_overview:
            
            # Display overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'status' in license_overview:
                    status = license_overview['status']
                    st.metric("📋 라이센스 상태", status)
            
            with col2:
                if 'expirationDate' in license_overview:
                    exp_date = license_overview['expirationDate']
                    # Format date for better display
                    if exp_date and exp_date != 'N/A':
                        try:
                            # Parse and format date
                            from datetime import datetime
                            parsed_date = datetime.fromisoformat(exp_date.replace('Z', '+00:00'))
                            formatted_date = parsed_date.strftime('%Y-%m-%d')
                        except:
                            formatted_date = exp_date
                    else:
                        formatted_date = exp_date
                    st.metric("📅 만료일", formatted_date)
            
            with col3:
                if 'licensedDeviceCounts' in license_overview:
                    device_counts = license_overview['licensedDeviceCounts']
                    total_devices = sum(device_counts.values()) if device_counts else 0
                    st.metric("🔢 총 라이센스 디바이스", total_devices)
            
            with col4:
                if 'usedDeviceCounts' in license_overview:
                    used_counts = license_overview['usedDeviceCounts']
                    total_used = sum(used_counts.values()) if used_counts else 0
                    st.metric("📱 사용 중인 디바이스", total_used)
            
            # Display license comparison table
            st.markdown("---")
            st.markdown("#### 📋 라이센스 개수")
            
            # Debug: Show what's in license_overview
            if SHOW_DEBUG_INFO:
                st.write("Debug - license_overview keys:", list(license_overview.keys()))
                st.write("Debug - license_overview values:", license_overview)
            
            # Create license comparison table
            license_data = []
            
            # Get licensed and used device counts
            licensed_counts = license_overview.get('licensedDeviceCounts', {})
            used_counts = license_overview.get('usedDeviceCounts', {})
            
            # Get all product types from both dictionaries
            all_products = set(licensed_counts.keys()) | set(used_counts.keys())
            
            for product in sorted(all_products):
                license_limit = licensed_counts.get(product, 0)
                current_count = used_counts.get(product, 0)
                
                # Format license limit (show "free" for 0, or specific number)
                if license_limit == 0:
                    limit_display = "무제한"
                else:
                    limit_display = str(license_limit)
                
                # Format current count
                if current_count == 0:
                    count_display = "0"
                else:
                    count_display = str(current_count)
                
                license_data.append({
                    "제품 타입": product,
                    "라이센스 개수": limit_display
                })
            
            if license_data:
                license_df = pd.DataFrame(license_data)
                # Make table smaller and center-aligned
                st.dataframe(
                    license_df, 
                    use_container_width=False,
                    hide_index=True,
                    column_config={
                        "제품 타입": st.column_config.TextColumn("제품 타입", width="medium"),
                        "라이센스 한도": st.column_config.TextColumn("라이센스 한도", width="small")
                    }
                )
            else:
                st.info("라이센스 개요에서 표시할 수 있는 데이터가 없습니다.")
                if SHOW_DEBUG_INFO:
                    st.write("Debug - license_data is empty")
                    st.write("Debug - licensed_counts:", licensed_counts)
                    st.write("Debug - used_counts:", used_counts)
    else:
        st.warning("⚠️ 라이센스 개요 정보를 가져올 수 없습니다")
        st.info("💡 가능한 원인:")
        st.write("• API 키에 라이센스 정보 접근 권한이 없을 수 있습니다")
        st.write("• 조직에 라이센스 정보가 없을 수 있습니다")
        st.write("• 네트워크 연결 문제일 수 있습니다")
        
        # Try to load with different methods
        st.write("🔄 다른 방법으로 라이센스 정보를 시도합니다...")
        try:
            # Try to get basic organization info
            api = init_api(api_key)
            if api:
                org_info = api.organizations.getOrganization(organizationId=org_id)
                st.write(f"조직 정보: {org_info.get('name', 'Unknown')}")
        except Exception as e:
            st.write(f"조직 정보 로딩 실패: {e}")
    
    # Detailed Licenses Section - Auto load with per_page=1000
    st.markdown("---")
    st.subheader("📋 상세 라이센스 목록")
    
    with st.spinner("상세 라이센스 정보를 로딩 중..."):
        detailed_licenses = load_detailed_licenses(api_key, org_id, per_page=1000)
        
        # Debug information
        if SHOW_DEBUG_INFO:
            st.write(f"Debug: detailed_licenses type: {type(detailed_licenses)}")
            st.write(f"Debug: detailed_licenses length: {len(detailed_licenses) if detailed_licenses else 'None'}")
            if detailed_licenses:
                st.write(f"Debug: First license sample: {detailed_licenses[0] if len(detailed_licenses) > 0 else 'Empty'}")
        
        if detailed_licenses:
            st.success(f"✅ {len(detailed_licenses)}개의 상세 라이센스 정보를 로드했습니다")
            
            # Create detailed licenses table
            licenses_data = []
            for license_info in detailed_licenses:
                # Extract editions information
                editions = license_info.get('editions', [])
                edition_info = ""
                if editions:
                    edition_list = []
                    for edition in editions:
                        edition_name = edition.get('edition', 'N/A')
                        product_type = edition.get('productType', 'N/A')
                        edition_list.append(f"{edition_name} ({product_type})")
                    edition_info = ", ".join(edition_list)
                else:
                    edition_info = "N/A"
                
                # Extract counts information
                counts = license_info.get('counts', [])
                count_info = ""
                if counts:
                    count_list = []
                    for count in counts:
                        model = count.get('model', 'N/A')
                        count_num = count.get('count', 0)
                        count_list.append(f"{model}: {count_num}")
                    count_info = ", ".join(count_list)
                else:
                    count_info = "N/A"
                
                licenses_data.append({
                    "라이센스 키": license_info.get('key', 'N/A'),
                    "기간 (일)": license_info.get('duration', 'N/A'),
                    "모드": license_info.get('mode', 'N/A'),
                    "시작일": parse_date(license_info.get('startedAt', 'N/A')),
                    "클레임일": parse_date(license_info.get('claimedAt', 'N/A')),
                    "에디션": edition_info,
                    "모델별 수량": count_info
                })
            
            licenses_df = pd.DataFrame(licenses_data)
            
            # Display the table
            st.dataframe(licenses_df, use_container_width=True, hide_index=True)

