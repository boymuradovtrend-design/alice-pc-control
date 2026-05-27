from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

PC1_URL = os.environ["PC1_URL"]

def parse_command(text):
    text = text.lower()

    if "первый" in text or "первом" in text:
        target = "pc1"
    elif "второй" in text or "втором" in text:
        target = "pc2"
    else:
        target = "pc1"

    if "выключи" in text:
        cmd = "shutdown"
    elif "перезагрузи" in text:
        cmd = "restart"
    elif "статус" in text or "память" in text or "температура" in text or "процессор" in text:
        cmd = "stats"
    elif "открой" in text or "запусти" in text:
        cmd = "open"
        for word in ["браузер", "блокнот", "калькулятор", "проводник"]:
            if word in text:
                return send_command(target, cmd, word)
        return "Не понял какую программу открыть"
    else:
        return "Не понял команду. Попробуй: выключи, перезагрузи, статус, открой браузер"

    return send_command(target, cmd)

def send_command(target, cmd, app_name=None):
    payload = {"command": cmd, "target": target}
    if app_name:
        payload["app"] = app_name
    try:
        res = requests.post(f"{PC1_URL}/command", json=payload, timeout=5)
        return res.json().get("result", "Нет ответа")
    except:
        return "Компьютер не отвечает"

@app.route("/alice", methods=["POST"])
def alice():
    body = request.json
    user_text = body.get("request", {}).get("original_utterance", "")
    if not user_text:
        answer = "Управление компьютером. Скажи например: статус первого ПК или выключи первый ПК"
    else:
        answer = parse_command(user_text)
    return jsonify({
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {"text": answer, "end_session": False}
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
