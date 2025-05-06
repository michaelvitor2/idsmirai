from scapy.all import sniff, IP, TCP, UDP, GRE, ICMP
from datetime import datetime
import pandas as pd
import requests
import numpy as np
import os
import json
import time
from collections import defaultdict

flow_table = defaultdict(list)
flow_timestamps = {}
LOG_FILE = "policy_log.json"

def to_serializable(obj):
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def extrair_features(pacotes):
    times = [pkt.time for pkt in pacotes]
    tamanho_headers = sum(len(pkt) for pkt in pacotes)

    if TCP in pacotes[0]:
        protocolo = 6
    elif UDP in pacotes[0]:
        protocolo = 17
    elif GRE in pacotes[0]:
        protocolo = 47
    else:
        protocolo = 0

    flags = {"ACK": 0, "SYN": 0, "URG": 0, "RST": 0}
    tamanhos = []

    for pkt in pacotes:
        if TCP in pkt:
            tcp_flags = pkt[TCP].flags
            if tcp_flags & 0x10: flags["ACK"] += 1
            if tcp_flags & 0x02: flags["SYN"] += 1
            if tcp_flags & 0x20: flags["URG"] += 1
            if tcp_flags & 0x04: flags["RST"] += 1
        tamanhos.append(len(pkt))

    return {
        "flow_duration": max(times) - min(times) if len(times) > 1 else 0,
        "Header_Length": tamanho_headers,
        "Protocol Type": protocolo,
        "Duration": max(times) - min(times) if len(times) > 1 else 0,
        "ack_count": flags["ACK"],
        "syn_count": flags["SYN"],
        "urg_count": flags["URG"],
        "rst_count": flags["RST"],
        "HTTP": 1 if any((TCP in pkt and (pkt[TCP].dport == 80 or pkt[TCP].sport == 80)) for pkt in pacotes) else 0,
        "UDP": 1 if protocolo == 17 else 0,
        "GRE": 1 if protocolo == 47 else 0,
        "Min": np.min(tamanhos),
        "Covariance": float(np.cov(tamanhos)) if len(tamanhos) > 1 else 0,
        "Variance": float(np.var(tamanhos))
    }

def salvar_log(log):
    os.makedirs("storage", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                pass
    data.append(log)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def salvar_fluxo_csv(features):
    os.makedirs("storage", exist_ok=True)
    df = pd.DataFrame([features])
    csv_path = "storage/fluxos_recebidos.csv"
    df.to_csv(csv_path, mode="a", index=False, header=not os.path.exists(csv_path))

def processar_fluxo(pacotes, chave):
    features = extrair_features(pacotes)
    salvar_fluxo_csv(features)

    try:
        safe_features = {k: to_serializable(v) for k, v in features.items()}
        resp = requests.post("http://localhost:5000/analytics", json=safe_features)
        resultado = resp.json()

        rf_pred = resultado.get("RF_prediction", "")
        lgbm_pred = resultado.get("LGBM_prediction", "")

        if "Mirai" in rf_pred or "Mirai" in lgbm_pred:
            action = "BLOCK"
        elif rf_pred == "BENIGN" and lgbm_pred == "BENIGN":
            action = "ALLOW"
        else:
            action = "BLOCK"

        log = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "rf": rf_pred,
            "lgbm": lgbm_pred,
            "flow_key": chave
        }
        salvar_log(log)

        print(f"[{log['timestamp']}] {chave} → {action} ({rf_pred}, {lgbm_pred})")

    except Exception as e:
        print(f"❌ Erro ao consultar NWDAF: {e}")

def pacote_valido(pkt):
    if pkt.haslayer(TCP):
        if pkt[TCP].sport in (23, 5000, 5001) or pkt[TCP].dport in (23, 5000, 5001):
            return False
    if pkt.haslayer(UDP):
        if pkt[UDP].sport in (23, 5000, 5001) or pkt[UDP].dport in (23, 5000, 5001):
            return False
    return True

def handle_packet(pkt):
    if not (IP in pkt):
        return

    if not pacote_valido(pkt):
        return

    ip = pkt[IP]

    if TCP in pkt:
        proto = "TCP"
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
    elif UDP in pkt:
        proto = "UDP"
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport
    elif GRE in pkt:
        proto = "GRE"
        sport = 0
        dport = 0
    elif ICMP in pkt:
        proto = "ICMP"
        sport = 0
        dport = 0
    else:
        return

    chave = f"{ip.src}:{sport}->{ip.dst}:{dport}_{proto}"

    flow_table[chave].append(pkt)
    if chave not in flow_timestamps:
        flow_timestamps[chave] = time.time()

    if len(flow_table[chave]) >= 1:
        processar_fluxo(flow_table[chave], chave)
        del flow_table[chave]
        del flow_timestamps[chave]

if __name__ == "__main__":
    iface = "lo"  # ou "enp0s3" dependendo da interface que quiser escutar
    print(f"🎯 Escutando interface `{iface}` para fluxos IPv4 TCP/UDP/GRE/ICMP...")
    bpf_filter = "ip and not (port 23 or port 5000 or port 5001)"
    sniff(iface=iface, prn=handle_packet, store=False, promisc=True, filter=bpf_filter)
