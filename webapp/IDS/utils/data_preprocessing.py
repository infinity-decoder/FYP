import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoders.joblib")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "models", "feature_columns.joblib")

def preprocess_csv(file_path):
    df = pd.read_csv(file_path)

    # Drop nulls and fill NA
    df.dropna(inplace=True)
    df.fillna(0, inplace=True)

    # Load label encoders
    encoders = joblib.load(ENCODER_PATH)
    for col, le in encoders.items():
        if col in df.columns:
            df[col] = df[col].map(lambda s: '<unknown>' if s not in le.classes_ else s)
            le.classes_ = list(le.classes_) + ['<unknown>'] if '<unknown>' not in le.classes_ else le.classes_
            df[col] = le.transform(df[col])

    # Load expected feature columns
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

    # Add missing columns
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns]  # Ensure correct column order
    return df
