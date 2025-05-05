# FYP/webapp/IDS/utils/data_preprocessing.py
import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TrafficPreprocessor:
    def __init__(self):
        # Original features used during training (must match exactly)
        self.required_features = [
            'frame.len',
            'ip.ttl',
            'tcp.srcport', 
            'tcp.dstport',
            'frame.time_delta_displayed',
            'wlan_radio.signal_db'
        ]
        
    def preprocess(self, input_csv_path, output_dir):
        """
        Cleans and prepares raw packet data EXACTLY like during training.
        Returns path to processed CSV ready for prediction.
        """
        try:
            # 1. Load raw CSV with consistent parsing
            df = self._load_raw_csv(input_csv_path)
            
            # 2. Clean and validate data
            df = self._clean_data(df)
            
            # 3. Ensure required features exist
            df = self._ensure_features(df)
            
            # 4. Save processed data
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{Path(input_csv_path).stem}_processed.csv")
            df.to_csv(output_path, index=False)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise

    def _load_raw_csv(self, path):
        """Load CSV with consistent separator and handle parsing errors"""
        try:
            # Use same separator as tshark output
            return pd.read_csv(path, sep='|', low_memory=False)
        except Exception as e:
            logger.error(f"Failed to load CSV: {str(e)}")
            raise ValueError("Invalid PCAP CSV format")

    def _clean_data(self, df):
        """Perform exact same cleaning as training pipeline"""
        # Drop fully empty columns/rows
        df = df.dropna(axis=1, how='all')
        df = df.dropna(axis=0, how='all')
        
        # Fill missing values consistently with training
        num_cols = df.select_dtypes(include=np.number).columns
        df[num_cols] = df[num_cols].fillna(0)
        
        # Convert all numeric columns to float32 (matches training)
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')
            
        return df

    def _ensure_features(self, df):
        """Guarantee the model gets features in expected format"""
        # Add missing features with 0 values
        for feature in self.required_features:
            if feature not in df.columns:
                df[feature] = 0.0
                
        # Select only the required features in correct order
        return df[self.required_features]