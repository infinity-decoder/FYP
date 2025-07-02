# added listing of attack ips in FILE: FYP/webapp/IDS/utils/ml_predictor.py

import os
import joblib
import numpy as np
from django.conf import settings
import warnings

class IntrusionDetectionPredictor:
    def __init__(self):
        self.meta_model = None
        self.load_model()
        warnings.filterwarnings('ignore', category=UserWarning)

    def load_model(self):
        """Load ONLY the final TabNet meta-model."""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'IDS', 'media', 'trained_models', 'tabnet_meta_model.pkl')
            self.meta_model = joblib.load(model_path)
            print("✅ Loaded TabNet meta-model.")
        except Exception as e:
            print(f"❌ Failed to load TabNet model: {str(e)}")
            raise

    def predict(self, input_df):
        """
        Predict directly using the TabNet model with meta-feature input.
        Returns both predictions and malicious IP addresses.
        """
        try:
            # Store original DataFrame if it has IP information
            original_df = input_df.copy() if hasattr(input_df, 'copy') else None
            
            # Convert input to numpy array if needed
            if hasattr(input_df, 'values'):
                input_values = input_df.values
            elif isinstance(input_df, np.ndarray):
                input_values = input_df
            else:
                raise ValueError("Input must be a NumPy array or pandas DataFrame")

            # Get predictions
            preds = self.meta_model.predict(input_values)
            
            # Prepare malicious IPs list if source data contains IP information
            malicious_ips = []
            if original_df is not None and 'ip.src' in original_df.columns:
                malicious_indices = np.where(preds == 1)[0]
                malicious_ips = original_df.iloc[malicious_indices]['ip.src'].unique().tolist()
                # Limit to top 20 malicious IPs to prevent overwhelming output
                malicious_ips = malicious_ips[:20]

            return {
                'ensemble': {
                    'predictions': preds.astype(int).tolist(),
                    'normal': int((preds == 0).sum()),
                    'attack': int((preds == 1).sum()),
                    'malicious_ips': malicious_ips  # Added this line
                }
            }

        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            raise