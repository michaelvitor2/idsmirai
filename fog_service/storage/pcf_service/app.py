from flask import Flask, jsonify, render_template
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
LOG_FILE = "policy_log.json"

def save_log(entry):
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def gerar_trafego(perfil="benigno"):
    if perfil == "benigno":
        # Amostra real do dataset com label = 0 (BENIGN)
        return {
            "flow_duration": 79849,
            "Header_Length": 40,
            "Protocol Type": 6,
            "Duration": 69531,
            "ack_count": 0,
            "syn_count": 1,
            "urg_count": 0,
            "rst_count": 0,
            "HTTP": 1,
            "UDP": 0,
            "Min": 0.0,
            "Covariance": 0.0,
            "Variance": 0.0
        }
    else:
        # Simulação maliciosa
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

def realizar_policy_check(perfil):
    traffic = gerar_trafego(perfil)
    try:
        r = requests.post("http://localhost:5000/analytics", json=traffic)
        data = r.json()
    except Exception as e:
        return jsonify({"error": f"Falha ao consultar NWDAF: {str(e)}"}), 500

    # Lógica ajustada para rótulos numéricos (0 = BENIGN)
    try:
        rf_pred = int(data['RF_prediction'])
        lgbm_pred = int(data['LGBM_prediction'])
    except Exception as e:
        return jsonify({"error": f"Erro ao interpretar predição: {str(e)}"}), 500

    action = "BLOCK" if rf_pred != 0 and lgbm_pred != 0 else "ALLOW"

    log = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "perfil_esperado": perfil.upper(),
        "rf": rf_pred,
        "lgbm": lgbm_pred
    }
    save_log(log)

    return jsonify({
        "action": action,
        "nw-daf-response": data,
        "input-traffic": traffic
    })

@app.route("/policy-check")
def policy_check():
    return realizar_policy_check("malicioso")

@app.route("/policy-check-allow")
def policy_check_allow():
    return realizar_policy_check("benigno")

@app.route("/policy-check-block")
def policy_check_block():
    return realizar_policy_check("malicioso")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/dashboard/data")
def dashboard_data():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001)
