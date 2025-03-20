import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# File Paths
RAW_DATA_PATH = "D:/FYP/data/raw/network_traffic.pcapng"
PROCESSED_DATA_PATH = "D:/FYP/data/processed/traffic_data.csv"
FINAL_DATASET_PATH = "D:/FYP/data/datasets/final_dataset.csv"

def load_data(csv_path):
    """
    Load dataset from a CSV file.
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Successfully loaded data from {csv_path}")
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def clean_data(df):
    """
    Handle missing values and drop unnecessary columns.
    """
    df.dropna(inplace=True)  # Remove missing values
    
    # Drop irrelevant columns (modify as needed)
    if 'timestamp' in df.columns:
        df.drop(columns=['timestamp'], inplace=True)
    
    print("✅ Data cleaning completed.")
    return df

def encode_features(df):
    """
    Encode categorical variables (One-Hot Encoding for 'protocol').
    """
    if 'protocol' in df.columns:
        df = pd.get_dummies(df, columns=['protocol'])
    
    # Convert IP addresses into numerical values
    if 'source_ip' in df.columns and 'destination_ip' in df.columns:
        df['source_ip'] = df['source_ip'].astype('category').cat.codes
        df['destination_ip'] = df['destination_ip'].astype('category').cat.codes
    
    print("✅ Encoding completed.")
    return df

def normalize_features(df):
    """
    Normalize numerical features using Min-Max Scaling.
    """
    scaler = MinMaxScaler()
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    df[num_cols] = scaler.fit_transform(df[num_cols])
    print("✅ Normalization completed.")
    return df

def split_dataset(df, test_size=0.2):
    """
    Split dataset into training and testing sets.
    """
    X = df.drop(columns=['label'])  # Features
    y = df['label']  # Target variable
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    print("✅ Data split into training and testing sets.")
    return X_train, X_test, y_train, y_test

def save_processed_data(df, output_path):
    """
    Save the processed dataset to a CSV file.
    """
    try:
        df.to_csv(output_path, index=False)
        print(f"✅ Processed dataset saved at {output_path}")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

if __name__ == "__main__":
    # Load raw or processed data
    df = load_data(PROCESSED_DATA_PATH)
    
    if df is not None:
        df = clean_data(df)
        df = encode_features(df)
        df = normalize_features(df)
        
        # Save the final processed dataset
        save_processed_data(df, FINAL_DATASET_PATH)
