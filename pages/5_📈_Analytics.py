import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.utils import IMPORTANT_FEATURES

def generate_sample_data(n_samples=1000):
    """Generate sample network traffic data for visualization"""
    now = datetime.now()
    data = {
        'timestamp': pd.date_range(end=now, periods=n_samples, freq='1min'),
        'total_bytes': np.random.exponential(1000, n_samples),
        'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], n_samples),
        'source_ip': [f"192.168.1.{np.random.randint(1, 255)}" for _ in range(n_samples)],
        'destination_ip': [f"10.0.0.{np.random.randint(1, 255)}" for _ in range(n_samples)],
        'threat_score': np.random.beta(2, 5, n_samples),  # Beta distribution for threat scores
    }
    
    # Add important features
    for feature in IMPORTANT_FEATURES:
        if feature not in data:
            data[feature] = np.random.uniform(0, 100, n_samples)
    
    return pd.DataFrame(data)

def create_time_series(data, title="Network Traffic Over Time"):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['timestamp'],
        y=data['total_bytes'],
        name='Traffic Volume',
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy',
        fillcolor='rgba(30,136,229,0.1)'
    ))
    
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_protocol_pie(data):
    counts = data['protocol'].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=.3,
        marker=dict(colors=['#1E88E5', '#64B5F6', '#BBDEFB'])
    )])
    
    fig.update_layout(
        title="Protocol Distribution",
        template="plotly_white",
        height=400
    )
    
    return fig

def show_analytics():
    st.title("📈 Network Traffic Analytics")
    
    # Generate sample data
    data = generate_sample_data()
    
    # Time range selector
    time_ranges = {
        "Last Hour": timedelta(hours=1),
        "Last 6 Hours": timedelta(hours=6),
        "Last 24 Hours": timedelta(hours=24),
        "Last Week": timedelta(days=7)
    }
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_range = st.select_slider(
            "📅 Time Range",
            options=list(time_ranges.keys()),
            value="Last Hour"
        )
    with col2:
        auto_refresh = st.toggle("🔄 Auto Refresh", value=False)
    
    # Filter data based on selected time range
    cutoff_time = datetime.now() - time_ranges[selected_range]
    filtered_data = data[data['timestamp'] >= cutoff_time]
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["📊 Traffic Analysis", "🔍 Protocol Analysis", "⚡ Feature Analysis"])
    
    with tab1:
        st.plotly_chart(create_time_series(filtered_data), use_container_width=True)
        
        # Traffic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_traffic = filtered_data['total_bytes'].mean()
            st.metric("Avg Traffic", f"{avg_traffic:.0f} bytes", 
                     delta=f"{(filtered_data['total_bytes'].mean() - data['total_bytes'].mean()):.0f}")
        with col2:
            peak_traffic = filtered_data['total_bytes'].max()
            st.metric("Peak Traffic", f"{peak_traffic:.0f} bytes")
        with col3:
            unique_ips = len(set(filtered_data['source_ip']) | set(filtered_data['destination_ip']))
            st.metric("Unique IPs", unique_ips)
    
    with tab2:
        st.plotly_chart(create_protocol_pie(filtered_data), use_container_width=True)
        
        # Protocol stats
        protocol_stats = filtered_data.groupby('protocol').agg({
            'total_bytes': ['count', 'mean', 'max'],
            'threat_score': 'mean'
        }).round(2)
        
        st.markdown("### Protocol Statistics")
        st.dataframe(protocol_stats.style.background_gradient(cmap='Blues'))
    
    with tab3:
        st.markdown("### Feature Importance Analysis")
        
        # Create feature correlation heatmap
        numeric_features = [f for f in IMPORTANT_FEATURES if f not in ['protocol', 'service']]
        feature_data = filtered_data[numeric_features]
        corr = feature_data.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmin=-1, zmax=1
        ))
        
        fig.update_layout(
            title="Feature Correlation Matrix",
            height=600,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show top features by variance
        st.markdown("### Top Features by Variance")
        numeric_data = filtered_data[numeric_features]
        variances = numeric_data.var().sort_values(ascending=False)
        
        fig = go.Figure(data=go.Bar(
            x=variances.index,
            y=variances.values,
            marker_color='#1E88E5'
        ))
        
        fig.update_layout(
            title="Feature Variance Distribution",
            xaxis_title="Feature",
            yaxis_title="Variance",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Initialize and show the page
show_analytics()
