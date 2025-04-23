import os
import json
import traceback
import pandas as pd
from django.conf import settings
from .pcap_to_csv import PcapConverter
from .data_preprocessing import TrafficPreprocessor
from .ml_predictor import IntrusionDetectionPredictor
from IDS.models import PcapFile, AnalysisResult

class AnalysisEngine:
    def __init__(self, pcap_file_instance):
        self.pcap_instance = pcap_file_instance
        self.pcap_path = pcap_file_instance.file.path
        self.filename = os.path.basename(self.pcap_path).replace('.pcap', '').replace('.pcapng', '')
        self.media_root = settings.MEDIA_ROOT

        # Define folders
        self.upload_dir = os.path.join(self.media_root, 'uploads')
        self.csv_dir = os.path.join(self.media_root, 'csvs')
        self.dataset_dir = os.path.join(self.media_root, 'datasets')
        self.results_dir = os.path.join(self.media_root, 'results')

        # ✅ Make sure all dirs are created
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

        # Initialize utility classes
        self.converter = PcapConverter()
        self.preprocessor = TrafficPreprocessor()
        self.predictor = IntrusionDetectionPredictor()

    def run(self):
        try:
            print(f"📥 Starting analysis for {self.filename}")

            # Step 1: Convert PCAP to CSV
            print("🔄 Converting PCAP to CSV...")
            csv_path = self.converter.convert(self.pcap_path, self.csv_dir)

            # Step 2: Preprocess CSV to dataset
            print("🧹 Preprocessing CSV data...")
            dataset_path = self.preprocessor.preprocess(csv_path, self.dataset_dir)
            df = self._load_csv(dataset_path)

            if df.empty:
                raise ValueError("Processed dataset is empty. Cannot proceed with prediction.")

            # Step 3: Predict using ML models
            print("🤖 Running model predictions...")
            results = self.predictor.predict(df)

            # Step 4: Save result as JSON
            json_path = os.path.join(self.results_dir, f"{self.filename}_results.json")
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=4)

            print(f"✅ Analysis completed. Results saved to {json_path}")

            # Step 5: Save result to database
            analysis_obj = AnalysisResult.objects.create(
                pcap=self.pcap_instance,
                result_json=json_path,
                prediction_summary=self._extract_summary(results)
            )
            self.pcap_instance.status = 'completed'  # ✅ Matches views.py logic
            self.pcap_instance.analysis_result = {
                "status": "completed",
                **self._generate_summary_dict(results)
            }
            self.pcap_instance.save()

            return analysis_obj

        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            traceback.print_exc()
            self.pcap_instance.status = 'failed'
            self.pcap_instance.save()
            return None

    def _load_csv(self, path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            print(f"❌ Failed to load preprocessed CSV: {e}")
            return pd.DataFrame()

    def _extract_summary(self, results):
        try:
            ensemble_preds = results.get("ensemble", {}).get("predictions", [])
            total = len(ensemble_preds)
            malicious = sum(ensemble_preds)
            benign = total - malicious
            return f"Total: {total}, Malicious: {malicious}, Benign: {benign}"
        except Exception as e:
            return "Summary generation failed"

    def _generate_summary_dict(self, results):
        try:
            ensemble_preds = results.get("ensemble", {}).get("predictions", [])
            total = len(ensemble_preds)
            malicious = sum(ensemble_preds)
            benign = total - malicious
            return {
                "total_packets": total,
                "malicious_count": malicious,
                "normal_count": benign
            }
        except Exception as e:
            print("❌ Failed to generate summary dictionary.")
            return {
                "total_packets": 0,
                "malicious_count": 0,
                "normal_count": 0
            }
