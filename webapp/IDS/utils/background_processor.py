import threading
import traceback
from .analysis_engine import AnalysisEngine
from IDS.models import PcapFile

class BackgroundAnalyzer(threading.Thread):
    def __init__(self, pcap_id):
        super().__init__()
        self.pcap_id = pcap_id

    def run(self):
        try:
            print(f"🔧 [BackgroundAnalyzer] Starting analysis for PCAP ID: {self.pcap_id}")
            pcap_instance = PcapFile.objects.get(id=self.pcap_id)

            # Initialize and run analysis
            engine = AnalysisEngine(pcap_instance)
            engine.run()

            print(f"✅ [BackgroundAnalyzer] Analysis completed for PCAP ID: {self.pcap_id}")
        except PcapFile.DoesNotExist:
            print(f"❌ [BackgroundAnalyzer] PCAP with ID {self.pcap_id} does not exist.")
        except Exception as e:
            print(f"❌ [BackgroundAnalyzer] Error: {str(e)}")
            traceback.print_exc()
