#!/usr/bin/env python3
"""Flask Web 服务器 —— 供手机浏览器访问"""

import uuid
from flask import Flask, request, jsonify, render_template, session

from game.engine import GameEngine

app = Flask(__name__)
app.secret_key = "biaoju-mud-2025"

# 内存会话存储 {session_id: GameEngine}
_sessions: dict[str, GameEngine] = {}


def get_engine() -> GameEngine:
    sid = session.get("sid")
    if not sid or sid not in _sessions:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        _sessions[sid] = GameEngine()
    return _sessions[sid]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start():
    """新游戏或获取当前状态"""
    engine = get_engine()
    return jsonify(engine._response())


@app.route("/api/action", methods=["POST"])
def action():
    data = request.json or {}
    choice_id = str(data.get("choice_id", ""))
    text_input = str(data.get("text_input", ""))

    engine = get_engine()
    result = engine.apply_choice(choice_id, text_input)
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def reset():
    sid = session.get("sid")
    if sid and sid in _sessions:
        del _sessions[sid]
    session.pop("sid", None)
    engine = get_engine()
    return jsonify(engine._response())


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    print(f"\n镖局 MUD 已启动")
    print(f"本机访问：http://127.0.0.1:5000")
    print(f"局域网访问：http://{local_ip}:5000")
    print(f"（手机和电脑需在同一 WiFi）\n")

    app.run(host="0.0.0.0", port=5000, debug=False)
