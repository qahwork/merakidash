#!/usr/bin/env python3
"""
🚀 Meraki Network Analytics Dashboard Pro - Launch Script
Enhanced Network Performance & Analytics Platform

This script provides an easy way to launch the dashboard with proper configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['streamlit', 'meraki', 'pandas', 'plotly']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    dashboard_file = "meraki_dashboard_complete_final.py"
    
    if not Path(dashboard_file).exists():
        print(f"❌ Dashboard file '{dashboard_file}' not found")
        print("💡 Make sure you're in the correct directory")
        return False
    
    print("🚀 Launching Meraki Network Analytics Dashboard Pro...")
    print("📱 The dashboard will open in your default web browser")
    print("🔐 Enter your Meraki API key in the sidebar to start")
    print("🎭 Or enable Demo mode to test without hardware")
    print("\n" + "="*60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_file, "--server.port", "8501"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching dashboard: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🚀 Meraki Network Analytics Dashboard Pro")
    print("Enhanced Network Performance & Analytics Platform")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)
    
    # Launch dashboard
    if not launch_dashboard():
        print("\n❌ Failed to launch dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
