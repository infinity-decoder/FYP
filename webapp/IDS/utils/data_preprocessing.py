# webapp/IDS/utils/data_preprocessing.py

import os
import pandas as pd
import numpy as np
import joblib
from django.conf import settings
from sklearn.exceptions import NotFittedError
import warnings

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
        warnings.filterwarnings('ignore', category=FutureWarning)

    def load_scaler(self):
        """Load pre-trained scaler from correct path"""
        try:
            # Correct path to scaler
            scaler_path = os.path.join(settings.BASE_DIR, 'webapp', 'IDS', 'media', 'trained_models', 'meta_scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Scaler loaded from: {scaler_path}")
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
            # Load CSV with error handling
            df = pd.read_csv(input_csv_path)
            
            if df.empty:
                raise ValueError("Loaded CSV is empty.")

            # Clean data - drop empty columns and rows with threshold
            df = df.dropna(axis=1, how='all')
            df = df.dropna(thresh=int(0.5 * len(df)), axis=1)
            
            # Ensure we have at least some data left
            if df.empty:
                raise ValueError("No data remaining after initial cleaning.")

            # Handle missing values without chained assignment
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())
                
            for col in df.select_dtypes(exclude=['float64', 'int64']).columns:
                mode_values = df[col].mode()
                df[col] = df[col].fillna(mode_values[0] if not mode_values.empty else "unknown")

            # Align features with what scaler expects
            available_features = [f for f in self.scaler.feature_names_in_ if f in df.columns]
            missing_features = list(set(self.scaler.feature_names_in_) - set(available_features))
            
            if missing_features:
                print(f"⚠️ Adding missing features: {missing_features}")
                for feature in missing_features:
                    df[feature] = 0  # Add with default value
                    
            # Select only the features the scaler expects
            df = df[self.scaler.feature_names_in_]

            # Scale data
            scaled_data = self.scaler.transform(df)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, os.path.basename(input_csv_path).replace('.csv', '_processed.csv'))
            
            # Save processed data
            pd.DataFrame(scaled_data, columns=self.scaler.feature_names_in_).to_csv(output_path, index=False)
            
            print(f"✅ Preprocessed data saved to: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Preprocessing failed: {str(e)}")
            raise