from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
import json
from datetime import datetime

app = Flask(__name__)

# Carregar modelos treinados
rf_model = pickle.load(open("./models/rf_model.pkl", "rb"))
lgbm_model = pickle.load(open("./models/lgbm_model.pkl", "rb"))

# Conversor seguro para JSON
def to_serializable(obj):
    if hasattr(obj, "item"):
        return obj.item()
    return obj

# Endpoint para receber e armazenar tráfego (simulando NWDAF/ADRF)
@app.route("/data-report", methods=["POST"])
def data_report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON inválido ou vazio"}), 400

    timestamp = datetime.now().isoformat()
    os.makedirs("storage", exist_ok=True)
    with open(f"storage/traffic_{timestamp}.json", "w") as f:
        json.dump(data, f, indent=2)

    return jsonify({"status": "received", "timestamp": timestamp})

# Endpoint de inferência com os modelos RF e LGBM
@app.route("/analytics", methods=["POST"])
@app.route("/analytics", methods=["POST"])
def analytics():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON inválido ou vazio"}), 400

    try:
        df = pd.DataFrame([data])
        rf_pred = rf_model.predict(df)[0]
        lgbm_pred = lgbm_model.predict(df)[0]

        # Mapear valores numéricos para strings
        label_map = {
            0: "BENIGN",
            1: "Mirai-greip_flood",
            2: "Mirai-greeth_flood",
            3: "Mirai-udpplain"
        }

        return jsonify({
            "RF_prediction": label_map.get(int(rf_pred), str(rf_pred)),
            "LGBM_prediction": label_map.get(int(lgbm_pred), str(lgbm_pred))
        })

    except Exception as e:
        return jsonify({"error": f"Erro na inferência: {str(e)}"}), 500

# Healthcheck do NWDAF
@app.route("/health")
def health():
    return jsonify({"status": "nw-daf running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
