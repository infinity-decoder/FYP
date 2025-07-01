import pyshark
import pandas as pd
from collections import defaultdict
from datetime import datetime

# Load the PCAP file
pcap_path = 'D:/FYP/data/raw/attack_traffic_01.pcapng'
cap = pyshark.FileCapture(pcap_path, use_json=True, include_raw=False)

flows = defaultdict(list)

def get_tuple(pkt):
    try:
        proto = pkt.transport_layer
        src_ip = pkt.ip.src
        dst_ip = pkt.ip.dst
        src_port = pkt[pkt.transport_layer].srcport
        dst_port = pkt[pkt.transport_layer].dstport
        return (src_ip, dst_ip, src_port, dst_port, proto)
    except:
        return None

for pkt in cap:
    if 'IP' in pkt:
        flow_id = get_tuple(pkt)
        if flow_id is not None:
            try:
                timestamp = float(pkt.sniff_timestamp)
                pkt_len = int(pkt.length)
                tcp_flags = pkt.tcp.flags if 'TCP' in pkt else '0'
                flows[flow_id].append((timestamp, pkt_len, tcp_flags))
            except Exception as e:
                continue

cap.close()

flow_features = []

for flow, pkts in flows.items():
    timestamps = [p[0] for p in pkts]
    sizes = [p[1] for p in pkts]
    flags = [p[2] for p in pkts]
    
    duration = max(timestamps) - min(timestamps)
    total_pkts = len(pkts)
    total_bytes = sum(sizes)
    avg_pkt_size = total_bytes / total_pkts if total_pkts else 0

    inter_arrival = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
    avg_inter_arrival = sum(inter_arrival) / len(inter_arrival) if inter_arrival else 0

    src_ip, dst_ip, src_port, dst_port, proto = flow
    direction_ratio = 1.0  # Placeholder; you can define it based on packet direction logic
    syn_count = sum('0x0002' in f for f in flags)  # SYN flag
    fin_count = sum('0x0001' in f for f in flags)  # FIN flag

    flow_features.append({
        'src_ip': src_ip,
        'dst_ip': dst_ip,
        'src_port': src_port,
        'dst_port': dst_port,
        'protocol': proto,
        'duration': duration,
        'total_packets': total_pkts,
        'total_bytes': total_bytes,
        'avg_packet_size': avg_pkt_size,
        'avg_inter_arrival_time': avg_inter_arrival,
        'syn_count': syn_count,
        'fin_count': fin_count,
        'direction_ratio': direction_ratio
    })

df = pd.DataFrame(flow_features)
df.to_csv('flow_features.csv', index=False)
print("Features saved to flow_features.csv")
