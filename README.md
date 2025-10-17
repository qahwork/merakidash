# 🚀 Meraki Network Analytics Dashboard Pro

**Enhanced Network Performance & Analytics Platform**

A professional-grade Streamlit application for comprehensive Meraki network monitoring, traffic analysis, and performance insights.

## ✨ Features

### 🔐 **Enhanced API Integration**
- **Secure API Key Management** with password masking
- **Demo Mode** for testing without hardware
- **Real-time Connection Status** monitoring
- **Enhanced Error Handling** with troubleshooting tips

### 📊 **Advanced Analytics Dashboard**
- **Real-time Network Overview** with health metrics
- **Enhanced Traffic Analysis** with application insights
- **Client Usage Analytics** with behavior patterns
- **Switch Port Monitoring** with detailed statistics
- **Advanced Bandwidth Analysis** for MX appliances

### 🎨 **Professional User Experience**
- **Modern UI Design** with intuitive navigation
- **Responsive Layout** optimized for all screen sizes
- **Interactive Charts** with Plotly and enhanced visualizations
- **Expandable Sections** for detailed information
- **Enhanced Sidebar** with configuration options

### 🔧 **Advanced Configuration**
- **Flexible Time Ranges** from 1 hour to 1 month
- **Configurable Data Resolution** for performance optimization
- **Feature Toggles** for selective functionality
- **Auto-refresh Options** with customizable intervals

## 🚀 Quick Start

### 1. Installation

#### **Option A: Docker Deployment (Recommended for Production)**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/meraki-dashboard-pro.git
cd meraki-dashboard-pro

# Copy configuration template
cp config_example.py config.py

# Edit configuration with your API key
nano config.py

# Deploy with Docker Compose
docker compose up -d
```

#### **Option B: Local Development**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/meraki-dashboard-pro.git
cd meraki-dashboard-pro

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp config_example.py config.py

# Edit configuration with your API key
nano config.py

# Run the application
streamlit run meraki_dashboard_complete_final.py
```

#### **Option C: Ubuntu Server Deployment**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/meraki-dashboard-pro.git
cd meraki-dashboard-pro

# Run automated deployment script
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

### 2. Configuration

#### **Option A: Configuration File (Recommended)**
1. **Copy the example config**:
   ```bash
   cp config_example.py config.py
   ```

2. **Edit config.py** and set your API key:
   ```python
   MERAKI_API_KEY = "your_actual_api_key_here"
   ```

3. **Customize other settings** as needed

#### **Option B: Direct Code Modification**
1. **Edit the dashboard file** directly:
   ```python
   MERAKI_API_KEY = "your_actual_api_key_here"
   ```

