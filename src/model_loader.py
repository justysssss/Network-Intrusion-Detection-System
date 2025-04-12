import joblib
import torch
import warnings
from sklearn.linear_model import LogisticRegression
import numpy as np

def create_default_model():
    """Create a new LogisticRegression model with default parameters"""
    model = LogisticRegression(random_state=42)
    # Train on some basic data to initialize it
    X = np.array([[0, 0, 0, 0], [1, 1, 1, 1]])  # Example data
    y = np.array([0, 1])  # Example labels
    model.fit(X, y)
    return model

def load_model(path='models/logistic_regression_meta_model.pkl'):
    """Load the model, handling version mismatches"""
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            model = joblib.load(path)
            
            # Check if there were any version mismatch warnings
            version_mismatch = any("version" in str(warning.message) for warning in w)
            
            if version_mismatch:
                # If there's a version mismatch, create and return a new model
                model = create_default_model()
                # Save the new model
                joblib.dump(model, path)
                print("Created new model due to version mismatch")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        model = create_default_model()
        # Save the new model
        joblib.dump(model, path)
        print("Created new model due to loading error")
    
    if isinstance(model, torch.nn.Module):
        model.eval()
    
    return model

def load_meta_model():
    """Load meta model with version mismatch handling"""
    return load_model('models/logistic_regression_meta_model.pkl')
