#!/bin/bash

# Meraki Network Analytics Dashboard Pro - Ubuntu Server Deployment Script
# ========================================================================
# This script automates the deployment on Ubuntu Server
# ========================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DASHBOARD_PORT=8501
NGINX_PORT=80
NGINX_SSL_PORT=443
WEBHOOK_PORT=8080
PROJECT_NAME="meraki-dashboard"

# Functions
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
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons"
        print_status "Please run as a regular user with sudo privileges"
        exit 1
    fi
}

# Check if user has sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo privileges"
        print_status "Please ensure your user has sudo access"
        exit 1
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System packages updated"
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        print_status "Docker is already installed"
        return
    fi
    
    print_status "Installing Docker..."
    
    # Remove old versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Install prerequisites
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully"
    print_warning "Please log out and log back in for group changes to take effect"
}

# Install Docker Compose
install_docker_compose() {
    if command -v docker compose &> /dev/null; then
        print_status "Docker Compose is already installed"
        return
    fi
    
    print_status "Installing Docker Compose..."
    sudo apt install -y docker-compose-plugin
    print_success "Docker Compose installed successfully"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p ssl
    mkdir -p data
    mkdir -p nginx/conf.d
    
    print_success "Directories created"
}

# Create configuration file
create_config() {
    if [ -f "config.py" ]; then
        print_status "Configuration file already exists"
        return
    fi
    
    print_status "Creating configuration file..."
    cp config_example.py config.py
    
    print_warning "Please edit config.py and set your Meraki API key:"
    print_status "nano config.py"
    print_status "Set MERAKI_API_KEY = 'your_actual_api_key_here'"
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    sudo tee /etc/systemd/system/meraki-dashboard.service > /dev/null <<EOF
[Unit]
Description=Meraki Network Analytics Dashboard
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable meraki-dashboard.service
    
    print_success "Systemd service created and enabled"
}

# Setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    if command -v ufw &> /dev/null; then
        sudo ufw allow $NGINX_PORT/tcp
        sudo ufw allow $NGINX_SSL_PORT/tcp
        sudo ufw allow $DASHBOARD_PORT/tcp
        sudo ufw allow $WEBHOOK_PORT/tcp
        print_success "Firewall rules added"
    else
        print_warning "UFW not found, please configure firewall manually"
    fi
}

# Build and start containers
start_containers() {
    print_status "Building and starting containers..."
    
    # Build the image
    docker compose build --no-cache
    
    # Start the services
    docker compose up -d
    
    print_success "Containers started successfully"
}

# Show status
show_status() {
    print_status "Checking container status..."
    docker compose ps
    
    print_status "Checking logs..."
    docker compose logs --tail=20 meraki-dashboard
}

# Main deployment function
main() {
    print_status "Starting Meraki Dashboard deployment on Ubuntu Server..."
    
    check_root
    check_sudo
    update_system
    install_docker
    install_docker_compose
    create_directories
    create_config
    create_systemd_service
    setup_firewall
    start_containers
    show_status
    
    print_success "Deployment completed successfully!"
    print_status "Dashboard should be available at: http://localhost:$NGINX_PORT"
    print_status "Direct access: http://localhost:$DASHBOARD_PORT"
    print_status ""
    print_status "Useful commands:"
    print_status "  View logs: docker compose logs -f"
    print_status "  Stop services: docker compose down"
    print_status "  Start services: docker compose up -d"
    print_status "  Restart services: docker compose restart"
    print_status "  System service: sudo systemctl start/stop/restart meraki-dashboard"
}

# Run main function
main "$@"
