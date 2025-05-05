import joblib
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

BASE_MODELS = {
    'xgb': joblib.load(os.path.join(MODELS_DIR, 'xgb_model.pkl')),
    'lgbm': joblib.load(os.path.join(MODELS_DIR, 'lgbm_model.pkl')),
    'rf': joblib.load(os.path.join(MODELS_DIR, 'rf_model.pkl'))
}
META_MODEL = joblib.load(os.path.join(MODELS_DIR, 'tabnet_meta_model.pkl'))
SCALER = joblib.load(os.path.join(MODELS_DIR, 'meta_scaler.pkl'))

def predict_with_ensemble(preprocessed_df):
    base_outputs = []

    for name, model in BASE_MODELS.items():
        if hasattr(model, "predict_proba"):
            preds = model.predict_proba(preprocessed_df)[:, 1]
        else:
            preds = model.predict(preprocessed_df)
        base_outputs.append(preds)

    meta_input = np.column_stack(base_outputs)
    meta_input_scaled = SCALER.transform(meta_input)

    meta_preds = META_MODEL.predict(meta_input_scaled)
    return meta_preds.tolist()
