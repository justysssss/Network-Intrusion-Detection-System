import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scapy.all import sniff, IP, TCP, UDP, conf
from scapy.arch import get_windows_if_list
from src.utils import process_packet, preprocess_data, load_scalers
from src.model_loader import load_model
from threading import Thread
from datetime import datetime, timedelta
import psutil

# Initialize model and scalers
model = load_model()
if 'minmax_scaler' not in st.session_state or 'standard_scaler' not in st.session_state:
    st.session_state.minmax_scaler, st.session_state.standard_scaler = load_scalers()

# Initialize session state for monitoring
if 'packet_history' not in st.session_state:
    st.session_state.packet_history = []
if 'threat_history' not in st.session_state:
    st.session_state.threat_history = []
if 'total_packets' not in st.session_state:
    st.session_state.total_packets = 0
if 'threats_detected' not in st.session_state:
    st.session_state.threats_detected = 0

def get_available_interfaces():
    """Get list of available network interfaces"""
    interfaces = []
    
    # Try using Windows-specific interface list
    try:
        windows_interfaces = get_windows_if_list()
        interfaces = [iface['name'] for iface in windows_interfaces]
        interfaces = [iface for iface in interfaces if iface != 'lo']
    except:
        pass
    
    # Fallback to psutil if Windows-specific method fails
    if not interfaces:
        try:
            net_if_stats = psutil.net_if_stats()
            interfaces = [iface for iface, stats in net_if_stats.items() 
                        if iface != 'lo' and stats.isup]
        except:
            pass
    
    # If no interfaces found
    if not interfaces:
        st.warning("⚠️ Running with limited network access. Please ensure you have appropriate permissions.")
        # Use Windows common interface names as fallback
        interfaces = ["Wi-Fi", "Ethernet", "Local Area Connection"]
    
    return interfaces

def create_network_chart(data, title="Network Traffic"):
    """Create a network traffic visualization"""
    if not data:
        return None

    df = pd.DataFrame(data[-100:])  # Keep last 100 packets for visualization
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['size'],
        name='Packet Size',
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy',
        fillcolor='rgba(30,136,229,0.1)'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Packet Size (bytes)",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def show_real_time():
    st.title("🌐 Network Monitor")
    
    # Network interface selection
    interfaces = get_available_interfaces()
    
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        selected_interface = st.selectbox(
            "🔌 Select Network Interface", 
            interfaces,
            help="Choose the network interface to monitor. You may need to run with administrator privileges."
        )
    with col2:
        threshold = st.slider("🎯 Detection Threshold", 0.0, 1.0, 0.8, key="rt_threshold")
    with col3:
        interval = st.slider("⏱️ Update Interval (s)", 0.5, 5.0, 1.0, key="rt_interval")
    
    # Main layout
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
    
    # Threats Table
    st.markdown("""
    <div class="section-header" style='margin-top: 2rem;'>
        <h2>Detected Threats</h2>
        <div class="divider"></div>
    </div>
    """, unsafe_allow_html=True)
    
    threats_table = st.empty()
    
    if monitoring:
        try:
            def packet_callback(packet):
                if IP in packet:
                    # Extract packet information
                    packet_info = {
                        'timestamp': datetime.now(),
                        'source_ip': packet[IP].src,
                        'dest_ip': packet[IP].dst,
                        'protocol': packet[IP].proto,
                        'size': len(packet),
                        'source_port': packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else 0,
                        'dest_port': packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else 0,
                        'flags': str(packet[TCP].flags) if TCP in packet else 'N/A'
                    }
                    
                    st.session_state.packet_history.append(packet_info)
                    st.session_state.total_packets += 1
                    
                    # Process for threat detection
                    features = process_packet(packet)
                    processed = preprocess_data(features,
                                           st.session_state.minmax_scaler,
                                           st.session_state.standard_scaler)
                    
                    try:
                        prediction = model.predict(processed)
                        if prediction > threshold:
                            st.session_state.threats_detected += 1
                            packet_info['threat_score'] = float(prediction)
                            st.session_state.threat_history.append(packet_info)
                    except Exception as e:
                        st.error(f"Prediction error: {str(e)}")

            # Start packet capture in a separate thread
            try:
                # Disable unnecessary features
                conf.use_pcap = False
                conf.use_bpf = False
                
                # Try to start sniffing
                st.info("Starting packet capture... This may take a few moments.")
                sniff_thread = Thread(target=lambda: sniff(
                    iface=selected_interface,
                    prn=packet_callback,
                    store=False
                ))
                sniff_thread.daemon = True
                sniff_thread.start()
                st.success(f"✅ Successfully started monitoring on interface: {selected_interface}")
            except Exception as e:
                st.error(f"❌ Error starting packet capture: {str(e)}\n\nTry running with administrator privileges.")
                monitoring = False
                return
            
            while monitoring:
                # Update traffic chart
                if st.session_state.packet_history:
                    fig = create_network_chart(st.session_state.packet_history)
                    if fig:
                        chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Update threat table
                if st.session_state.threat_history:
                    df = pd.DataFrame(st.session_state.threat_history[-50:])  # Show last 50 threats
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp', ascending=False)
                    
                    # Format the dataframe
                    df['threat_score'] = df['threat_score'].apply(lambda x: f"{x:.2%}")
                    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    threats_table.dataframe(
                        df,
                        column_config={
                            "timestamp": "Time",
                            "source_ip": "Source IP",
                            "source_port": "Source Port",
                            "dest_ip": "Destination IP",
                            "dest_port": "Destination Port",
                            "protocol": "Protocol",
                            "size": "Size (bytes)",
                            "flags": "Flags",
                            "threat_score": "Threat Score"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                
                time.sleep(interval)
                
        except Exception as e:
            st.error(f"Error monitoring network: {str(e)}\n\nTry running with administrator privileges.")
            monitoring = False

# Show the network monitoring page
show_real_time()