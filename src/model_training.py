import os
import joblib
import torch
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
import lightgbm as lgb
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression

# Define paths
MODEL_DIR = "D:/FYP/models/trained_models/"
DATASET_PATH = "D:/FYP/data/datasets/final_dataset.csv"

# Load dataset
def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    X = df.drop(columns=['label'])  # Features
    y = df['label']  # Target variable
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Train and save CatBoost model
def train_catboost(X_train, y_train):
    model = CatBoostClassifier(verbose=0, iterations=500)
    model.fit(X_train, y_train)
    model_path = os.path.join(MODEL_DIR, "catboost_model.cbm")
    model.save_model(model_path)
    print(f"✅ CatBoost model saved at {model_path}")
    return model

# Train and save LightGBM model
def train_lightgbm(X_train, y_train):
    model = lgb.LGBMClassifier()
    model.fit(X_train, y_train)
    model_path = os.path.join(MODEL_DIR, "lightgbm_model.txt")
    model.booster_.save_model(model_path)
    print(f"✅ LightGBM model saved at {model_path}")
    return model

# Train and save TabNet model
def train_tabnet(X_train, y_train):
    model = TabNetClassifier()
    model.fit(X_train.values, y_train.values, max_epochs=100, patience=10)
    model_path = os.path.join(MODEL_DIR, "tabnet_model.pt")
    model.save_model(model_path)
    print(f"✅ TabNet model saved at {model_path}")
    return model

# Train and save Stacking Ensemble
def train_stacking(X_train, y_train, models):
    estimators = [(name, model) for name, model in models.items()]
    stacking_model = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression())
    stacking_model.fit(X_train, y_train)
    model_path = os.path.join(MODEL_DIR, "stacking_model.joblib")
    joblib.dump(stacking_model, model_path)
    print(f"✅ Stacking model saved at {model_path}")
    return stacking_model

# Train all models
def train_all_models():
    X_train, X_test, y_train, y_test = load_dataset()
    
    catboost_model = train_catboost(X_train, y_train)
    lightgbm_model = train_lightgbm(X_train, y_train)
    tabnet_model = train_tabnet(X_train, y_train)
    
    models = {
        "CatBoost": catboost_model,
        "LightGBM": lightgbm_model
    }
    
    train_stacking(X_train, y_train, models)
    print("✅ All models trained and saved successfully!")

if __name__ == "__main__":
    train_all_models()
