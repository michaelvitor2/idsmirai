import pandas as pd
import requests
import time
import os
from datetime import datetime

# Arquivo original do CICIoT
dataset_path = "data/cic_iot2023_filtered.csv"
df = pd.read_csv(dataset_path)

# Número de amostras para simular
df = df.sample(n=50, random_state=42).reset_index(drop=True)

logs = []

for i, row in df.iterrows():
    features = row.drop("label").to_dict()
    try:
        r = requests.post("http://localhost:5000/analytics", json=features)
        resultado = r.json()
        log = {
            "timestamp": datetime.now().isoformat(),
            "real_label": row["label"],
            "RF_prediction": resultado.get("RF_prediction"),
            "LGBM_prediction": resultado.get("LGBM_prediction")
        }
        print(f"[{i+1:02d}] Real: {row['label']} → Predito: {log['RF_prediction']}, {log['LGBM_prediction']}")
        logs.append(log)
        time.sleep(0.2)
    except Exception as e:
        print(f"❌ Erro na amostra {i+1}: {e}")

# Salvar resultado em CSV
os.makedirs("storage", exist_ok=True)
pd.DataFrame(logs).to_csv("storage/teste_replay_resultado.csv", index=False)
print("✅ Teste concluído. Resultados salvos em storage/teste_replay_resultado.csv")
