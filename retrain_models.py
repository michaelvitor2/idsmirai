import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split

# Caminho do arquivo gerado pelo NWDAF
csv_path = "storage/last_predictions.csv"

# Verifica se o arquivo existe
if not os.path.exists(csv_path):
    print("⚠️ Nenhum dado disponível para re-treinamento.")
    exit()

# Carrega os dados
df = pd.read_csv(csv_path)

# Remove colunas que não são usadas no treinamento
for col in ["RF_prediction", "LGBM_prediction", "timestamp"]:
    if col in df.columns:
        df = df.drop(columns=[col])

# Verifica se coluna 'label' está presente
if "label" not in df.columns:
    print("❌ A coluna 'label' não foi encontrada no dataset. Re-treinamento abortado.")
    exit()

# Separa features e rótulo
X = df.drop(columns=["label"])
y = df["label"]

# Divide em treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Re-treina modelos
rf = RandomForestClassifier().fit(X_train, y_train)
lgbm = LGBMClassifier().fit(X_train, y_train)

# Salva os modelos atualizados
pickle.dump(rf, open("models/rf_model.pkl", "wb"))
pickle.dump(lgbm, open("models/lgbm_model.pkl", "wb"))

print("✅ Modelos re-treinados e salvos com sucesso.")
