import pandas as pd

# Carregar dados
dados_treino = pd.read_csv("data/cic_iot2023_filtered.csv")
dados_novos = pd.read_csv("storage/fluxos_recebidos.csv")

# Features comuns
features = list(set(dados_treino.columns) & set(dados_novos.columns))
features.remove("label") if "label" in features else None

print("🔍 Comparando faixas de valores por feature:\n")

for feature in sorted(features):
    min_treino = dados_treino[feature].min()
    max_treino = dados_treino[feature].max()
    min_novo = dados_novos[feature].min()
    max_novo = dados_novos[feature].max()

    fora_faixa = min_novo < min_treino or max_novo > max_treino
    print(f"📌 {feature}:")
    print(f"   → Treino:   min = {min_treino:.2f}, max = {max_treino:.2f}")
    print(f"   → Capturado: min = {min_novo:.2f}, max = {max_novo:.2f}")
    print(f"   ⚠️ {'FORA DA FAIXA' if fora_faixa else 'OK'}\n")
