import subprocess
import pandas as pd
import os
import zipfile
from pathlib import Path

class PcapConverter:
    """
    A class to detect, extract, and convert PCAP/PCAPNG files to CSV using tshark.
    """

    def __init__(self, input_dir: str, output_dir: str):
        """
        Initializes the converter with input and output directories.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_pcap_files(self):
        """
        Lists all .pcap, .pcapng, and .zip files in the input directory.
        """
        pcap_files = list(self.input_dir.glob("*.pcap")) + list(self.input_dir.glob("*.pcapng"))
        zip_files = list(self.input_dir.glob("*.zip"))

        if not pcap_files and not zip_files:
            print("❌ No PCAP/PCAPNG or ZIP files found.")
            return []

        print("\n📂 Available PCAP files:")
        for idx, file in enumerate(pcap_files, start=1):
            print(f"{idx}. {file.name}")

        if zip_files:
            print("\n📦 Available ZIP files:")
            for idx, file in enumerate(zip_files, start=len(pcap_files) + 1):
                print(f"{idx}. {file.name}")

        print(f"{len(pcap_files) + len(zip_files) + 1}. Process ALL files")

        return pcap_files, zip_files

    def select_files(self, pcap_files, zip_files):
        """
        Allows the user to select which files to convert.
        """
        choice = input("\nEnter file number to process: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(pcap_files):
                return [pcap_files[choice - 1]]
            elif len(pcap_files) < choice <= len(pcap_files) + len(zip_files):
                return [zip_files[choice - len(pcap_files) - 1]]
            elif choice == len(pcap_files) + len(zip_files) + 1:
                return pcap_files + zip_files  # Process all files
            else:
                print("❌ Invalid selection.")
                return []
        except ValueError:
            print("❌ Please enter a valid number.")
            return []

    def extract_zip(self, zip_file: Path):
        """
        Extracts PCAP files from a ZIP archive.
        """
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith(".pcap") or file.endswith(".pcapng"):
                        extracted_path = self.input_dir / file
                        zip_ref.extract(file, self.input_dir)
                        extracted_files.append(extracted_path)
                        print(f"📂 Extracted: {file}")
            return extracted_files
        except Exception as e:
            print(f"❌ Error extracting {zip_file}: {e}")
            return []

    def hex_to_ascii(self, hex_str):
        """
        Converts hexadecimal SSID values to ASCII.
        """
        try:
            return bytes.fromhex(hex_str).decode("utf-8")
        except Exception:
            return hex_str  # Return original if conversion fails

    def convert_pcap_to_csv(self, pcap_file: Path):
        """
        Converts a single PCAP/PCAPNG file to CSV using tshark.
        """
        print(f"🔄 Processing {pcap_file.name}...")

        # Define tshark command
        tshark_command = [
            "tshark",
            "-r",
            str(pcap_file),
            "-T",
            "fields",
            "-e", "frame.number",
            "-e", "frame.time",
            "-e", "wlan_radio.signal_db",
            "-e", "wlan_radio.channel",
            "-e", "wlan.ssid",
            "-e", "_ws.col.Protocol",
            "-e", "ip.ttl",
            "-e", "wlan.bssid",
            "-e", "wlan.sa",
            "-e", "wlan.ta",
            "-e", "wlan.ra",
            "-e", "wlan.da",
            "-e", "ip.src",
            "-e", "ip.dst",
            "-e", "tcp.srcport",
            "-e", "tcp.dstport",
            "-e", "tcp.flags",
            "-e", "_ws.col.Info",
            "-e", "frame.len",
            "-e", "frame.time_delta_displayed",
            "-e", "ppi_gps.lat",
            "-e", "ppi_gps.lon",
            "-e", "ppi_gps.alt",
            "-E", "header=y",
            "-E", "separator=|"
        ]

        # Run tshark
        process = subprocess.Popen(tshark_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            print(f"❌ Error processing {pcap_file.name}: {error.decode()}")
            return False

        # Convert output to DataFrame
        output_lines = output.decode().split("\n")
        if not output_lines:
            print(f"⚠️ No valid packet data found in {pcap_file.name}")
            return False

        header = output_lines[0].split("|")
        data = [line.split("|") for line in output_lines[1:] if line.strip()]
        df = pd.DataFrame(data, columns=header)

        # Convert hexadecimal SSID to ASCII
        if "wlan.ssid" in df.columns:
            df["wlan.ssid"] = df["wlan.ssid"].apply(self.hex_to_ascii)

        # Save CSV file
        output_file = self.output_dir / f"{pcap_file.stem}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Processed: {output_file}")

        return True

    def run(self):
        """
        Main workflow: detect, extract, and convert PCAP/PCAPNG files to CSV.
        """
        pcap_files, zip_files = self.list_pcap_files()
        if not pcap_files and not zip_files:
            return

        selected_files = self.select_files(pcap_files, zip_files)

        # Extract ZIP files first
        extracted_pcap_files = []
        for file in selected_files:
            if file.suffix == ".zip":
                extracted_pcap_files.extend(self.extract_zip(file))
            else:
                extracted_pcap_files.append(file)

        # Process extracted and selected PCAP files
        for pcap_file in extracted_pcap_files:
            self.convert_pcap_to_csv(pcap_file)


if __name__ == "__main__":
    converter = PcapConverter("D:/FYP/data/raw/", "D:/FYP/data/processed/")
    converter.run()
