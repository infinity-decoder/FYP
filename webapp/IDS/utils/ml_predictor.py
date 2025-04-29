# webapp/IDS/utils/ml_predictor.py

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
        """Load base models, meta-model, and scaler from disk."""
        model_dir = os.path.join(settings.MEDIA_ROOT, 'trained_models')

        try:
            self.models = {
                'xgboost': joblib.load(os.path.join(model_dir, 'xgboost_native_model.pkl')),
                'lightgbm': joblib.load(os.path.join(model_dir, 'lightgbm_intrusion_detection.pkl')),
                'catboost': joblib.load(os.path.join(model_dir, 'catboost_intrusion_detection.pkl')),
            }
            self.meta_model = joblib.load(os.path.join(model_dir, 'tabnet_meta_model.pkl'))
            self.scaler = joblib.load(os.path.join(model_dir, 'meta_scaler.pkl'))

            print("✅ All models and scaler loaded successfully.")
        except Exception as e:
            print(f"❌ Model loading failed: {str(e)}")
            raise

    def predict(self, input_df):
        """
        Run predictions using base models and meta-model.
        Args:
            input_df (DataFrame): preprocessed input data
        Returns:
            dict: structured predictions
        """
        try:
            if not isinstance(input_df, pd.DataFrame):
                raise ValueError("Input must be a pandas DataFrame")

            # Step 1: Scale input features
            scaled_input = self.scaler.transform(input_df)

            base_predictions = {}
            meta_input_features = []

            # Step 2: Run base models
            for name, model in self.models.items():
                preds = model.predict(scaled_input)
                proba = model.predict_proba(scaled_input)[:, 1] if hasattr(model, 'predict_proba') else None

                normal = int((preds == 0).sum())
                attack = int((preds == 1).sum())

                base_predictions[name] = {
                    'predictions': preds.tolist(),
                    'confidence': proba.tolist() if proba is not None else None,
                    'normal': normal,
                    'attack': attack
                }

                meta_input_features.append(proba if proba is not None else preds)

            # Step 3: Meta-model (TabNet)
            meta_input = np.vstack(meta_input_features).T
            final_preds = self.meta_model.predict(meta_input)

            base_predictions['ensemble'] = {
                'predictions': final_preds.astype(int).tolist(),
                'confidence': None,
                'normal': int((final_preds == 0).sum()),
                'attack': int((final_preds == 1).sum())
            }

            return base_predictions

        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            raise
