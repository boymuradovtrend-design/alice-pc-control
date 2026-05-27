import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
PC1_URL = os.environ["PC1_URL"]


def send_command(target, cmd, param=""):
    payload = {"command": cmd, "target": target, "param": param}
    try:
        res = requests.post(f"{PC1_URL}/command", json=payload, timeout=5)
        return res.json().get("result", "Нет ответа от ПК")
    except Exception:
        return "Компьютер недоступен. Проверь ngrok и агент."


def parse_command(text):
    text = text.lower().strip()
    target = "pc1"

    # Обработка команд для YouTube
    yt_triggers = [
        "включи на ютубе",
        "открой на ютубе",
        "найди на ютубе",
        "видео на ютубе",
    ]
    for trigger in yt_triggers:
        if trigger in text:
            query = text.replace(trigger, "").strip()
            return send_command(target, "youtube", query)

    # Системные команды питания
    if "выключи компьютер" in text or "выключи пк" in text:
        return send_command(target, "shutdown")
    elif "перезагрузи" in text:
        return send_command(target, "restart")

    # Команды для запуска игр
    elif "запусти игру" in text or "включи игру" in text:
        game = text.replace("запусти игру", "").replace("включи игру", "").strip()
        return send_command(target, "play_game", game)

    # Универсальное открытие (программы, папки)
    elif "открой" in text or "запусти" in text:
        item = text.replace("открой", "").replace("запусти", "").strip()
        # Быстрый перехват, если слово "игру" было пропущено (например, "запусти кс")
        if item in ["кс", "cs", "cs2", "дота", "dota"]:
            return send_command(target, "play_game", item)
        return send_command(target, "open_item", item)

    return "Я не поняла команду. Скажи, например: «Включи на ютубе хайлайты» или «Запусти кс»."


@app.route("/alice", methods=["POST"])
def alice():
    body = request.json
    user_text = body.get("request", {}).get("original_utterance", "")

    if not user_text:
        answer = "Управление ПК готово к работе."
    else:
        answer = parse_command(user_text)

    return jsonify(
        {
            "version": body.get("version", "1.0"),
            "session": body.get("session", {}),
            "response": {"text": answer, "end_session": False},
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
