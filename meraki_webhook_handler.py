# Meraki Webhook Handler
# Handles incoming webhooks from Cisco Meraki dashboard
import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import hashlib
import hmac
import base64
import time

# Store webhook events in memory (for demo/development)
# In production, consider using a database
if 'webhook_events' not in st.session_state:
    st.session_state.webhook_events = []

def verify_webhook(data, shared_secret, signature):
    """
    Verify the webhook signature using the shared secret
    """
    if not shared_secret or not signature:
        return False
    
    # Calculate HMAC signature
    computed_hash = hmac.new(
        key=shared_secret.encode('utf-8'),
        msg=data.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    # Encode in base64
    computed_signature = base64.b64encode(computed_hash).decode()
    
    # Compare signatures
    return hmac.compare_digest(computed_signature, signature)

def process_webhook(webhook_data):
    """
    Process incoming webhook data
    """
    try:
        # Extract main webhook data
        alert_id = webhook_data.get("alertId", "Unknown")
        alert_type = webhook_data.get("alertType", "Unknown")
        alert_type_id = webhook_data.get("alertTypeId", "Unknown")
        alert_level = webhook_data.get("alertLevel", "informational")
        occurred_at = webhook_data.get("occurredAt")
        
        # Extract device information
        device_name = webhook_data.get("deviceName", "Unknown")
        device_serial = webhook_data.get("deviceSerial", "Unknown")
        device_model = webhook_data.get("deviceModel", "Unknown")
        device_mac = webhook_data.get("deviceMac", "Unknown")
        
        # Extract network information
        network_id = webhook_data.get("networkId", "Unknown")
        network_name = webhook_data.get("networkName", "Unknown")
        
        # Extract organization information
        org_id = webhook_data.get("organizationId", "Unknown")
        org_name = webhook_data.get("organizationName", "Unknown")
        
        # Extract alert data
        alert_data = webhook_data.get("alertData", {})
        
        # Format occurred_at as datetime if available
        timestamp = None
        if occurred_at:
            try:
                timestamp = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.now()  # Fallback to current time
        else:
            timestamp = datetime.now()
            
        # Create event record
        event = {
            "id": alert_id,
            "timestamp": timestamp,
            "type": alert_type,
            "type_id": alert_type_id,
            "level": alert_level,
            "device": {
                "name": device_name,
                "serial": device_serial,
                "model": device_model,
                "mac": device_mac
            },
            "network": {
                "id": network_id,
                "name": network_name
            },
            "organization": {
                "id": org_id,
                "name": org_name
            },
            "alert_data": alert_data,
            "raw_data": webhook_data
        }
        
        # Store event
        st.session_state.webhook_events.append(event)
        
        # Limit stored events (optional)
        if len(st.session_state.webhook_events) > 1000:
            st.session_state.webhook_events = st.session_state.webhook_events[-1000:]
        
        return True, event
    except Exception as e:
        return False, {"error": str(e)}

def get_webhook_events(max_events=100, filter_level=None, filter_type=None):
    """
    Get stored webhook events with optional filtering
    """
    events = st.session_state.webhook_events
    
    # Apply filters
    if filter_level:
        events = [e for e in events if e.get("level") == filter_level]
    if filter_type:
        events = [e for e in events if e.get("type_id") == filter_type]
    
    # Sort by timestamp (newest first)
    events = sorted(events, key=lambda x: x.get("timestamp", datetime.now()), reverse=True)
    
    # Limit number of events
    return events[:max_events]

def get_webhook_stats():
    """
    Get statistics about webhook events
    """
    events = st.session_state.webhook_events
    
    if not events:
        return {
            "total_count": 0,
            "level_counts": {},
            "type_counts": {},
            "network_counts": {},
            "device_counts": {},
            "latest_timestamp": None
        }
    
    # Count by level
    level_counts = {}
    for e in events:
        level = e.get("level", "unknown")
        level_counts[level] = level_counts.get(level, 0) + 1
    
    # Count by type
    type_counts = {}
    for e in events:
        alert_type = e.get("type", "unknown")
        type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
    
    # Count by network
    network_counts = {}
    for e in events:
        network_name = e.get("network", {}).get("name", "unknown")
        network_counts[network_name] = network_counts.get(network_name, 0) + 1
    
    # Count by device
    device_counts = {}
    for e in events:
        device_name = e.get("device", {}).get("name", "unknown")
        device_counts[device_name] = device_counts.get(device_name, 0) + 1
    
    # Get latest timestamp
    latest_timestamp = max([e.get("timestamp", datetime.fromtimestamp(0)) for e in events])
    
    return {
        "total_count": len(events),
        "level_counts": level_counts,
        "type_counts": type_counts,
        "network_counts": network_counts,
        "device_counts": device_counts,
        "latest_timestamp": latest_timestamp
    }

def render_webhooks_dashboard():
    """
    Render a dashboard for webhook events
    """
    st.header("🚨 Meraki Webhook Events")
    
    # Get webhook stats
    stats = get_webhook_stats()
    
    # Display summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", stats["total_count"])
    with col2:
        critical_count = stats["level_counts"].get("critical", 0)
        st.metric("Critical Events", critical_count, 
                 delta_color="inverse" if critical_count > 0 else "normal")
    with col3:
        warning_count = stats["level_counts"].get("warning", 0)
        st.metric("Warnings", warning_count,
                 delta_color="inverse" if warning_count > 0 else "normal")
    with col4:
        info_count = stats["level_counts"].get("informational", 0)
        st.metric("Info Events", info_count)
    
    # Show latest event time
    if stats["latest_timestamp"]:
        latest_time_str = stats["latest_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        st.info(f"Latest event received: {latest_time_str}")
    
    # Filter options
    st.subheader("Event Filters")
    col1, col2 = st.columns(2)
    with col1:
        level_filter = st.selectbox("Filter by Level", 
                                   ["All"] + list(stats["level_counts"].keys()),
                                   key="webhook_level_filter")
    with col2:
        type_filter = st.selectbox("Filter by Type",
                                  ["All"] + list(stats["type_counts"].keys()),
                                  key="webhook_type_filter")
    
    # Apply filters
    filter_level = None if level_filter == "All" else level_filter
    filter_type = None if type_filter == "All" else type_filter
    
    # Get filtered events
    filtered_events = get_webhook_events(filter_level=filter_level, filter_type=filter_type)
    
    # Display events
    st.subheader(f"Events ({len(filtered_events)})")
    
    if not filtered_events:
        st.info("No webhook events received yet.")
        return
    
    # Create a dataframe for easier display
    event_rows = []
    for event in filtered_events:
        event_rows.append({
            "Time": event.get("timestamp").strftime("%Y-%m-%d %H:%M:%S") if event.get("timestamp") else "Unknown",
            "Level": event.get("level", "Unknown"),
            "Type": event.get("type", "Unknown"),
            "Device": event.get("device", {}).get("name", "Unknown"),
            "Network": event.get("network", {}).get("name", "Unknown"),
            "ID": event.get("id", "Unknown")
        })
    
    events_df = pd.DataFrame(event_rows)
    st.dataframe(events_df, use_container_width=True, hide_index=True)
    
    # Event details section
    st.subheader("Event Details")
    selected_event_id = st.selectbox("Select Event", 
                                    [f"{e['id']} - {e['type']} ({e['timestamp'].strftime('%H:%M:%S')})" 
                                     if e.get("timestamp") else f"{e['id']} - {e['type']}"
                                     for e in filtered_events],
                                    key="webhook_event_selector")
    
    # Extract event ID from selection
    selected_id = selected_event_id.split(" - ")[0]
    
    # Find the selected event
    selected_event = next((e for e in filtered_events if e["id"] == selected_id), None)
    
    if selected_event:
        # Display event details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Event Information")
            st.write(f"**ID:** {selected_event['id']}")
            st.write(f"**Type:** {selected_event['type']}")
            st.write(f"**Level:** {selected_event['level']}")
            if selected_event.get("timestamp"):
                st.write(f"**Time:** {selected_event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.markdown("### Device & Network")
            st.write(f"**Device:** {selected_event['device']['name']}")
            st.write(f"**Model:** {selected_event['device']['model']}")
            st.write(f"**Serial:** {selected_event['device']['serial']}")
            st.write(f"**Network:** {selected_event['network']['name']}")
        
        # Alert data (if any)
        if selected_event.get("alert_data"):
            st.markdown("### Alert Data")
            for key, value in selected_event["alert_data"].items():
                st.write(f"**{key}:** {value}")
        
        # Raw data (for debugging)
        with st.expander("Raw Data"):
            st.json(selected_event["raw_data"])

def create_webhook_endpoint(app, api_key=None, webhook_secret=None):
    """
    Create a webhook endpoint for the Streamlit app
    This is typically used with a framework like Flask
    """
    # This is a placeholder - actual implementation depends on your deployment strategy
    pass


