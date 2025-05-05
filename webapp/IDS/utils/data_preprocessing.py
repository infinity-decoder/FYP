# FYP/webapp/IDS/utils/data_preprocessing.py
import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import joblib
from django.conf import settings

logger = logging.getLogger(__name__)

class TrafficPreprocessor:
    def __init__(self):
        # These must match EXACTLY what was used during training
        self.required_features = [
            'frame.len',
            'ip.ttl',
            'tcp.srcport',
            'tcp.dstport',
            'frame.time_delta_displayed',
            'wlan_radio.signal_db'
        ]
        
        # Additional features needed for reporting
        self.reporting_features = ['ip.src', 'ip.dst']
        
        # Load the scaler used during training
        self.scaler = self._load_scaler()

    def _load_scaler(self):
        """Load the StandardScaler used during training"""
        try:
            scaler_path = os.path.join(
                settings.BASE_DIR,
                'IDS',
                'media',
                'trained_models',
                'meta_scaler.pkl'
            )
            return joblib.load(scaler_path)
        except Exception as e:
            logger.error(f"Scaler load failed: {str(e)}")
            raise

    def preprocess(self, input_csv_path, output_dir):
        """
        Process data EXACTLY like during training
        Returns path to processed CSV ready for prediction
        """
        try:
            # 1. Load raw CSV with consistent parsing
            df = pd.read_csv(input_csv_path, sep='|')
            
            # 2. Clean and validate data
            df = self._clean_and_validate(df)
            
            # 3. Ensure required features exist with correct names
            df = self._ensure_features(df)
            
            # 4. Prepare features for base models
            X = df[self.required_features].values
            
            # 5. Generate meta-features (same as training)
            meta_features = self._generate_meta_features(X)
            
            # 6. Scale meta-features
            scaled_meta = self.scaler.transform(meta_features)
            
            # 7. Save processed data
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{Path(input_csv_path).stem}_processed.csv")
            np.savetxt(output_path, scaled_meta, delimiter=',')
            
            return output_path
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise

    def _clean_and_validate(self, df):
        """Perform exact same cleaning as training pipeline"""
        # Convert all numeric columns to float32 (matches training)
        for col in df.select_dtypes(include=np.number).columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')
            
        # Fill missing values consistently with training
        df = df.fillna(0)
        
        return df

    def _ensure_features(self, df):
        """Guarantee the model gets features in expected format"""
        # Add missing features with 0 values
        for feature in self.required_features + self.reporting_features:
            if feature not in df.columns:
                df[feature] = 0.0
                
        return df

    def _generate_meta_features(self, X):
        """Generate predictions from base models (like during training)"""
        models = self._load_base_models()
        
        # XGBoost prediction
        xgb_preds = models['xgboost'].predict(X)
        
        # LightGBM prediction
        lgb_preds = models['lightgbm'].predict(X)
        
        return np.vstack((xgb_preds, lgb_preds)).T

    def _load_base_models(self):
        """Load the base models for meta-feature generation"""
        models = {}
        model_dir = os.path.join(
            settings.BASE_DIR,
            'IDS',
            'media',
            'trained_models'
        )
        
        # Load XGBoost
        xgb_path = os.path.join(model_dir, "xgboost_native_model.pkl")
        models['xgboost'] = joblib.load(xgb_path)
        
        # Load LightGBM
        lgb_path = os.path.join(model_dir, "lightgbm_intrusion_detection.pkl")
        models['lightgbm'] = joblib.load(lgb_path)
        
        return models