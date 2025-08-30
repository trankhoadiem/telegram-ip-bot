# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests, os, sys, sqlite3, string, random, time

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")  # Railway: đặt TOKEN = <telegram-bot-token>

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

# ==== DB init (SQLite) ====
DB_PATH = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS links (
        id TEXT PRIMARY KEY,
        target TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id TEXT,
        ip TEXT,
        user_agent TEXT,
        timestamp INTEGER)""")
    conn.commit()
    conn.close()
init_db()

# ==== Helper ====
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass

def append_footer(text: str) -> str:
    return text + "\n\n👉 Gõ /help để xem hướng dẫn | /start"

def gen_id(n=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

# ==== SERVER_URL (web service domain) ====
SERVER_URL = os.environ.get("SERVER_URL", "").rstrip("/")
if not SERVER_URL:
    raise ValueError(
        "⚠️ SERVER_URL chưa được cấu hình.\n"
        "👉 Vào Railway hoặc GitHub Secrets để thêm biến:\n"
        "   Name: SERVER_URL\n"
        "   Value: https://your-app.up.railway.app"
    )

# =======================
# 🚧 AI MODE (bảo trì)
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("🚧 Tính năng **AI (GPT, Grok, Gemini)** hiện đang bảo trì."))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("✅ Bạn đã thoát khỏi **Chế độ AI**."))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("🚧 Tính năng **ChatGPT** hiện đang bảo trì."))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("🚧 Tính năng **Grok** hiện đang bảo trì."))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("🚧 Tính năng **Gemini** hiện đang bảo trì."))

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text(append_footer("⛔ Bạn không có quyền dùng lệnh này."))
        return
    await update.message.reply_text(append_footer("🛑 Bot đang **tắt**..."))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text(append_footer("⛔ Bạn không có quyền dùng lệnh này."))
        return
    await update.message.reply_text(append_footer("♻️ Bot đang **khởi động lại**..."))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text(append_footer("⛔ Bạn không có quyền dùng lệnh này."))
        return
    await update.message.reply_text(append_footer("✅ Bot đang chạy bình thường!"))

# =======================
# 🚀 Lệnh chính: start / help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(append_footer(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 📊 Logger link | 🤖 AI (bảo trì)\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot"
    ))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Hướng dẫn sử dụng BOT* (chi tiết)\n\n"
        "🚀 **Lệnh cơ bản**:\n"
        "   • /start — Giới thiệu bot\n"
        "   • /help — Xem hướng dẫn chi tiết\n\n"
        "🤖 **AI (🚧 bảo trì)**:\n"
        "   • /ai, /gpt, /grok, /gemini, /exit\n\n"
        "🌐 **IP**:\n"
        "   • /ip <ip> — Kiểm tra thông tin IP (ví dụ: /ip 8.8.8.8)\n\n"
        "🎬 **TikTok**:\n"
        "   • /tiktok <link> — Tải video/ảnh TikTok\n"
        "   • /tiktokinfo <username> — Lấy info tài khoản TikTok\n\n"
        "📊 **Logger (Grabify-like)**:\n"
        "   • /createlink <url> — Tạo link theo dõi click\n"
        "   • /logs <id> — Xem IP, User-Agent, thời gian click\n\n"
        "🔒 **Admin**:\n"
        "   • /shutdown, /restart, /startbot\n\n"
        "⚠️ *Chỉ sử dụng Logger khi có sự đồng ý của người click.*"
    )
    await update.message.reply_text(append_footer(text))

# =======================
# 📊 Logger (createlink + logs)
# =======================
async def createlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /createlink <url>"))
        return
    url = context.args[0].strip()
    link_id = gen_id()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO links (id, target) VALUES (?,?)", (link_id, url))
    conn.commit()
    conn.close()
    fake_link = f"{SERVER_URL}/{link_id}"
    await update.message.reply_text(append_footer(f"✅ Link tạo thành công:\n{fake_link}"))

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /logs <id>"))
        return
    link_id = context.args[0].strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip, user_agent, timestamp FROM logs WHERE link_id=? ORDER BY id DESC LIMIT 100", (link_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text(append_footer("❌ Chưa có ai click link này."))
        return
    msg = f"📊 Logs cho link {link_id}:\n\n"
    for ip, ua, ts in rows:
        msg += f"🕒 {time.ctime(ts)}\n🌐 IP: {ip}\n📱 UA: {ua}\n\n"
    await update.message.reply_text(append_footer(msg))

# =======================
# 🌐 IP checker
# =======================
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy IP: {ip}"
        info = (
            f"🌐 Thông tin IP {res['query']}:\n"
            f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Tọa độ: {res['lat']}, {res['lon']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}\n"
            f"🔗 AS: {res['as']}"
        )
        return f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png", info
    except Exception as e:
        return None, f"⚠️ Lỗi IP: {e}"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /ip 8.8.8.8"))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=append_footer(info))
    else:
        await update.message.reply_text(append_footer(info))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktok <link>"))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text(append_footer("❌ Không tải được TikTok."))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            await waiting_msg.delete()
            await update.message.reply_video(data.get("hdplay") or data.get("play"),
                                             caption=append_footer(f"🎬 {title}"))
        elif data.get("images"):
            for img in data["images"]:
                await update.message.reply_photo(img)
        else:
            await waiting_msg.edit_text(append_footer("⚠️ Không tìm thấy video/ảnh."))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi TikTok: {e}"))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktokinfo <username>"))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy info @{username}...")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        user = requests.get(api_url, headers=HEADERS, timeout=15).json().get("data", {})
        caption = (
            f"📱 TikTok @{user.get('unique_id', username)}\n"
            f"👤 {user.get('nickname','N/A')}\n"
            f"🌍 Quốc gia: {user.get('region','?')}\n"
            f"👥 Followers: {user.get('follower_count','?')}\n"
            f"❤️ Likes: {user.get('total_favorited','?')}\n"
            f"🎬 Video: {user.get('aweme_count','?')}\n"
            f"📝 Bio: {user.get('signature','')}"
        )
        avatar = user.get("avatar")
        if avatar:
            await waiting_msg.delete()
            await update.message.reply_photo(avatar, caption=append_footer(caption))
        else:
            await waiting_msg.edit_text(append_footer(caption))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi TikTok info: {e}"))

# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # AI
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("grok", grok))
    app.add_handler(CommandHandler("gemini", gemini))

    # Tools
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("tiktokinfo", tiktok_info))

    # Logger
    app.add_handler(CommandHandler("createlink", createlink))
    app.add_handler(CommandHandler("logs", logs))

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
