from flask import Flask, request, redirect
import sqlite3, time

app = Flask(__name__)

# DB init
def init_db():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS links (
                    id TEXT PRIMARY KEY,
                    target TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_id TEXT,
                    ip TEXT,
                    user_agent TEXT,
                    timestamp INTEGER
                )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/<link_id>")
def tracker(link_id):
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("SELECT target FROM links WHERE id=?", (link_id,))
    row = c.fetchone()
    if not row:
        return "❌ Link không tồn tại.", 404

    target_url = row[0]

    # Log thông tin
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "Unknown")
    ts = int(time.time())
    c.execute("INSERT INTO logs (link_id, ip, user_agent, timestamp) VALUES (?,?,?,?)",
              (link_id, ip, ua, ts))
    conn.commit()
    conn.close()

    return redirect(target_url)

@app.route("/")
def index():
    return "✅ Logger đang chạy!"
