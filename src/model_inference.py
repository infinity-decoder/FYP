import os
import joblib
import torch
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
import lightgbm as lgb
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report

# Define paths
MODEL_DIR = "D:/FYP/models/trained_models/"
DATASET_PATH = "D:/FYP/data/datasets/final_dataset.csv"

# Load dataset
def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    X = df.drop(columns=['label'])  # Features
    y = df['label']  # Target variable
    return X, y

# Load trained models
def load_model(model_name):
    model_path = os.path.join(MODEL_DIR, model_name)
    if model_name.endswith(".cbm"):
        model = CatBoostClassifier()
        model.load_model(model_path)
    elif model_name.endswith(".txt"):
        model = lgb.Booster(model_file=model_path)
    elif model_name.endswith(".joblib"):
        model = joblib.load(model_path)
    elif model_name.endswith(".pt"):
        model = TabNetClassifier()
        model.load_model(model_path)
    else:
        raise ValueError("Unsupported model format!")
    return model

# Run inference
def run_inference(model, X):
    if isinstance(model, lgb.Booster):
        return model.predict(X)
    elif isinstance(model, TabNetClassifier):
        return model.predict(X.values)
    else:
        return model.predict(X)

# Evaluate model
def evaluate_model(model, X, y):
    y_pred = run_inference(model, X)
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, average='weighted')
    recall = recall_score(y, y_pred, average='weighted')
    f1 = f1_score(y, y_pred, average='weighted')
    roc_auc = roc_auc_score(y, y_pred, multi_class='ovr')
    report = classification_report(y, y_pred)
    
    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC AUC": roc_auc,
        "Classification Report": report
    }

# Run evaluation for all models
def evaluate_all_models():
    X, y = load_dataset()
    model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith((".cbm", ".txt", ".joblib", ".pt"))]
    results = {}
    
    for model_file in model_files:
        print(f"Evaluating {model_file}...")
        model = load_model(model_file)
        results[model_file] = evaluate_model(model, X, y)
        print(results[model_file])
    
    return results

if __name__ == "__main__":
    evaluate_all_models()
