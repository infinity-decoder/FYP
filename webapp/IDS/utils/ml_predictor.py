import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings


class IntrusionDetectionPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.meta_model = None
        self.load_models()

    def load_models(self):
        """Load base models, meta-model, and scaler"""
        model_dir = os.path.join(settings.MEDIA_ROOT, 'trained_models')

        try:
            self.models = {
                'xgboost': joblib.load(os.path.join(model_dir, 'xgboost_native_model.pkl')),
                'lightgbm': joblib.load(os.path.join(model_dir, 'lightgbm_intrusion_detection.pkl')),
                'catboost': joblib.load(os.path.join(model_dir, 'catboost_intrusion_detection.pkl')),
            }
            self.meta_model = joblib.load(os.path.join(model_dir, 'tabnet_meta_model.pkl'))
            self.scaler = joblib.load(os.path.join(model_dir, 'meta_scaler.pkl'))

            print("✅ All models loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load models: {str(e)}")
            raise

    def predict(self, input_df):
        """
        Run predictions using base models and meta-model.
        Returns:
            dict: predictions from base models and final ensemble.
        """
        try:
            if not isinstance(input_df, pd.DataFrame):
                raise ValueError("Input data must be a pandas DataFrame")

            # Scale input features
            scaled_input = self.scaler.transform(input_df)

            base_predictions = {}
            meta_input_features = []

            # Predict using each base model
            for name, model in self.models.items():
                preds = model.predict(scaled_input)
                proba = model.predict_proba(scaled_input)[:, 1] if hasattr(model, 'predict_proba') else None

                base_predictions[name] = {
                    'predictions': preds.tolist(),
                    'confidence': proba.tolist() if proba is not None else None
                }

                # For meta-model input, use prediction probabilities or predictions
                if proba is not None:
                    meta_input_features.append(proba)
                else:
                    meta_input_features.append(preds)

            # Transpose to shape: (n_samples, n_models)
            meta_input = np.vstack(meta_input_features).T

            # Final prediction from meta-model (TabNet)
            final_preds = self.meta_model.predict(meta_input)

            base_predictions['ensemble'] = {
                'predictions': final_preds.astype(int).tolist(),
                'confidence': None  # Could be extended to return TabNet probabilities
            }

            return base_predictions

        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            raise
