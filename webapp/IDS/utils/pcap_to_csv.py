import subprocess
import os
from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class PcapConverter:
    def __init__(self):
        # Must match features used during training
        self.field_mapping = {
            'frame.number': 'frame.number',
            '_ws.col.protocol': '_ws.col.Protocol',
            'ip.ttl': 'ip.ttl',
            'ip.src': 'ip.src',
            'ip.dst': 'ip.dst',
            'tcp.srcport': 'tcp.srcport',
            'tcp.dstport': 'tcp.dstport',
            'tcp.flags': 'tcp.flags',
            '_ws.col.info': '_ws.col.Info',
            'frame.len': 'frame.len',
            'frame.time_delta_displayed': 'frame.time_delta_displayed'
        }

    def convert(self, pcap_path, output_dir):
        try:
            pcap_path = Path(pcap_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_csv_path = output_dir / f"{pcap_path.stem}.csv"

            # Build tshark command
            cmd = [
                "tshark",
                "-r", str(pcap_path),
                "-T", "fields",
                "-E", "header=y",
                "-E", "separator=|"
            ]
            for tshark_field in self.field_mapping.values():
                cmd += ["-e", tshark_field]

            logger.info(f"🔄 Running TShark on {pcap_path.name}")
            with open(output_csv_path, 'w', encoding='utf-8') as outfile:
                subprocess.run(
                    cmd,
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )

            if not output_csv_path.exists() or output_csv_path.stat().st_size == 0:
                raise ValueError(f"TShark produced empty CSV for: {pcap_path.name}")

            # Load CSV and assign correct column names
            df = pd.read_csv(output_csv_path, sep='|')
            df.columns = list(self.field_mapping.keys())

            # Ensure all fields are numeric where needed
            for col in self.field_mapping.keys():
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

            # Save standardized output
            df.to_csv(output_csv_path, index=False)
            logger.info(f"✅ CSV created at: {output_csv_path}")
            return str(output_csv_path)

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ TShark failed: {e.stderr.strip()}")
            raise ValueError(f"PCAP conversion failed: {e.stderr.strip()}")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise RuntimeError(f"Unexpected error: {str(e)}")
