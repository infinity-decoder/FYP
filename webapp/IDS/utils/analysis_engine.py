# FYP/webapp/IDS/utils/analysis_engine.py
import os
import json
import traceback
import pandas as pd
import logging
from django.conf import settings
from .pcap_to_csv import PcapConverter
from .data_preprocessing import TrafficPreprocessor
from .ml_predictor import IntrusionDetectionPredictor
from IDS.models import PcapFile, AnalysisResult

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self, pcap_file_instance):
        self.pcap_instance = pcap_file_instance
        self.pcap_path = pcap_file_instance.file.path
        self.filename = os.path.basename(self.pcap_path).replace('.pcap', '').replace('.pcapng', '')
        
        # Correct media root path - point directly to IDS/media
        self.media_root = os.path.join(settings.BASE_DIR, 'IDS', 'media')
        
        # Correct subdirectories
        self.csv_dir = os.path.join(self.media_root, 'csvs')
        self.dataset_dir = os.path.join(self.media_root, 'datasets')
        self.results_dir = os.path.join(self.media_root, 'results')

        # Ensure directories exist
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

        # Initialize processing components with error handling
        try:
            self.converter = PcapConverter()
            self.preprocessor = TrafficPreprocessor()
            self.predictor = IntrusionDetectionPredictor()
        except Exception as e:
            logger.error(f"[Engine] Failed to initialize components: {str(e)}")
            raise

    def _validate_pcap(self):
        """Verify PCAP file can be processed"""
        try:
            # Quick check if file exists and is valid
            if not os.path.exists(self.pcap_path):
                raise ValueError("PCAP file does not exist")
            
            if os.path.getsize(self.pcap_path) == 0:
                raise ValueError("PCAP file is empty")
                
            # Verify file magic number
            with open(self.pcap_path, 'rb') as f:
                magic = f.read(4)
                if magic not in [b'\xa1\xb2\xc3\xd4', b'\xd4\xc3\xb2\xa1']:
                    raise ValueError("Invalid PCAP file format")
                    
        except Exception as e:
            logger.error(f"Invalid PCAP file: {str(e)}")
            raise

    def run(self):
        try:
            logger.info(f"Starting analysis for: {self.filename}")
            self.pcap_instance.update_progress('converting', 'Converting PCAP to CSV...')

            # Validate PCAP before processing
            self._validate_pcap()

            # Step 1: Convert PCAP ➝ CSV
            logger.info("Converting PCAP to CSV...")
            csv_path = self.converter.convert(self.pcap_path, self.csv_dir)
            self.pcap_instance.update_progress('preprocessing', 'Preprocessing CSV data...')

            # Step 2: Preprocess ➝ Dataset
            logger.info("Preprocessing CSV data...")
            dataset_path = self.preprocessor.preprocess(csv_path, self.dataset_dir)
            df = self._load_csv(dataset_path)

            if df.empty:
                raise ValueError("Processed dataset is empty. Cannot proceed with prediction.")

            # Step 3: Predict
            logger.info("Running model predictions...")
            self.pcap_instance.update_progress('predicting', 'Running model predictions...')
            results = self.predictor.predict(df)

            # Step 4: Save predictions to JSON
            json_path = os.path.join(self.results_dir, f"{self.filename}_results.json")
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=4)

            logger.info(f"Prediction completed. Results saved to: {json_path}")
            self.pcap_instance.update_progress('saving', 'Saving results to database...')

            # Step 5: Extract summary
            ensemble_preds = results.get("ensemble", {}).get("predictions", [])
            total = len(ensemble_preds)
            malicious = sum(ensemble_preds)
            benign = total - malicious
            malicious_ips = self._extract_malicious_ips(df, ensemble_preds)

            # Step 6: Save to DB
            analysis_result = AnalysisResult.objects.create(
                pcap_file=self.pcap_instance,
                total_packets=total,
                malicious_count=malicious,
                normal_count=benign,
                malicious_ips=malicious_ips,
                model_details=results
            )

            self.pcap_instance.status = 'completed'
            self.pcap_instance.progress_stage = 'completed'
            self.pcap_instance.progress_message = 'Analysis completed successfully'
            self.pcap_instance.analysis_result = {
                "status": "completed",
                "total_packets": total,
                "malicious_count": malicious,
                "normal_count": benign
            }
            self.pcap_instance.save()

            return analysis_result

        except Exception as e:
            logger.error(f"[Engine] Error: {str(e)}")
            traceback.print_exc()
            self.pcap_instance.status = 'failed'
            self.pcap_instance.progress_stage = 'failed'
            self.pcap_instance.progress_message = f'Analysis failed: {str(e)}'
            self.pcap_instance.save()
            return None

    def _load_csv(self, path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            logger.error(f"Failed to load preprocessed CSV: {e}")
            return pd.DataFrame()

    def _extract_malicious_ips(self, df, predictions):
        try:
            if "ip.src" in df.columns:
                df["prediction"] = predictions
                malicious_ips = df[df["prediction"] == 1]["ip.src"].value_counts().index.tolist()
                return malicious_ips[:10]  # Top 10 most frequent malicious IPs
        except Exception as e:
            logger.error(f"Failed to extract malicious IPs: {e}")
        return []