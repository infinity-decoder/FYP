# webapp/IDS/utils/background_processor.py

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
            print(f"🔧 [Thread] Starting analysis for PCAP ID: {self.pcap_id}")
            pcap_instance = PcapFile.objects.get(id=self.pcap_id)

            # Start analysis
            engine = AnalysisEngine(pcap_instance)
            result = engine.run()

            if result:
                print(f"✅ [Thread] Analysis completed for: {self.pcap_id}")
            else:
                print(f"⚠️ [Thread] Analysis failed for: {self.pcap_id}")

        except PcapFile.DoesNotExist:
            print(f"❌ [Thread] PCAP with ID {self.pcap_id} does not exist.")
        except Exception as e:
            print(f"❌ [Thread] Unexpected error: {str(e)}")
            traceback.print_exc()
