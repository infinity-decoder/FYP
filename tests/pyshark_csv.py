import pyshark
import pandas as pd
import os
from pathlib import Path

class PcapProcessor:
    """
    A class to process PCAP/PCAPNG files and convert them into a CSV dataset.
    """
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize the processor with input and output directories.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_pcap_files(self):
        """
        Lists all .pcap and .pcapng files in the input directory.
        """
        pcap_files = list(self.input_dir.glob("*.pcap")) + list(self.input_dir.glob("*.pcapng"))
        if not pcap_files:
            print("❌ No PCAP/PCAPNG files found.")
            return []
        
        print("\n📂 Available PCAP files:")
        for idx, file in enumerate(pcap_files, start=1):
            print(f"{idx}. {file.name}")
        print(f"{len(pcap_files) + 1}. Process ALL files")

        return pcap_files

    def select_pcap_file(self, pcap_files):
        """
        Allows the user to select a PCAP file for processing.
        """
        choice = input("\nEnter file number to process: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(pcap_files):
                return [pcap_files[choice - 1]]
            elif choice == len(pcap_files) + 1:
                return pcap_files  # Process all files
            else:
                print("❌ Invalid selection.")
                return []
        except ValueError:
            print("❌ Please enter a valid number.")
            return []

    def extract_packet_info(self, packet):
        """
        Extracts relevant information from a packet.
        """
        try:
            return {
                "timestamp": getattr(packet, "sniff_time", None),
                "source_ip": getattr(packet.ip, "src", None) if hasattr(packet, "ip") else None,
                "destination_ip": getattr(packet.ip, "dst", None) if hasattr(packet, "ip") else None,
                "protocol": getattr(packet, "transport_layer", None),
                "packet_size": getattr(packet, "length", None),
                "source_port": getattr(packet[packet.transport_layer], "srcport", None) if hasattr(packet, "transport_layer") else None,
                "destination_port": getattr(packet[packet.transport_layer], "dstport", None) if hasattr(packet, "transport_layer") else None,
                "tcp_flags": getattr(packet.tcp, "flags", None) if hasattr(packet, "tcp") else None,
                "ttl": getattr(packet.ip, "ttl", None) if hasattr(packet, "ip") else None,
                "info": packet.highest_layer if hasattr(packet, "highest_layer") else None  # Get protocol layer
            }
        except AttributeError:
            return None  # Skip packets with missing fields

    def process_pcap(self, input_file: Path):
        """
        Converts a single PCAP/PCAPNG file into a CSV file.
        """
        print(f"🔄 Processing {input_file.name}...")

        try:
            capture = pyshark.FileCapture(
                str(input_file),
                display_filter="tcp || udp || icmp",
                use_json=True  # Fixes include_raw error
            )

            extracted_data = [self.extract_packet_info(packet) for packet in capture if self.extract_packet_info(packet)]
            capture.close()

            if not extracted_data:
                print(f"⚠️ No valid packet data extracted from {input_file.name}")
                return

            df = pd.DataFrame(extracted_data)
            output_file = self.output_dir / f"{input_file.stem}.csv"
            df.to_csv(output_file, index=False)

            print(f"✅ Processed: {output_file}")

        except Exception as e:
            print(f"❌ Error processing {input_file.name}: {e}")

    def run(self):
        """
        Runs the full interactive PCAP processing workflow.
        """
        pcap_files = self.list_pcap_files()
        if not pcap_files:
            return

        selected_files = self.select_pcap_file(pcap_files)
        for file in selected_files:
            self.process_pcap(file)


if __name__ == "__main__":
    processor = PcapProcessor("D:/FYP/data/raw/", "D:/FYP/data/processed/")
    processor.run()
