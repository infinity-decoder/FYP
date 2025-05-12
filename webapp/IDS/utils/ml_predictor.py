# ✅ FINAL FIXED FILE: FYP/webapp/IDS/utils/ml_predictor.py

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
        The input is expected to be a 2D numpy array or a pandas DataFrame with two columns.
        """
        try:
            if hasattr(input_df, 'values'):
                input_df = input_df.values
            elif not isinstance(input_df, np.ndarray):
                raise ValueError("Input must be a NumPy array or pandas DataFrame")

            preds = self.meta_model.predict(input_df)
            return {
                'ensemble': {
                    'predictions': preds.astype(int).tolist(),
                    'normal': int((preds == 0).sum()),
                    'attack': int((preds == 1).sum())
                }
            }

        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            raise
