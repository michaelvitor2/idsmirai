import pandas as pd
import requests
import time

df = pd.read_csv("data/cic_iot2023_filtered.csv").drop(columns=["label"])

for i in range(5):
    amostra = df.iloc[i].to_dict()
    resp = requests.post("http://localhost:5000/analytics", json=amostra)
    print(f"Amostra {i+1}: {resp.json()}")
    time.sleep(1)
