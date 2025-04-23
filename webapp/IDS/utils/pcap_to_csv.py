import subprocess
import pandas as pd
import os
from pathlib import Path
from django.conf import settings

class PcapConverter:
    @staticmethod
    def convert(pcap_path, output_dir):
        """Convert PCAP to CSV using tshark"""
        try:
            output_path = os.path.join(output_dir, f"{Path(pcap_path).stem}.csv")
            
            tshark_command = [
                "tshark",
                "-r", pcap_path,
                "-T", "fields",
                "-e", "frame.number",
                "-e", "frame.time",
                "-e", "ip.src",
                "-e", "ip.dst",
                "-e", "ip.ttl",
                "-e", "tcp.srcport",
                "-e", "tcp.dstport",
                "-e", "frame.len",
                "-e", "frame.time_delta_displayed",
                "-e", "wlan_radio.signal_db",
                "-E", "header=y",
                "-E", "separator=,"
            ]
            
            # Run conversion
            with open(output_path, 'w') as f:
                subprocess.run(tshark_command, stdout=f, check=True)
                
            return output_path
            
        except Exception as e:
            print(f"❌ PCAP conversion error: {str(e)}")
            raise