# FYP/webapp/IDS/utils/pcap_to_csv.py
import subprocess
import os
from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class PcapConverter:
    def __init__(self):
        # Universal field names that work across TShark versions
        self.field_mapping = {
            'frame_number': 'frame.number',
            'protocol': 'frame.protocols',  # More reliable than _ws.col.Protocol
            'ip_ttl': 'ip.ttl',
            'ip_src': 'ip.src',
            'ip_dst': 'ip.dst',
            'tcp_srcport': 'tcp.srcport',
            'tcp_dstport': 'tcp.dstport',
            'tcp_flags': 'tcp.flags',
            'frame_info': 'frame.info',  # Alternative to _ws.col.Info
            'frame_len': 'frame.len',
            'time_delta': 'frame.time_delta',
            'signal_db': 'wlan_radio.signal_db'
        }

    def convert(self, pcap_path, output_dir):
        """Robust PCAP to CSV conversion with fallback fields"""
        try:
            output_path = os.path.join(output_dir, f"{Path(pcap_path).stem}.csv")
            
            # Build tshark command with verified fields
            cmd = [
                "tshark",
                "-r", pcap_path,
                "-T", "fields",
                "-E", "header=y",
                "-E", "separator=|",
            ]
            
            # Add all fields that should work universally
            cmd.extend(f"-e {field}" for field in self.field_mapping.values())
            
            # Run conversion
            with open(output_path, 'w') as outfile:
                result = subprocess.run(
                    cmd,
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            
            # Verify output file
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ValueError("Conversion produced empty output")
            
            # Standardize column names
            df = pd.read_csv(output_path, sep='|')
            df.columns = list(self.field_mapping.keys())
            df.to_csv(output_path, index=False)
            
            logger.info(f"Successfully converted PCAP to CSV: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"PCAP conversion failed: {e.stderr.strip()}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected conversion error: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)