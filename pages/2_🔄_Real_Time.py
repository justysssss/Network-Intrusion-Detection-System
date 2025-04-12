import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scapy.all import sniff, get_if_list, IP
from src.utils import process_packet, preprocess_data, load_scalers
from src.model_loader import load_model
from threading import Thread
from datetime import datetime, timedelta

# Initialize model and scalers
model = load_model()
if 'minmax_scaler' not in st.session_state or 'standard_scaler' not in st.session_state:
    st.session_state.minmax_scaler, st.session_state.standard_scaler = load_scalers()

# Initialize session state for monitoring
if 'packet_history' not in st.session_state:
    st.session_state.packet_history = pd.DataFrame()
if 'threat_history' not in st.session_state:
    st.session_state.threat_history = []
if 'total_packets' not in st.session_state:
    st.session_state.total_packets = 0
if 'threats_detected' not in st.session_state:
    st.session_state.threats_detected = 0

def get_available_interfaces():
    """Get list of available network interfaces with error handling"""
    try:
        interfaces = get_if_list()
        if not interfaces:
            return ["Simulation Mode"]
        return interfaces
    except Exception as e:
        st.info("Running in simulation mode due to limited network access")
        return ["Simulation Mode"]

def generate_simulated_packet():
    """Generate a simulated network packet for testing"""
    packet_data = pd.DataFrame({
        'protocol': [np.random.choice([6, 17])],  # TCP or UDP
        'sbytes': [np.random.randint(40, 1500)],
        'dbytes': [np.random.randint(40, 1500)],
        'rate': [np.random.uniform(1, 100)]
    })
    return packet_data

def create_network_chart(data, title="Network Traffic"):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=data['sbytes'],
        name='Source Bytes',
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy',
        fillcolor='rgba(30,136,229,0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        y=data['dbytes'],
        name='Destination Bytes',
        line=dict(color='#64B5F6', width=2),
        fill='tozeroy',
        fillcolor='rgba(100,181,246,0.1)'
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
        template="plotly_white",
        hovermode='x unified'
    )
    
    return fig

def show_real_time():
    st.title("🌐 Real-Time Network Monitoring")
    
    # Network interface selection with error handling
    interfaces = get_available_interfaces()
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        selected_interface = st.selectbox("🔌 Select Network Interface", interfaces)
    with col2:
        threshold = st.slider("🎯 Detection Threshold", 0.0, 1.0, 0.8, key="rt_threshold")
    with col3:
        interval = st.slider("⏱️ Update Interval (s)", 0.5, 5.0, 1.0, key="rt_interval")
    
    if selected_interface == "Simulation Mode":
        st.info("🔄 Running in simulation mode - generating synthetic network traffic")
    
    # Create main layout
    chart_col, stats_col = st.columns([3, 1])
    
    with stats_col:
        st.markdown("### 📊 Network Stats")
        monitoring = st.toggle("🚀 Start Monitoring", key="rt_monitor")
        
        # Stats metrics
        st.metric("Total Packets", f"{st.session_state.total_packets:,}", 
                 delta="Active" if monitoring else "Inactive")
        st.metric("Threats Detected", f"{st.session_state.threats_detected:,}",
                 delta="Scanning" if monitoring else None,
                 delta_color="inverse")
        
        # Health indicator
        health_score = 100 - (st.session_state.threats_detected / max(st.session_state.total_packets, 1) * 100)
        st.progress(health_score/100, text=f"Network Health: {health_score:.1f}%")
    
    with chart_col:
        chart_container = st.container()
        with chart_container:
            chart_placeholder = st.empty()
            alert_placeholder = st.empty()
    
    if monitoring:
        packet_buffer = []
        
        if selected_interface == "Simulation Mode":
            while monitoring:
                packet_data = generate_simulated_packet()
                packet_buffer.append(packet_data)
                
                if len(packet_buffer) >= 10:
                    live_data = pd.concat(packet_buffer, ignore_index=True)
                    packet_buffer = []
                    
                    # Update session state
                    st.session_state.total_packets += len(live_data)
                    
                    # Process and predict
                    processed = preprocess_data(live_data,
                                           st.session_state.minmax_scaler,
                                           st.session_state.standard_scaler)
                    prediction = model.predict(processed)
                    
                    # Update threat count
                    threats = sum(prediction > threshold)
                    st.session_state.threats_detected += threats
                    
                    # Update visualizations
                    fig = create_network_chart(live_data, "Live Traffic (Simulation)")
                    chart_placeholder.plotly_chart(fig, use_container_width=True)
                    
                    if threats > 0:
                        alert_placeholder.error(f"⚠️ {threats} potential threats detected!")
                        alerts = live_data[prediction > threshold]
                        alert_placeholder.dataframe(
                            alerts.style
                            .background_gradient(cmap='Reds')
                            .format({col: '{:.2f}' for col in alerts.select_dtypes('float').columns})
                        )
                    else:
                        alert_placeholder.success("✅ No threats detected")
                
                time.sleep(interval)

# Initialize and show the page
show_real_time()