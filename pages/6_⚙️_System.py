import streamlit as st
import psutil
import platform
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def get_system_info():
    """Get detailed system information"""
    return {
        "OS": f"{platform.system()} {platform.version()}",
        "Architecture": platform.machine(),
        "Python Version": platform.python_version(),
        "CPU Cores": psutil.cpu_count(),
        "Total Memory": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
        "Total Disk": f"{psutil.disk_usage('/').total / (1024**3):.1f} GB"
    }

def create_gauge_chart(value, title, max_value=100):
    """Create a gauge chart for system metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': "rgba(30,136,229,0.8)"},
            'bgcolor': "white",
            'steps': [
                {'range': [0, max_value/3], 'color': "#E8F5E9"},
                {'range': [max_value/3, max_value*2/3], 'color': "#FFF3E0"},
                {'range': [max_value*2/3, max_value], 'color': "#FFEBEE"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value*0.8
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig

def create_line_chart(data, title):
    """Create a line chart for time series data"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        name=title,
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy',
        fillcolor='rgba(30,136,229,0.1)'
    ))
    
    fig.update_layout(
        title=title,
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def show_system():
    st.title("⚙️ System Monitor")
    
    # System Information
    st.markdown("### 💻 System Information")
    sys_info = get_system_info()
    
    cols = st.columns(3)
    for i, (key, value) in enumerate(sys_info.items()):
        with cols[i % 3]:
            st.info(f"**{key}**: {value}")
    
    # Resource Usage
    st.markdown("### 📊 Resource Usage")
    
    # Initialize history in session state if not exists
    if 'cpu_history' not in st.session_state:
        st.session_state.cpu_history = []
    if 'memory_history' not in st.session_state:
        st.session_state.memory_history = []
    
    # Current Usage
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Update history
    st.session_state.cpu_history.append(cpu_percent)
    st.session_state.memory_history.append(memory.percent)
    
    # Keep last 60 readings
    st.session_state.cpu_history = st.session_state.cpu_history[-60:]
    st.session_state.memory_history = st.session_state.memory_history[-60:]
    
    # Display gauges
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(create_gauge_chart(cpu_percent, "CPU Usage %"), use_container_width=True)
    with col2:
        st.plotly_chart(create_gauge_chart(memory.percent, "Memory Usage %"), use_container_width=True)
    with col3:
        st.plotly_chart(create_gauge_chart(disk.percent, "Disk Usage %"), use_container_width=True)
    
    # Display history charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_line_chart(st.session_state.cpu_history, "CPU History"), use_container_width=True)
    with col2:
        st.plotly_chart(create_line_chart(st.session_state.memory_history, "Memory History"), use_container_width=True)
    
    # Network Interfaces
    st.markdown("### 🌐 Network Interfaces")
    
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    
    for interface, addresses in net_if_addrs.items():
        if interface in net_if_stats:
            stats = net_if_stats[interface]
            with st.expander(f"Interface: {interface}"):
                st.write(f"Status: {'🟢 Up' if stats.isup else '🔴 Down'}")
                st.write(f"Speed: {stats.speed} Mbps")
                st.write("Addresses:")
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        st.write(f"- IPv4: {addr.address}")
                    elif addr.family == 23:  # IPv6
                        st.write(f"- IPv6: {addr.address}")
    
    # Auto-refresh
    if st.toggle("🔄 Auto Refresh", value=False, key="system_auto_refresh"):
        st.empty()
        st.rerun()

# Initialize and show the page
show_system()