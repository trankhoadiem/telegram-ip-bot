# web.py
from flask import Flask, request, redirect
import sqlite3, time, os

app = Flask(__name__)
DB_PATH = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id TEXT PRIMARY KEY,
        target TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id TEXT,
        ip TEXT,
        user_agent TEXT,
        timestamp INTEGER
    )
    """)
    conn.commit()
    conn.close()

# init DB ở web (an toàn nếu cả 2 service cùng db)
init_db()

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
    return "✅ Logger server đang chạy. Dùng bot Telegram để tạo link!"

@app.route("/<link_id>")
def tracker(link_id):
    target = get_target(link_id)
    if not target:
        return "❌ Link không tồn tại!", 404

    # IP từ header X-Forwarded-For nếu có (platform như Railway)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "Unknown")
    log_click(link_id, ip, ua)
    return redirect(target)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
