import streamlit as st
import torch
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def generate_sample_packets(n_samples=100):
    """Generate sample packet data for visualization"""
    # Generate timestamps
    now = datetime.now()
    timestamps = [now - timedelta(seconds=i) for i in reversed(range(n_samples))]
    
    # Generate random packet data using PyTorch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Generate good packets (normal distribution)
    good_packets = torch.normal(mean=0.3, std=0.1, size=(n_samples,)).to(device)
    good_packets = torch.clamp(good_packets, 0, 1)
    
    # Generate bad packets (occasional spikes)
    bad_packets = torch.zeros(n_samples).to(device)
    spike_indices = torch.randint(0, n_samples, (n_samples//10,))
    bad_packets[spike_indices] = torch.rand(len(spike_indices)) * 0.8 + 0.2
    
    return timestamps, good_packets.cpu().numpy(), bad_packets.cpu().numpy()

def show_packets():
    st.title("Packet Analysis")
    
    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Real-time Graph", "Statistics"])
    
    with tab1:
        # Initialize the graph
        timestamps, good_packets, bad_packets = generate_sample_packets()
        
        # Create plotly figure
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(
            x=timestamps, 
            y=good_packets,
            name="Good Packets",
            line=dict(color='green', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps, 
            y=bad_packets,
            name="Bad Packets",
            line=dict(color='red', width=2)
        ))
        
        # Update layout
        fig.update_layout(
            title="Network Packet Analysis",
            xaxis_title="Time",
            yaxis_title="Packet Score",
            hovermode='x unified',
            showlegend=True
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Add auto-refresh option
        if st.toggle("Enable Auto-refresh", value=False):
            st.empty()  # Placeholder for future real-time updates
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        
        # Calculate statistics using PyTorch
        total_packets = len(good_packets) + len(bad_packets)
        good_ratio = float(np.sum(good_packets > 0.5)) / total_packets
        bad_ratio = float(np.sum(bad_packets > 0.5)) / total_packets
        
        with col1:
            st.metric(
                label="Total Packets",
                value=f"{total_packets:,}",
                delta="Last 100 samples"
            )
        
        with col2:
            st.metric(
                label="Good Packet Ratio",
                value=f"{good_ratio:.2%}",
                delta="normal traffic"
            )
        
        with col3:
            st.metric(
                label="Bad Packet Ratio",
                value=f"{bad_ratio:.2%}",
                delta="potential threats",
                delta_color="inverse"
            )
        
        # Show distribution plot
        dist_fig = go.Figure()
        dist_fig.add_trace(go.Histogram(
            x=good_packets,
            name="Good Packets",
            opacity=0.75,
            marker_color='green'
        ))
        dist_fig.add_trace(go.Histogram(
            x=bad_packets[bad_packets > 0],
            name="Bad Packets",
            opacity=0.75,
            marker_color='red'
        ))
        
        dist_fig.update_layout(
            title="Packet Score Distribution",
            xaxis_title="Score",
            yaxis_title="Count",
            barmode='overlay'
        )
        
        st.plotly_chart(dist_fig, use_container_width=True)

# Call the function
show_packets()