# webapp/IDS/utils/ml_predictor.py

import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings
import warnings

class IntrusionDetectionPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.meta_model = None
        self.load_models()
        warnings.filterwarnings('ignore', category=UserWarning)

    def load_models(self):
        """Load base models, meta-model, and scaler from correct path."""
        # Correct model directory path
        model_dir = os.path.join(settings.BASE_DIR, 'webapp', 'IDS', 'media', 'trained_models')
        
        # List of models to try loading
        model_files = {
            'xgboost': 'xgboost_native_model.pkl',
            'lightgbm': 'lightgbm_intrusion_detection.pkl',
            'catboost': 'catboost_intrusion_detection.pkl'
        }
        
        try:
            # Load scaler first
            self.scaler = joblib.load(os.path.join(model_dir, 'meta_scaler.pkl'))
            
            # Try loading each model
            for name, filename in model_files.items():
                try:
                    model_path = os.path.join(model_dir, filename)
                    self.models[name] = joblib.load(model_path)
                    print(f"✅ Loaded model: {name}")
                except Exception as e:
                    print(f"❌ Failed to load {name}: {str(e)}")
                    continue
            
            # Load meta model
            self.meta_model = joblib.load(os.path.join(model_dir, 'tabnet_meta_model.pkl'))
            
            if not self.models:
                raise ValueError("No base models loaded successfully")
                
            print(f"✅ Loaded available models: {list(self.models.keys())}")

        except Exception as e:
            print(f"❌ Critical model loading error: {str(e)}")
            raise

    def predict(self, input_df):
        """
        Run predictions using available base models and meta-model.
        Args:
            input_df (DataFrame): preprocessed input data
        Returns:
            dict: structured predictions
        """
        try:
            if not isinstance(input_df, pd.DataFrame):
                raise ValueError("Input must be a pandas DataFrame")

            # Ensure we have models loaded
            if not self.models:
                raise ValueError("No models available for prediction")

            base_predictions = {}
            meta_input_features = []

            # Run each available model
            for name, model in self.models.items():
                try:
                    # Get predictions
                    preds = model.predict(input_df.values)  # Using native API format
                    
                    # Get probabilities if available
                    if hasattr(model, 'predict_proba'):
                        proba = model.predict_proba(input_df.values)[:, 1]
                    else:
                        proba = None

                    # Store results
                    base_predictions[name] = {
                        'predictions': preds.tolist(),
                        'confidence': proba.tolist() if proba is not None else None,
                        'normal': int((preds == 0).sum()),
                        'attack': int((preds == 1).sum())
                    }

                    # Add to meta features
                    if proba is not None:
                        meta_input_features.append(proba)
                    else:
                        meta_input_features.append(preds.astype(float))

                except Exception as e:
                    print(f"⚠️ Prediction failed for {name}: {str(e)}")
                    continue

            # Meta-model prediction if we have at least one base model result
            if meta_input_features:
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