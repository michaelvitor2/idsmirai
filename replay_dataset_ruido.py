import pandas as pd
import requests
import time
import os
import numpy as np
from datetime import datetime

# Cria diretório de armazenamento
os.makedirs("storage", exist_ok=True)

# Carrega o dataset
df = pd.read_csv("data/cic_iot2023_filtered.csv")

# Features de entrada
features = ['flow_duration', 'Header_Length', 'Protocol Type', 'Duration',
            'ack_count', 'syn_count', 'urg_count', 'rst_count', 'HTTP', 'UDP',
            'Min', 'Covariance', 'Variance']

# Separar BENIGN e MALICIOUS
benign_df = df[df["label"] == 0].sample(20, random_state=42)
mal_df = df[df["label"] != 0].sample(20, random_state=42)

# Aplica ruído nas features numéricas
def add_noise(row, noise_level=0.05):
    noisy_row = row.copy()
    for col in features:
        if isinstance(row[col], (int, float, np.integer, np.floating)):
            variation = row[col] * noise_level
            noisy_row[col] += np.random.uniform(-variation, variation)
    return noisy_row

# Aplica ruído e prepara o conjunto
samples = pd.concat([benign_df, mal_df])
logs = []

for i, row in samples.iterrows():
    real_label = "BENIGN" if row["label"] == 0 else "MALICIOUS"
    noisy_sample = add_noise(row)

    data = noisy_sample[features].to_dict()

    try:
        resp = requests.post("http://localhost:5000/analytics", json=data)
        pred = resp.json()
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "real_label": real_label,
            "RF_prediction": pred.get("RF_prediction"),
            "LGBM_prediction": pred.get("LGBM_prediction")
        })
        print(f"{real_label} (RUÍDO) => RF: {pred.get('RF_prediction')} | LGBM: {pred.get('LGBM_prediction')}")
    except Exception as e:
        print(f"Erro ao enviar amostra: {e}")

    time.sleep(0.5)

# Salva os resultados
pd.DataFrame(logs).to_csv("storage/teste_ruido_resultado.csv", index=False)
print("✓ Teste com ruído concluído. Resultados salvos.")
