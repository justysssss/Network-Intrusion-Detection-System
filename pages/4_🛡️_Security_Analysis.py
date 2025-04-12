import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scapy.all import rdpcap
import io
import numpy as np
from datetime import datetime

def create_packet_summary(data):
    """Create a summary visualization for packet analysis"""
    fig = go.Figure()
    
    # Add protocol distribution
    protocols = data['protocol'].value_counts()
    fig.add_trace(go.Bar(
        x=protocols.index,
        y=protocols.values,
        name='Protocol Distribution',
        marker_color='#1E88E5'
    ))
    
    fig.update_layout(
        title="Protocol Distribution",
        xaxis_title="Protocol",
        yaxis_title="Count",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def analyze_packets(data):
    """Analyze packet data and return insights"""
    total_packets = len(data)
    avg_size = data['size'].mean()
    protocols = data['protocol'].value_counts()
    
    return {
        'total': total_packets,
        'avg_size': avg_size,
        'protocols': protocols
    }

def show_security_analysis():
    st.title("🛡️ Security Analysis")
    
    # Upload section
    st.markdown("""
    <div class="section-header">
        <h2>Packet Analysis</h2>
        <div class="divider"></div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a PCAP file for analysis", type=['pcap', 'pcapng'])
    
    if uploaded_file:
        # Create sample data (replace with actual PCAP parsing in production)
        num_packets = 1000
        sample_data = pd.DataFrame({
            'timestamp': [datetime.now() for _ in range(num_packets)],
            'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], num_packets),
            'source': [f'192.168.1.{np.random.randint(1, 255)}' for _ in range(num_packets)],
            'destination': [f'10.0.0.{np.random.randint(1, 255)}' for _ in range(num_packets)],
            'size': np.random.randint(64, 1500, num_packets),
            'flags': np.random.choice(['SYN', 'ACK', 'PSH', 'FIN'], num_packets)
        })
        
        # Security Overview
        st.markdown("""
        <div class="section-header">
            <h2>Security Overview</h2>
            <div class="divider"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metrics-container">
                <h3 style='color: #1E88E5; margin: 0;'>📦 Packets</h3>
                <h2 style='margin: 10px 0;'>1,000</h2>
                <p style='color: #666; margin: 0;'>Total analyzed</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metrics-container">
                <h3 style='color: #1E88E5; margin: 0;'>⚠️ Threats</h3>
                <h2 style='margin: 10px 0;'>15</h2>
                <p style='color: #666; margin: 0;'>Detected</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metrics-container">
                <h3 style='color: #1E88E5; margin: 0;'>🔍 Analysis</h3>
                <h2 style='margin: 10px 0;'>98%</h2>
                <p style='color: #666; margin: 0;'>Coverage</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="metrics-container">
                <h3 style='color: #1E88E5; margin: 0;'>📊 Risk Score</h3>
                <h2 style='margin: 10px 0;'>Low</h2>
                <p style='color: #666; margin: 0;'>Overall rating</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed Analysis Tabs
        st.markdown("""
        <div class="section-header">
            <h2>Detailed Analysis</h2>
            <div class="divider"></div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🔍 Traffic Analysis", "⚠️ Security Threats", "📊 Statistics"])
        
        with tab1:
            # Protocol distribution
            st.plotly_chart(create_packet_summary(sample_data), use_container_width=True)
            
            # Traffic patterns
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="metrics-container">
                    <h3>Top Sources</h3>
                    <ul>
                        <li>192.168.1.100 (25%)</li>
                        <li>192.168.1.150 (18%)</li>
                        <li>192.168.1.200 (15%)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="metrics-container">
                    <h3>Top Destinations</h3>
                    <ul>
                        <li>10.0.0.50 (30%)</li>
                        <li>10.0.0.25 (22%)</li>
                        <li>10.0.0.75 (12%)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("""
            <div class="metrics-container">
                <h3>Detected Threats</h3>
                <table style="width:100%">
                    <tr>
                        <th>Type</th>
                        <th>Count</th>
                        <th>Severity</th>
                    </tr>
                    <tr>
                        <td>Port Scan</td>
                        <td>5</td>
                        <td>🟡 Medium</td>
                    </tr>
                    <tr>
                        <td>DDoS Attempt</td>
                        <td>2</td>
                        <td>🔴 High</td>
                    </tr>
                    <tr>
                        <td>Suspicious Traffic</td>
                        <td>8</td>
                        <td>🟡 Medium</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Show threat details in a dataframe
            threats = sample_data.sample(15)  # Simulate threat data
            threats['threat_type'] = np.random.choice(['Port Scan', 'DDoS', 'Suspicious'], 15)
            threats['severity'] = np.random.choice(['High', 'Medium', 'Low'], 15)
            st.dataframe(
                threats,
                column_config={
                    "timestamp": "Time",
                    "source": "Source IP",
                    "destination": "Destination IP",
                    "threat_type": "Threat Type",
                    "severity": "Severity"
                },
                use_container_width=True
            )
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="metrics-container">
                    <h3>Protocol Statistics</h3>
                    <ul>
                        <li>TCP: 65%</li>
                        <li>UDP: 30%</li>
                        <li>ICMP: 5%</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="metrics-container">
                    <h3>Packet Sizes</h3>
                    <ul>
                        <li>Average: 782 bytes</li>
                        <li>Maximum: 1,500 bytes</li>
                        <li>Minimum: 64 bytes</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📤 Upload a PCAP file to begin security analysis")

# Show the security analysis page
show_security_analysis()