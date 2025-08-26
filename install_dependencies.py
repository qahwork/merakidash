#!/usr/bin/env python3
"""
🔧 Meraki Dashboard - Dependency Installer
Simple script to install required packages for the dashboard
"""

import subprocess
import sys

def install_package(package):
    """Install a single package using pip."""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Main installation function."""
    print("🚀 Meraki Network Analytics Dashboard Pro")
    print("🔧 Dependency Installation Script")
    print("=" * 50)
    
    # Core required packages
    required_packages = [
        "streamlit>=1.28.0",
        "meraki>=1.35.0", 
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.17.0"
    ]
    
    # Optional packages
    optional_packages = [
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "openpyxl>=3.1.0"
    ]
    
    print("\n📋 Installing required packages...")
    failed_packages = []
    
    for package in required_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("💡 Try installing manually with: pip install <package_name>")
        return False
    
    print("\n📋 Installing optional packages...")
    for package in optional_packages:
        install_package(package)
    
    print("\n🎉 Installation complete!")
    print("💡 You can now run the dashboard with:")
    print("   streamlit run meraki_dashboard_complete_final.py")
    print("   or")
    print("   python run_dashboard.py")
    
    return True

if __name__ == "__main__":
    main()
