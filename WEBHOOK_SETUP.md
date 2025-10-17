# Meraki Webhook Integration Setup

This guide explains how to set up and use the Cisco Meraki webhook integration with the Meraki Network Analytics Dashboard.

## Overview

The webhook integration allows the dashboard to receive real-time alerts and events from the Cisco Meraki cloud. This provides immediate notification of network changes, device status updates, security alerts, and more without having to poll the API.

## Configuration

1. Edit your `config.py` file and ensure the webhook settings are properly configured:

```python
# Webhook Configuration
WEBHOOK_ENABLED = True  # Enable webhook receiver
WEBHOOK_SECRET = "your_webhook_secret_here"  # Shared secret for webhook validation
WEBHOOK_STORE_EVENTS = 1000  # Maximum number of events to store in memory
```

2. Replace `your_webhook_secret_here` with a secure random string. This will be used to validate incoming webhooks from Cisco Meraki.

## Webhook Receiver

The webhook receiver runs as a separate process within the dashboard application. By default, it listens on port 5000. You'll need to make this endpoint accessible from the internet so that the Meraki cloud can send webhooks to it.

Options include:
- Deploying the application to a cloud server with a public IP address
- Using a tunneling service like ngrok to expose the endpoint
- Setting up a reverse proxy to forward webhooks to your application

## Setting Up Webhooks in Meraki Dashboard

1. Log in to your Cisco Meraki Dashboard
2. Navigate to Network-wide > Configure > Alerts
3. Scroll down to the "Webhooks" section and click "Add a webhook"
4. Configure the webhook with:
   - Name: A descriptive name for your webhook (e.g., "Analytics Dashboard")
   - URL: The public URL of your webhook endpoint (e.g., `https://your-server.com:5000/webhook` or your ngrok URL)
   - Shared Secret: The same secret you configured in `config.py`
5. Select which alert types you want to receive
6. Save your settings

## Testing the Integration

1. Start your dashboard application
2. Navigate to the "웹훅 이벤트" tab
3. You should see a message indicating that the webhook receiver is running
4. When events occur in your Meraki network, they will appear in this tab

To test manually, you can generate test events in the Meraki dashboard or use the webhook verification tool from Cisco Meraki.

## Data Fields

The webhook integration captures the following fields from Meraki alerts:

- **alertId**: Unique identifier for the alert
- **alertType**: Human-readable description of the alert type
- **alertTypeId**: Machine-readable identifier for the alert type
- **alertLevel**: Severity level (informational, warning, critical)
- **deviceName**, **deviceSerial**, **deviceModel**: Information about the device that triggered the alert
- **networkId**, **networkName**: Information about the network
- **organizationId**, **organizationName**: Information about the organization
- **alertData**: Additional data specific to the alert type (varies)
- **occurredAt**: When the alert occurred

## Visualization

The webhook dashboard provides:

1. Summary statistics of received events
2. Distribution of events by level and type
3. Timeline of event activity
4. Detailed event viewer
5. Network and device event distribution

## Limitations

- Events are stored in memory and will be lost if the application restarts
- For production use, consider implementing persistent storage for events
- The webhook receiver must be accessible from the internet to receive alerts

## Troubleshooting

If you're not receiving webhooks:

1. Check that `WEBHOOK_ENABLED` is set to `True` in your config
2. Verify your webhook URL is accessible from the internet
3. Check that the shared secret matches between config and Meraki dashboard
4. Look for any errors in the application logs
5. Use the Meraki webhook testing tool to verify your endpoint


