# FYP/webapp/IDS/utils/pcap_to_csv.py
import subprocess
import os
from pathlib import Path

class PcapConverter:
    def __init__(self):
        # Consistent tshark fields that match our feature requirements
        self.tshark_fields = [
            "frame.len",
            "ip.ttl",
            "tcp.srcport",
            "tcp.dstport",
            "frame.time_delta_displayed",
            "wlan_radio.signal_db",
            "ip.src"  # For malicious IP reporting
        ]

    def convert(self, pcap_path, output_dir):
        """Convert PCAP to CSV with consistent fields"""
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
                
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise ValueError(f"PCAP conversion failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected conversion error: {str(e)}")