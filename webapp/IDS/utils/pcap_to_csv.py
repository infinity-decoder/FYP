import subprocess
import os
from pathlib import Path
import pandas as pd
import logging
from io import StringIO

logger = logging.getLogger(__name__)

class PcapConverter:
    def __init__(self):
        self.required_fields = [
            'frame.number',
            'frame.time',
            'wlan_radio.signal_db',
            'wlan_radio.channel',
            'wlan.ssid',
            '_ws.col.Protocol',
            'ip.ttl',
            'ip.src',
            'ip.dst',
            'tcp.srcport',
            'tcp.dstport',
            'frame.len',
            'frame.time_delta_displayed'
        ]

    def convert(self, pcap_path, output_dir):
        """
        Convert PCAP to CSV with robust error handling and consistent formatting
        Returns:
            str: Path to generated CSV file
        Raises:
            subprocess.CalledProcessError: If tshark command fails
            Exception: For other conversion errors
        """
        try:
            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate output path
            pcap_path = Path(pcap_path)
            output_csv = Path(output_dir) / f"{pcap_path.stem}.csv"
            
            # Build tshark command with pipe delimiter
            tshark_command = [
                "tshark",
                "-r", str(pcap_path),
                "-T", "fields",
                *[item for field in self.required_fields for item in ("-e", field)],
                "-E", "header=y",
                "-E", "separator=|",
                "-E", "occurrence=f"  # Get first occurrence of each field
            ]

            logger.info(f"Executing tshark command: {' '.join(tshark_command)}")
            
            # Run tshark and capture output
            result = subprocess.run(
                tshark_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            # Clean and validate the output
            cleaned_csv = self._clean_tshark_output(result.stdout)
            
            # Write cleaned output to file
            with open(output_csv, 'w') as f:
                f.write(cleaned_csv)
            
            logger.info(f"Successfully converted PCAP to CSV: {output_csv}")
            return str(output_csv)

        except subprocess.CalledProcessError as e:
            error_msg = f"tshark failed with error: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            logger.error(f"PCAP conversion failed: {str(e)}")
            raise

    def _clean_tshark_output(self, raw_output):
        """
        Clean and validate tshark output to ensure consistent CSV format
        Args:
            raw_output (str): Raw output from tshark command
        Returns:
            str: Cleaned CSV content
        """
        try:
            # Read into DataFrame for cleaning
            df = pd.read_csv(StringIO(raw_output), sep='|')
            
            # Ensure all required columns are present
            for col in self.required_fields:
                if col not in df.columns:
                    df[col] = None  # Add missing columns with null values
            
            # Clean SSID fields if present
            if 'wlan.ssid' in df.columns:
                df['wlan.ssid'] = df['wlan.ssid'].apply(self._hex_to_ascii)
            
            # Convert back to CSV string
            output = StringIO()
            df.to_csv(output, sep='|', index=False)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to clean tshark output: {str(e)}")
            raise RuntimeError("Failed to process tshark output") from e

    def _hex_to_ascii(self, hex_str):
        """Convert hexadecimal SSID to ASCII if possible"""
        if not isinstance(hex_str, str) or not hex_str:
            return hex_str
            
        try:
            # Remove any non-hex characters
            clean_hex = ''.join(c for c in hex_str if c in '0123456789abcdefABCDEF')
            if len(clean_hex) % 2 != 0:
                return hex_str  # Not valid hex
            return bytes.fromhex(clean_hex).decode('utf-8', errors='ignore')
        except:
            return hex_str