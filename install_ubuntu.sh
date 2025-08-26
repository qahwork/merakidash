#!/bin/bash

# 🚀 Meraki Network Analytics Dashboard Pro - Ubuntu Server Installation Script
# Enhanced Network Performance & Analytics Platform

set -e  # Exit on any error

echo "🚀 Meraki Network Analytics Dashboard Pro - Ubuntu Server Installation"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget \
    nginx \
    supervisor \
    ufw \
    certbot \
    python3-certbot-nginx

# Create project directory
PROJECT_DIR="$HOME/meraki-dashboard"
print_status "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Create systemd service file
print_status "Creating systemd service for the dashboard..."
sudo tee /etc/systemd/system/meraki-dashboard.service > /dev/null <<EOF
[Unit]
Description=Meraki Network Analytics Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/streamlit run meraki_dashboard_complete_final.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/meraki-dashboard > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable Nginx site
print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/meraki-dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Start and enable services
print_status "Starting and enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable meraki-dashboard
sudo systemctl start meraki-dashboard
sudo systemctl restart nginx

# Create configuration file
print_status "Creating configuration file..."
if [ ! -f "config.py" ]; then
    cp config_example.py config.py
    print_warning "Configuration file created. Please edit config.py with your Meraki API key."
fi

# Create startup script
print_status "Creating startup script..."
tee start_dashboard.sh > /dev/null <<EOF
#!/bin/bash
cd "$PROJECT_DIR"
source venv/bin/activate
streamlit run meraki_dashboard_complete_final.py --server.port 8501 --server.address 0.0.0.0
EOF

chmod +x start_dashboard.sh

# Create status check script
print_status "Creating status check script..."
tee check_status.sh > /dev/null <<EOF
#!/bin/bash
echo "🔍 Checking Meraki Dashboard status..."
echo "====================================="

echo "📊 Dashboard Service Status:"
sudo systemctl status meraki-dashboard --no-pager -l

echo -e "\n🌐 Nginx Status:"
sudo systemctl status nginx --no-pager -l

echo -e "\n🔌 Port Status:"
sudo netstat -tlnp | grep :8501

echo -e "\n📁 Project Directory: $PROJECT_DIR"
echo -e "\n🐍 Python Version:"
source $PROJECT_DIR/venv/bin/activate
python --version

echo -e "\n📦 Installed Packages:"
pip list | grep -E "(streamlit|meraki|pandas|plotly)"
EOF

chmod +x check_status.sh

# Final instructions
echo ""
echo "🎉 Installation completed successfully!"
echo "====================================="
echo ""
echo "📋 Next steps:"
echo "1. Edit configuration: nano $PROJECT_DIR/config.py"
echo "2. Add your Meraki API key to config.py"
echo "3. Check status: ./check_status.sh"
echo "4. Access dashboard: http://$(curl -s ifconfig.me)"
echo ""
echo "🔧 Useful commands:"
echo "   Start dashboard: ./start_dashboard.sh"
echo "   Check status: ./check_status.sh"
echo "   View logs: sudo journalctl -u meraki-dashboard -f"
echo "   Restart service: sudo systemctl restart meraki-dashboard"
echo ""
echo "📚 For more information, check the README.md file"
echo ""
print_success "Meraki Dashboard is now running on your Ubuntu server!"
