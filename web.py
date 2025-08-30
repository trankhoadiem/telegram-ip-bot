# web.py
from flask import Flask, request, redirect
import sqlite3, time, os

app = Flask(__name__)

DB_PATH = "db.sqlite3"

def log_click(link_id, ip, ua):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO logs (link_id, ip, user_agent, timestamp) VALUES (?,?,?,?)",
              (link_id, ip, ua, int(time.time())))
    conn.commit()
    conn.close()

def get_target(link_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT target FROM links WHERE id=?", (link_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

@app.route("/")
def home():
    return "✅ Web service cho Telegram Bot đang chạy!"

@app.route("/<link_id>")
def redirect_link(link_id):
    target = get_target(link_id)
    if not target:
        return "❌ Link không tồn tại hoặc đã bị xóa.", 404

    # Lấy IP và User-Agent
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "Unknown")

    # Ghi log
    log_click(link_id, ip, ua)

    # Redirect về URL gốc
    return redirect(target, code=302)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