2. **Get Your Meraki API Key**:
   - Log into [Meraki Dashboard](https://dashboard.meraki.com)
   - Go to Organization > Settings > API access
   - Generate a new API key

3. **Run the Dashboard**:
   ```bash
   streamlit run meraki_dashboard_complete_final.py
   ```

### 3. Demo Mode

- **Enable Demo Mode** in the sidebar for testing
- **Realistic Network Simulation** without hardware
- **All Features Available** for exploration

## 📊 Dashboard Sections

### 🏢 **Organization Overview**
- **Connection Status** and API health
- **Network Discovery** with device counts
- **Real-time Metrics** and performance indicators

### 📈 **Network Analytics**
- **Device Status Distribution** with health percentages
- **Product Type Analysis** with visual charts
- **Firmware Version Tracking** across devices
- **Network Performance Insights**

### 🌐 **Traffic Analysis**
- **Application Traffic Patterns** with usage metrics
- **User Activity Analysis** with client counts
- **Traffic Distribution** (upload vs download)
- **Performance Optimization** recommendations

### 👥 **Client Analytics**
- **Individual Client Usage** with session tracking
- **Behavior Pattern Analysis** over time
- **Heavy vs Light User** identification
- **Time Series Usage** visualization

### 🔌 **Switch Port Monitoring**
- **Port Status Overview** with connection counts
- **Performance Metrics** (speed, errors, warnings)
- **Power Usage** and traffic statistics
- **Detailed Port Tables** with filtering

### 📊 **Advanced Bandwidth**
- **WAN Interface Performance** (primary/secondary)
- **VPN Tunnel Analytics** with quality metrics
- **Load Balancing Efficiency** analysis
- **Peak vs Average** usage patterns

## ⚙️ Configuration Options

### **Time Ranges**
- **1 Hour**: Real-time monitoring
- **2 Hours**: Short-term trends
- **24 Hours**: Daily patterns
- **3 Days**: Multi-day analysis
- **1 Week**: Weekly trends
- **1 Month**: Long-term insights

### **Data Resolution**
- **1 Minute**: High precision, real-time
- **5 Minutes**: Balanced detail & performance
- **15 Minutes**: Trend analysis focused
- **1 Hour**: Hourly patterns
- **1 Day**: Daily summaries

### **Feature Toggles**
- **Advanced Metrics**: Comprehensive performance data
- **Traffic Analysis**: Application and traffic insights
- **Client Analysis**: Individual usage patterns
- **Switch Monitoring**: Port-level statistics

## 🔧 Troubleshooting

### **Common Issues**

#### **API Connection Problems**
- Verify API key is correct and active
- Check network connectivity
- Ensure API key has proper permissions
- Check for rate limiting

#### **No Data Available**
- Enable traffic analytics in Meraki Dashboard
- Wait 5-10 minutes for data collection
- Verify network supports required features
- Check API permissions

#### **Performance Issues**
- Use appropriate time ranges
- Select suitable data resolution
- Enable only needed features
- Clear cache if needed

### **Getting Help**

1. **Check Documentation**: Expand sidebar help sections
2. **Verify Settings**: Ensure proper configuration
3. **Test with Demo Mode**: Verify functionality
4. **Review Error Messages**: Check console for details

## 🎯 Best Practices

### **For Network Administrators**
- **Regular Monitoring**: Set up auto-refresh for critical networks
- **Performance Baselines**: Use historical data for capacity planning
- **Alert Monitoring**: Watch for offline devices and performance issues
- **Traffic Optimization**: Identify bandwidth-heavy applications

### **For IT Teams**
- **Client Behavior**: Understand usage patterns for support
- **Capacity Planning**: Use peak vs average analysis
- **Troubleshooting**: Leverage detailed port and device data
- **Reporting**: Export data for management presentations

## 🔒 Security Features

- **API Key Protection** with password masking
- **Secure Data Handling** with proper authentication
- **Demo Mode** for safe testing
- **Permission-based Access** control

## 📱 Browser Compatibility

- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Mobile**: Responsive design support

## 🚀 Future Enhancements

- **Export Functionality** for reports
- **Custom Alerts** and notifications
- **Advanced Machine Learning** insights
- **Integration APIs** for other tools
- **Mobile App** version

## 🚀 Deployment

### **Ubuntu Server Deployment**

For production deployment on Ubuntu Server, use our automated deployment script:

```bash
# Clone and deploy
git clone https://github.com/YOUR_USERNAME/meraki-dashboard-pro.git
cd meraki-dashboard-pro
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

### **Docker Deployment**

```bash
# Using Docker Compose
docker compose up -d

# Using Docker directly
docker build -t meraki-dashboard .
docker run -p 8501:8501 -v $(pwd)/config.py:/app/config.py meraki-dashboard
```

### **Service Management**

```bash
# Start services
sudo systemctl start meraki-dashboard

# Stop services
sudo systemctl stop meraki-dashboard

# View logs
docker compose logs -f

# Restart services
docker compose restart
```

### **Access URLs**

- **Dashboard**: `http://your-server-ip:8501`
- **Nginx Proxy**: `http://your-server-ip` (port 80)
- **HTTPS**: `https://your-domain.com` (with SSL)

For detailed deployment instructions, see [GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md).

## 🎨 Customization

### **Company Branding**
- Add your company logo
- Customize company name and colors
- Modify login page design
- Set up organization filtering

### **Quick Setup**
1. **Copy configuration template**:
   ```bash
   cp config_example.py config.py
   ```

2. **Edit config.py** with your settings:
   ```python
   # API Configuration
   MERAKI_API_KEY = "your_meraki_api_key_here"
   
   # Login Configuration
   LOGIN_USERNAME = "your_username"
   LOGIN_PASSWORD = "your_secure_password"
   
   # Company Branding
   COMPANY_LOGO_PATH = "your_company_logo.png"
   COMPANY_NAME = "Your Company Name"
   COMPANY_TAGLINE = "Your Company Tagline"
   
   # Organization Management
   DEFAULT_ORGANIZATION = "your_org_id"
   ALLOWED_ORGANIZATION_IDS = ["org1", "org2", "org3"]
   ```

3. **Add your company logo** to the project root

4. **Run the application**:
   ```bash
   streamlit run meraki_dashboard_complete_final.py
   ```

For detailed customization instructions, see [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md).

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Cisco Meraki** for the excellent API
- **Streamlit** for the amazing web framework
- **Plotly** for beautiful visualizations
- **Open Source Community** for inspiration

---

**🚀 Built with ❤️ for Network Administrators Worldwide**

*For support, questions, or feature requests, please open an issue on GitHub.*
