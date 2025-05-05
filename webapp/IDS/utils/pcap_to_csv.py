# FYP/webapp/IDS/utils/pcap_to_csv.py
import subprocess
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PcapConverter:
    def __init__(self):
        # Define EXACT fields that match your training data features
        self.tshark_fields = [
            "frame.number",
            "_ws.col.Protocol",
            "ip.ttl",
            "ip.src",
            "ip.dst",
            "tcp.srcport",
            "tcp.dstport",
            "tcp.flags",
            "_ws.col.Info",
            "frame.len",
            "frame.time_delta_displayed",
            "wlan_radio.signal_db"  # Additional feature used in your models
        ]

    def convert(self, pcap_path, output_dir):
        """Convert PCAP to CSV with consistent fields that match training data"""
        try:
            output_path = os.path.join(output_dir, f"{Path(pcap_path).stem}.csv")
            
            # Build tshark command with exact fields we need
            cmd = [
                "tshark",
                "-r", pcap_path,
                "-T", "fields",
                "-E", "header=y",
                "-E", "separator=|",
            ] + [f"-e {field}" for field in self.tshark_fields]
            
            # Run conversion
            with open(output_path, 'w') as outfile:
                subprocess.run(cmd, stdout=outfile, check=True)
            
            logger.info(f"Successfully converted PCAP to CSV at {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"PCAP conversion failed: {str(e)}")
            raise ValueError(f"PCAP conversion failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected conversion error: {str(e)}")
            raise RuntimeError(f"Unexpected conversion error: {str(e)}")