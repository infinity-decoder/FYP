# webapp/IDS/utils/pcap_to_csv.py

import subprocess
import os
from pathlib import Path

class PcapConverter:
    @staticmethod
    def convert(pcap_path, output_dir):
        """
        Convert a .pcap or .pcapng file to CSV using tshark.
        Args:
            pcap_path (str): Full path to input pcap file.
            output_dir (str): Directory to save the output CSV.
        Returns:
            str: Path to generated CSV file.
        """
        try:
            # Windows 11-compatible path handling
            os.makedirs(output_dir, exist_ok=True)
            filename = Path(pcap_path).stem
            output_csv = os.path.join(output_dir, f"{filename}.csv")

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
                "-E", "separator=,",  # CSV format
            ]

            with open(output_csv, 'w', encoding='utf-8') as f:
                subprocess.run(tshark_command, stdout=f, stderr=subprocess.PIPE, check=True)

            print(f"✅ PCAP converted to CSV: {output_csv}")
            return output_csv

        except subprocess.CalledProcessError as e:
            print(f"❌ tshark error: {e.stderr.decode(errors='ignore')}")
            raise
        except Exception as e:
            print(f"❌ PCAP conversion failed: {str(e)}")
            raise
