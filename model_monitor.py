import pandas as pd
import requests
import time
from datetime import datetime

# Quantas amostras de cada perfil
N = 20

# Geração de tráfego com base nas mesmas features usadas no treinamento
def gerar_trafego(perfil):
    if perfil == "benigno":
        return {
            "flow_duration": 10000,
            "Header_Length": 30,
            "Protocol Type": 6,
            "Duration": 8000,
            "ack_count": 10,
            "syn_count": 2,
            "urg_count": 0,
            "rst_count": 0,
            "HTTP": 1,
            "UDP": 0,
            "Min": 0.5,
            "Covariance": 0.002,
            "Variance": 0.01
        }
    else:  # malicioso
        return {
            "flow_duration": 90000,
            "Header_Length": 60,
            "Protocol Type": 17,
            "Duration": 95000,
            "ack_count": 0,
            "syn_count": 0,
            "urg_count": 1,
            "rst_count": 5,
            "HTTP": 0,
            "UDP": 1,
            "Min": 0.01,
            "Covariance": 1.0,
            "Variance": 5.0
        }

logs = []

# Simular ambos os perfis
for perfil in ["benigno", "malicioso"]:
    for _ in range(N):
        data = gerar_trafego(perfil)
        try:
            resp = requests.post("http://localhost:5000/analytics", json=data)
            pred = resp.json()
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "perfil_real": perfil.upper(),
                "rf_pred": pred.get("RF_prediction", "ERRO"),
                "lgbm_pred": pred.get("LGBM_prediction", "ERRO")
            })
        except Exception as e:
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "perfil_real": perfil.upper(),
                "rf_pred": "ERRO",
                "lgbm_pred": "ERRO"
            })
        time.sleep(0.5)

# Salvar os resultados para análise posterior
df = pd.DataFrame(logs)
df.to_csv("storage/monitoramento_resultados.csv", index=False)
print("✓ Monitoramento concluído — resultados salvos em storage/monitoramento_resultados.csv")
