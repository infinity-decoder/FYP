import os
import pandas as pd
import numpy as np
import joblib
from django.conf import settings
import warnings
from pathlib import Path
import logging
import xgboost as xgb
import lightgbm as lgb

logger = logging.getLogger(__name__)

class TrafficPreprocessor:
    def __init__(self):
        # Must exactly match training features used in base models
        self.original_features = [
            'frame.number',
            '_ws.col.protocol',
            'ip.ttl',
            'ip.src',
            'ip.dst',
            'tcp.srcport',
            'tcp.dstport',
            'tcp.flags',
            '_ws.col.info',
            'frame.len',
            'frame.time_delta_displayed'
        ]
        self.required_features = self.original_features
        self.scaler = self._load_scaler()
        self.models = self._load_base_models()
        warnings.filterwarnings('ignore')

    def _load_scaler(self):
        try:
            scaler_path = os.path.join(
                settings.BASE_DIR,
                'IDS', 'media', 'trained_models', 'meta_scaler.pkl'
            )
            return joblib.load(scaler_path)
        except Exception as e:
            logger.error(f"Scaler load failed: {str(e)}")
            raise

    def preprocess(self, input_csv_path, output_dir):
        try:
            df = pd.read_csv(input_csv_path, sep='|')
            X_df = self._prepare_original_features(df)
            meta_features = self._generate_meta_features(X_df)
            scaled_meta = self.scaler.transform(meta_features)

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{Path(input_csv_path).stem}_processed.csv")
            np.savetxt(output_path, scaled_meta, delimiter=',')
            return output_path

        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise

    def _prepare_original_features(self, df):
        df = df.copy()
        for feature in self.original_features:
            if feature not in df.columns:
                df[feature] = 0.0
            else:
                df[feature] = pd.to_numeric(df[feature], errors='coerce').fillna(0.0)
        return df[self.original_features]

    def _generate_meta_features(self, X_df):
        try:
            xgb_input = xgb.DMatrix(X_df, feature_names=self.original_features)
            xgb_preds = self.models['xgboost'].predict(xgb_input)
            lgb_preds = self.models['lightgbm'].predict(X_df)
            return np.vstack((xgb_preds, lgb_preds)).T
        except Exception as e:
            logger.error(f"Meta-feature generation failed: {str(e)}")
            raise

    def _load_base_models(self):
        model_dir = os.path.join(settings.BASE_DIR, 'IDS', 'media', 'trained_models')
        models = {}
        try:
            models['xgboost'] = joblib.load(os.path.join(model_dir, "xgboost_native_model.pkl"))
            models['lightgbm'] = joblib.load(os.path.join(model_dir, "lightgbm_intrusion_detection.pkl"))
            return models
        except Exception as e:
            logger.error(f"Error loading base models: {str(e)}")
            raise
