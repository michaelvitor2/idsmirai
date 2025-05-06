from scapy.all import IP, TCP, send
import random
import time

# IP da máquina alvo (onde roda o seu IDS/sniffer)
dst_ip = "192.168.2.118"

# Portas comumente usadas pelo Mirai (Telnet, HTTP, Exploits)
mirai_ports = [23, 2323, 80, 8080, 7547, 5555]

# Quantidade de pacotes a serem enviados
total_packets = 200

print(f"🚀 Enviando {total_packets} pacotes SYN para {dst_ip}...")

for i in range(total_packets):
    pkt = IP(dst=dst_ip)/TCP(
        sport=random.randint(1024, 65535),
        dport=random.choice(mirai_ports),
        flags="S"
    )
    send(pkt, verbose=0)
    print(f"[{i+1}/{total_packets}] Pacote enviado para porta {pkt.dport}")
    time.sleep(0.02)  # pausa curta entre os pacotes (simula comportamento de scan)
