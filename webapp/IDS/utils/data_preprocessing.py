# webapp/IDS/utils/data_preprocessing.py

import os
import pandas as pd
import numpy as np
import joblib
from django.conf import settings
from sklearn.exceptions import NotFittedError

class TrafficPreprocessor:
    def __init__(self):
        self.required_features = [
            'frame.len',
            'ip.ttl',
            'tcp.srcport',
            'tcp.dstport',
            'frame.time_delta_displayed',
            'wlan_radio.signal_db'
        ]
        self.scaler = None
        self.load_scaler()

    def load_scaler(self):
        """Load pre-trained scaler for consistent feature scaling"""
        try:
            scaler_path = os.path.join(settings.MEDIA_ROOT, 'trained_models', 'meta_scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            print("✅ Scaler loaded from meta_scaler.pkl")
        except Exception as e:
            print(f"❌ Scaler load failed: {str(e)}")
            raise

    def preprocess(self, input_csv_path, output_dir):
        """
        Clean, transform, and scale the CSV file.
        Args:
            input_csv_path (str): Raw tshark CSV file
            output_dir (str): Directory to save processed output
        Returns:
            str: Full path to processed CSV
        """
        try:
            df = pd.read_csv(input_csv_path)

            if df.empty:
                raise ValueError("Loaded CSV is empty.")

            # Drop empty columns or those with too many missing values
            df = df.dropna(axis=1, how='all')
            df = df.dropna(thresh=int(0.5 * len(df)), axis=1)

            # Fill missing values
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "unknown", inplace=True)

            # Filter required features
            features_available = [f for f in self.required_features if f in df.columns]
            missing_features = list(set(self.required_features) - set(features_available))

            if missing_features:
                print(f"⚠️ Missing features: {missing_features}")

            df = df[features_available]

            if df.empty:
                raise ValueError("Preprocessed DataFrame is empty after feature selection.")

            # Scale data
            try:
                scaled = self.scaler.transform(df)
            except NotFittedError:
                raise ValueError("Scaler not fitted. Ensure meta_scaler.pkl is trained.")

            output_path = os.path.join(output_dir, os.path.basename(input_csv_path).replace('.csv', '_processed.csv'))
            pd.DataFrame(scaled, columns=features_available).to_csv(output_path, index=False)

            print(f"✅ Preprocessed data saved to: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Preprocessing failed: {str(e)}")
            raise
