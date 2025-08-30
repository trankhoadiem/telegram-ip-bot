from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")  # TikTok Info (RapidAPI)

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok Download API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== Footer ====
def append_footer(text: str) -> str:
    return text + "\n\n🔗 /start | /help"

# =======================
# 🚀 AI MODE (bảo trì)
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(append_footer("🚧 Tính năng **AI** (GPT, Grok, Gemini) hiện đang bảo trì."))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(append_footer("🚧 ChatGPT hiện đang bảo trì."))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(append_footer("🚧 Grok hiện đang bảo trì."))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(append_footer("🚧 Gemini hiện đang bảo trì."))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(append_footer("✅ Bạn đã thoát khỏi **Chế độ AI**."))

# =======================
# 🚀 Admin Commands
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
# 🚀 Các lệnh khác
# =======================
async def start(update, context):
    await update.message.reply_text(append_footer(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 📱 TikTok Info | 🤖 AI (bảo trì)\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot"
    ))

async def help_command(update, context):
    text = (
        "📖 *Hướng dẫn sử dụng BOT*\n\n"
        "🚀 **Cơ bản**:\n"
        "   • /start — Bắt đầu\n"
        "   • /help — Trợ giúp chi tiết\n\n"
        "🤖 **Chế độ AI** (🚧 bảo trì):\n"
        "   • /ai, /gpt, /grok, /gemini — bật AI\n"
        "   • /exit — Thoát AI\n\n"
        "🌐 **IP Tools**:\n"
        "   • /ip <ip> — Kiểm tra thông tin IP\n"
        "   💡 Ví dụ: /ip 8.8.8.8\n\n"
        "🎬 **TikTok**:\n"
        "   • /tiktok <link> — Tải video/ảnh từ TikTok\n"
        "   • /tiktokinfo <username> — Thông tin tài khoản TikTok\n\n"
        "🔒 **Admin**:\n"
        "   • /shutdown — Tắt bot\n"
        "   • /restart — Khởi động lại\n"
        "   • /startbot — Kiểm tra bot"
    )
    await update.message.reply_text(append_footer(text))

# ==== IP Checker ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"
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
        flag_url = f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png"
        return flag_url, info
    except Exception as e:
        return None, f"⚠️ Lỗi khi kiểm tra IP: {e}"

async def check_ip(update, context):
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /ip 8.8.8.8"))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=append_footer(info))
    else:
        await update.message.reply_text(append_footer(info))

# ==== TikTok Downloader ====
async def download_tiktok(update, context):
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktok <link>"))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text(append_footer("❌ Không tải được TikTok."))
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=append_footer(f"🎬 {title} (HQ)"))
        elif data.get("images"):
            await waiting_msg.edit_text(append_footer(f"🖼 {title}\n\nĐang gửi ảnh..."))
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text(append_footer("⚠️ Không tìm thấy video/ảnh."))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi khi tải TikTok: {e}"))

# ==== TikTok Info (RapidAPI) ====
async def tiktok_info(update, context):
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktokinfo <username>"))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy thông tin TikTok @{username}...")
    try:
        url = "https://tiktok-scraper2.p.rapidapi.com/user/info"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "tiktok-scraper2.p.rapidapi.com"
        }
        res = requests.get(url, headers=headers, params={"username": username}, timeout=15).json()
        user = res.get("data", {})

        avatar = user.get("avatar_url", "")
        nickname = user.get("nickname", "Ẩn")
        uid = user.get("unique_id", username)
        followers = user.get("follower_count", "Ẩn")
        following = user.get("following_count", "Ẩn")
        likes = user.get("heart_count", "Ẩn")
        videos = user.get("video_count", "Ẩn")
        bio = user.get("signature", "Ẩn")
        verified = "✅ Có" if user.get("verified") else "❌ Không"

        caption = (
            f"📱 Thông tin TikTok @{uid}:\n"
            f"👤 Tên: {nickname}\n"
            f"✔️ Verified: {verified}\n"
            f"👥 Followers: {followers}\n"
            f"👤 Following: {following}\n"
            f"❤️ Tổng like: {likes}\n"
            f"🎬 Số video: {videos}\n"
            f"📝 Bio: {bio}"
        )

        if avatar:
            await waiting_msg.delete()
            await update.message.reply_photo(avatar, caption=append_footer(caption))
        else:
            await waiting_msg.edit_text(append_footer(caption))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi TikTok info: {e}"))

# ==== Welcome ====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            append_footer(f"🎉👋 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!")
        )

# =======================
# 🚀 MAIN
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

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    # Welcome
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
