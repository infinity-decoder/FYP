# FYP/webapp/IDS/utils/ml_predictor.py
import os
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class IntrusionDetectionPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.meta_model = None
        self._load_models()

    def _load_models(self):
        """Load all models using their native APIs"""
        model_dir = os.path.join(settings.BASE_DIR, 'IDS', 'media', 'trained_models')
        
        try:
            # Load scaler first
            self.scaler = joblib.load(os.path.join(model_dir, 'meta_scaler.pkl'))
            
            # Load XGBoost (native format)
            xgb_model_path = os.path.join(model_dir, 'xgboost_native_model.pkl')
            self.models['xgboost'] = joblib.load(xgb_model_path)
            
            # Load LightGBM (native format)
            lgb_model_path = os.path.join(model_dir, 'lightgbm_intrusion_detection.pkl')
            self.models['lightgbm'] = joblib.load(lgb_model_path)
            
            # Load TabNet meta model
            self.meta_model = joblib.load(os.path.join(model_dir, 'tabnet_meta_model.pkl'))
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise

    def predict(self, input_df):
        """
        Run ensemble prediction pipeline:
        1. Get base model predictions (native APIs)
        2. Generate meta-features
        3. Apply TabNet meta-model
        """
        try:
            # Convert DataFrame to numpy for native APIs
            X = input_df.values
            
            # Get base model predictions
            base_results = {}
            meta_features = []
            
            # XGBoost prediction (native DMatrix format)
            xgb_input = xgb.DMatrix(X)
            xgb_preds = self.models['xgboost'].predict(xgb_input)
            base_results['xgboost'] = self._format_prediction(xgb_preds)
            meta_features.append(xgb_preds)
            
            # LightGBM prediction (native format)
            lgb_preds = self.models['lightgbm'].predict(X)
            base_results['lightgbm'] = self._format_prediction(lgb_preds)
            meta_features.append(lgb_preds)
            
            # Prepare meta-features for TabNet
            meta_input = np.vstack(meta_features).T
            scaled_meta = self.scaler.transform(meta_input)
            
            # Final prediction with TabNet
            final_preds = self.meta_model.predict(scaled_meta)
            base_results['ensemble'] = self._format_prediction(final_preds)
            
            return base_results
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def _format_prediction(self, preds):
        """Convert raw predictions to consistent output format"""
        return {
            'predictions': preds.tolist(),
            'normal': int((preds == 0).sum()),
            'attack': int((preds == 1).sum())
        }