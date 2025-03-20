import pyshark
import pandas as pd
import os
from pathlib import Path

# Define input and output file paths
RAW_DATA_PATH = Path("D:/FYP/data/raw/network_traffic.pcapng")  # Ensure correct path
OUTPUT_PATH = Path("D:/FYP/data/processed/traffic_data.csv")

# Ensure output directory exists
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Check if the input file exists
if not RAW_DATA_PATH.exists():
    raise FileNotFoundError(f"Input file not found: {RAW_DATA_PATH}")

def process_pcap_to_csv(input_path, output_path):
    """
    Extract network packet features from PCAP/PCAPNG file and save to CSV.
    """
    try:
        # Load the PCAP file
        capture = pyshark.FileCapture(
            str(input_path),
            display_filter="tcp || udp || icmp",  # Only capture key protocols
            include_raw=False  # Raw data not needed
        )

        extracted_data = []

        # Process packets
        for packet in capture:
            try:
                packet_data = {
                    "timestamp": packet.sniff_time,  # Timestamp
                    "source_ip": getattr(packet.ip, "src", None),  # Source IP
                    "destination_ip": getattr(packet.ip, "dst", None),  # Destination IP
                    "protocol": getattr(packet, "transport_layer", None),  # Transport layer protocol
                    "packet_size": getattr(packet, "length", None),  # Packet size
                    "info": packet.highest_layer  # Highest protocol layer
                }
                extracted_data.append(packet_data)
            except AttributeError:
                continue  # Skip packets with missing fields

        # Close capture
        capture.close()

        # Convert data to CSV
        df = pd.DataFrame(extracted_data)
        df.to_csv(output_path, index=False)
        print(f"✅ Data extracted and saved to {output_path}")

    except Exception as e:
        print(f"❌ Error processing PCAP file: {e}")

if __name__ == "__main__":
    process_pcap_to_csv(RAW_DATA_PATH, OUTPUT_PATH)
