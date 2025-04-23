import os
import pandas as pd
import numpy as np
import joblib
from sklearn.exceptions import NotFittedError
from django.conf import settings


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
        """Load pre-trained scaler for consistent preprocessing"""
        try:
            scaler_path = os.path.join(settings.MEDIA_ROOT, 'trained_models', 'meta_scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            print("✅ Scaler loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load scaler: {str(e)}")
            raise

    def preprocess(self, input_csv_path, output_dir):
        """
        Clean, transform, and scale the raw CSV file from tshark output.
        Args:
            input_csv_path (str): Path to the raw CSV file generated from PCAP.
            output_dir (str): Directory to save the processed CSV file.
        Returns:
            str: Full path of the processed CSV file ready for prediction.
        """
        try:
            # Load CSV
            df = pd.read_csv(input_csv_path)

            if df.empty:
                raise ValueError("CSV file is empty or corrupted.")

            # Drop completely empty columns and columns with too many missing values
            df = df.dropna(axis=1, how='all')
            df = df.dropna(thresh=int(0.5 * len(df)), axis=1)

            # Fill missing values
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "unknown")

            # Filter only the required features
            available_features = [f for f in self.required_features if f in df.columns]
            missing_features = list(set(self.required_features) - set(available_features))

            if missing_features:
                print(f"⚠️ Warning: Missing features - {missing_features}")

            df = df[available_features]

            # Ensure dataframe is not empty
            if df.empty:
                raise ValueError("No required features found in the dataset.")

            # Scale the data using pre-trained scaler
            try:
                scaled_data = self.scaler.transform(df)
            except NotFittedError:
                raise ValueError("Scaler was not fitted. Check your meta_scaler.pkl file.")

            # Save to new processed file
            output_filename = os.path.basename(input_csv_path).replace('.csv', '_processed.csv')
            output_path = os.path.join(output_dir, output_filename)

            pd.DataFrame(scaled_data, columns=available_features).to_csv(output_path, index=False)

            print(f"✅ Preprocessed file saved to: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Preprocessing error: {str(e)}")
            raise
