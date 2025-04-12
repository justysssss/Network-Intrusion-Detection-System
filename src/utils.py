import joblib
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd
import numpy as np
from scapy.all import IP, TCP, UDP
from collections import defaultdict

# Define important features for NIDS
IMPORTANT_FEATURES = [
    'protocol', 'sbytes', 'dbytes', 'rate'  # Most critical features for intrusion detection
]

def load_scalers():
    """Load pre-trained scalers from models directory"""
    try:
        minmax_scaler = joblib.load('models/minmax_scaler.pkl')
        standard_scaler = joblib.load('models/standard_scaler.pkl')
    except:
        # Initialize new scalers if not found
        minmax_scaler = MinMaxScaler()
        standard_scaler = StandardScaler()
        minmax_scaler.fit(pd.DataFrame(np.zeros((1, len(IMPORTANT_FEATURES)))))
        standard_scaler.fit(pd.DataFrame(np.zeros((1, len(IMPORTANT_FEATURES)))))
    return minmax_scaler, standard_scaler

def process_packet(packet):
    """Extract features from a network packet"""
    features = defaultdict(float)
    
    if IP in packet:
        features['protocol'] = packet[IP].proto
        features['sttl'] = packet[IP].ttl
        features['dttl'] = packet[IP].ttl
        features['sbytes'] = len(packet[IP])
        features['dbytes'] = len(packet[IP])
        
        if TCP in packet:
            features['service'] = packet[TCP].dport
            features['swin'] = packet[TCP].window
            features['dwin'] = packet[TCP].window
            features['tcprtt'] = 0  # Will be calculated from sequence numbers
            features['synack'] = 1 if packet[TCP].flags.SA else 0
        elif UDP in packet:
            features['service'] = packet[UDP].dport
            
        # Calculate rate-based features
        features['rate'] = 1  # Will be updated based on packet timing
        features['sload'] = features['sbytes']
        features['dload'] = features['dbytes']
        features['spkts'] = 1
        features['dpkts'] = 1
        features['duration'] = 0  # Will be updated based on flow duration
    
    return pd.DataFrame([{f: features[f] for f in IMPORTANT_FEATURES}])

def preprocess_data(data, minmax_scaler, standard_scaler):
    """Preprocess network data for model input"""
    # Ensure data has all required features
    for feature in IMPORTANT_FEATURES:
        if feature not in data.columns:
            data[feature] = 0
            
    data = data[IMPORTANT_FEATURES]
    
    # Only use MinMax scaling for these critical features
    scaled_data = minmax_scaler.transform(data)
    return scaled_data
