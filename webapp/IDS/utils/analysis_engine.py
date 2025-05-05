import os
from .data_preprocessing import preprocess_csv
from .ml_predictor import predict_with_ensemble
import pandas as pd

def analyze_uploaded_file(file_path):
    try:
        # Step 1: Preprocess the uploaded CSV
        preprocessed_df = preprocess_csv(file_path)

        # Step 2: Run predictions
        predictions = predict_with_ensemble(preprocessed_df)

        # Step 3: Prepare output DataFrame
        result_df = pd.DataFrame(preprocessed_df)
        result_df["prediction"] = predictions

        return {
            "success": True,
            "data": result_df.to_dict(orient="records")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
