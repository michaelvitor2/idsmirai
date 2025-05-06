import pandas as pd
from sklearn.metrics import classification_report

# Carrega os dados
df = pd.read_csv("storage/teste_replay_resultado.csv")

# Converte rótulos reais para 0 (BENIGN) e 1 (MALICIOUS)
df["real_label"] = df["real_label"].apply(lambda x: 0 if x == "BENIGN" else 1)

# Converte predições para inteiro
df["RF_prediction"] = pd.to_numeric(df["RF_prediction"], errors="coerce")
df["LGBM_prediction"] = pd.to_numeric(df["LGBM_prediction"], errors="coerce")

# Converte predições para 0 ou 1
df["RF_bin"] = df["RF_prediction"].apply(lambda x: 0 if x == 0 else 1)
df["LGBM_bin"] = df["LGBM_prediction"].apply(lambda x: 0 if x == 0 else 1)

# Avaliar binário: 0 = benigno, 1 = malicioso
for modelo in ["RF_bin", "LGBM_bin"]:
    print(f"\n>>> Avaliação do modelo: {modelo}")
    print(classification_report(df["real_label"], df[modelo], target_names=["BENIGN", "MALICIOUS"], zero_division=0))
