import pandas as pd
import lightgbm as lgb
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Carregar dados
file = "data/cic_iot2023_filtered.csv"
df = pd.read_csv(file)
X = df.drop(columns=["label"])
y = df["label"]

# Treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y)

# Random Forest
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)
pickle.dump(rf, open("models/rf_model.pkl", "wb"))

# LightGBM
lgbm = lgb.LGBMClassifier()
lgbm.fit(X_train, y_train)
pickle.dump(lgbm, open("models/lgbm_model.pkl", "wb"))
