import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# App Config
st.set_page_config(page_title="NIDS Dashboard", layout="wide", page_icon="🛡️")

# Apply custom CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%); color: white; border-radius: 10px; margin-bottom: 2rem;'>
    <h1 style='margin: 0; padding: 0;'>Network Security Center</h1>
    <p style='margin: 0; opacity: 0.9;'>Enterprise Network Monitoring & Threat Detection</p>
</div>
""", unsafe_allow_html=True)

# Security Status Overview
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metrics-container" style='text-align: center;'>
        <div style='font-size: 3rem; color: #28A745;'>✓</div>
        <h3 style='color: #1E88E5; margin: 0;'>Security Status</h3>
        <div style='font-size: 1.5rem; margin: 10px 0;'>Protected</div>
        <div style='color: #666;'>All systems operational</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metrics-container" style='text-align: center;'>
        <div style='font-size: 3rem; color: #28A745;'>0</div>
        <h3 style='color: #1E88E5; margin: 0;'>Active Threats</h3>
        <div style='font-size: 1.5rem; margin: 10px 0;'>No Threats</div>
        <div style='color: #666;'>Last checked: Just now</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metrics-container" style='text-align: center;'>
        <div style='font-size: 3rem; color: #1E88E5;'>99%</div>
        <h3 style='color: #1E88E5; margin: 0;'>Network Health</h3>
        <div style='font-size: 1.5rem; margin: 10px 0;'>Excellent</div>
        <div style='color: #666;'>All metrics normal</div>
    </div>
    """, unsafe_allow_html=True)

# Network Activity
st.markdown("""
<div class="section-header" style='margin-top: 2rem;'>
    <h2>Network Activity</h2>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

# Create sample network activity data
dates = pd.date_range(start='2025-04-12 00:00', end='2025-04-12 23:59', freq='1H')
activity_data = pd.DataFrame({
    'timestamp': dates,
    'traffic': np.random.normal(100, 20, size=len(dates)),
    'threats': np.random.poisson(2, size=len(dates))
})

# Create network activity chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=activity_data['timestamp'],
    y=activity_data['traffic'],
    name='Network Traffic',
    line=dict(color='#1E88E5', width=2),
    fill='tozeroy',
    fillcolor='rgba(30,136,229,0.1)'
))

fig.add_trace(go.Scatter(
    x=activity_data['timestamp'],
    y=activity_data['threats'],
    name='Threat Events',
    line=dict(color='#DC3545', width=2),
    yaxis='y2'
))

fig.update_layout(
    title='24-Hour Network Activity',
    xaxis=dict(title='Time'),
    yaxis=dict(title='Traffic (GB)', side='left'),
    yaxis2=dict(title='Threats', side='right', overlaying='y', showgrid=False),
    height=400,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# System Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metrics-container">
        <h3 style='color: #1E88E5;'>Protected Systems</h3>
        <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
            <div>
                <div style='font-size: 2rem; color: #1E88E5;'>156</div>
                <div style='color: #666;'>Monitored endpoints</div>
            </div>
            <div style='font-size: 2rem;'>💻</div>
        </div>
        <div style='color: #28A745;'>✓ All systems reporting</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metrics-container">
        <h3 style='color: #1E88E5;'>Security Events</h3>
        <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
            <div>
                <div style='font-size: 2rem; color: #1E88E5;'>24</div>
                <div style='color: #666;'>Events today</div>
            </div>
            <div style='font-size: 2rem;'>🛡️</div>
        </div>
        <div style='color: #28A745;'>✓ All events resolved</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metrics-container">
        <h3 style='color: #1E88E5;'>Network Traffic</h3>
        <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
            <div>
                <div style='font-size: 2rem; color: #1E88E5;'>2.5 TB</div>
                <div style='color: #666;'>Daily volume</div>
            </div>
            <div style='font-size: 2rem;'>📊</div>
        </div>
        <div style='color: #28A745;'>✓ Normal traffic patterns</div>
    </div>
    """, unsafe_allow_html=True)

# Quick Actions
st.markdown("""
<div class="section-header" style='margin-top: 2rem;'>
    <h2>Quick Actions</h2>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("🔍 Security Scan", key="scan", use_container_width=True)
with col2:
    st.button("📊 Generate Report", key="report", use_container_width=True)
with col3:
    st.button("🔄 Update Rules", key="rules", use_container_width=True)
with col4:
    st.button("⚙️ Settings", key="settings", use_container_width=True)

# Recent Activity
st.markdown("""
<div class="section-header" style='margin-top: 2rem;'>
    <h2>Recent Activity</h2>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

activity_data = [
    {"time": "2 mins ago", "event": "Security scan completed", "status": "success"},
    {"time": "15 mins ago", "event": "Threat definitions updated", "status": "success"},
    {"time": "1 hour ago", "event": "System backup completed", "status": "success"},
    {"time": "2 hours ago", "event": "Configuration changes applied", "status": "success"}
]

for activity in activity_data:
    st.markdown(f"""
    <div style='background: white; padding: 1rem; border-radius: 5px; margin-bottom: 0.5rem; border-left: 4px solid {"#28A745" if activity["status"] == "success" else "#DC3545"}'>
        <div style='display: flex; justify-content: space-between;'>
            <div>
                <span style='color: #666;'>{activity["time"]}</span>
                <span style='margin-left: 1rem;'>{activity["event"]}</span>
            </div>
            <div style='color: #28A745;'>✓</div>
        </div>
    </div>
    """, unsafe_allow_html=True)