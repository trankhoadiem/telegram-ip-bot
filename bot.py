from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# =======================
# 🚀 Helper - xóa tin nhắn + footer
# =======================
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass

def append_footer(text: str) -> str:
    return text + "\n\n👉 Gõ /help để xem hướng dẫn | /start"

# =======================
# 🚀 AI MODE (bảo trì)
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = None
    await update.message.reply_text(append_footer(
        "🚧 Tính năng **AI (GPT, Grok, Gemini)** hiện đang bảo trì.\n\n"
        "👉 Vui lòng thử lại sau."
    ))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = None
    await update.message.reply_text(append_footer("✅ Bạn đã thoát khỏi **Chế độ AI**."))

# Model commands → chỉ báo bảo trì
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
# 🚀 Admin Commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text(append_footer("🛑 Bot đang **tắt**..."))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text(append_footer("♻️ Bot đang **khởi động lại**..."))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text(append_footer("✅ Bot đang chạy bình thường!"))

# =======================
# 🚀 Các lệnh khác
# =======================
async def start(update, context):
    await update.message.reply_text(append_footer(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot"
    ))

async def help_command(update, context):
    text = (
        "📖 *Hướng dẫn sử dụng BOT* (chi tiết)\n\n"
        "🚀 **Lệnh cơ bản**:\n"
        "   • /start — Hiển thị thông tin giới thiệu bot.\n"
        "   • /help — Hiển thị hướng dẫn chi tiết các lệnh.\n\n"
        "🤖 **Chế độ AI** (🚧 hiện đang bảo trì):\n"
        "   • /ai — Bật chế độ AI.\n"
        "   • /gpt — ChatGPT.\n"
        "   • /grok — Grok.\n"
        "   • /gemini — Gemini.\n"
        "   • /exit — Thoát chế độ AI.\n\n"
        "🌐 **Công cụ IP**:\n"
        "   • /ip <ip> — Kiểm tra thông tin chi tiết của một IP.\n"
        "   💡 Ví dụ: /ip 8.8.8.8\n\n"
        "🎬 **Công cụ TikTok**:\n"
        "   • /tiktok <link> — Tải video hoặc ảnh từ TikTok.\n"
        "   • /tiktokinfo <username> — Lấy thông tin tài khoản TikTok.\n"
        "     Bao gồm: tên, UID, quốc gia, ngày sinh, ngày tạo, followers, like, bio...\n"
        "   💡 Ví dụ: /tiktokinfo username\n\n"
        "🔒 **Lệnh Admin (chỉ @DuRinn_LeTuanDiem)**:\n"
        "   • /shutdown — Tắt bot.\n"
        "   • /restart — Khởi động lại bot.\n"
        "   • /startbot — Kiểm tra bot có đang hoạt động không.\n\n"
        "⚡ *Bot được phát triển và cập nhật hằng ngày.*"
    )
    await update.message.reply_text(append_footer(text))

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

async def download_tiktok(update, context):
    await delete_user_message(update)
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
            await waiting_msg.edit_text(append_footer("⚠️ Không tìm thấy video/ảnh trong link này."))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi khi tải TikTok: {e}"))

async def tiktok_info(update, context):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktokinfo <username>"))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy thông tin TikTok @{username}...")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        res = requests.get(api_url, headers=HEADERS, timeout=15).json()
        user = res.get("data", {})

        avatar = user.get("avatar", "")
        nickname = user.get("nickname", "N/A")
        uid = user.get("unique_id", username)
        secid = user.get("sec_uid", "Không có")
        followers = user.get("follower_count", "Ẩn")
        following = user.get("following_count", "Ẩn")
        heart = user.get("total_favorited", "Ẩn")
        video_count = user.get("aweme_count", "Ẩn")
        bio = user.get("signature", "Không có")
        region = user.get("region", "Không rõ")
        verified = "✅ Có" if user.get("verified") else "❌ Không"
        birthday = user.get("birthday", "Không công khai")
        create_time = user.get("create_time", "Không rõ")

        caption = (
            f"📱 Thông tin TikTok @{uid}:\n"
            f"👤 Tên: {nickname}\n"
            f"🆔 Sec-UID: {secid}\n"
            f"🌍 Quốc gia: {region}\n"
            f"✔️ Verified: {verified}\n"
            f"🎂 Ngày sinh: {birthday}\n"
            f"📅 Ngày tạo: {create_time}\n"
            f"👥 Followers: {followers}\n"
            f"👤 Following: {following}\n"
            f"❤️ Tổng like: {heart}\n"
            f"🎬 Số video: {video_count}\n"
            f"📝 Bio: {bio}"
        )

        if avatar:
            await waiting_msg.delete()
            await update.message.reply_photo(avatar, caption=append_footer(caption))
        else:
            await waiting_msg.edit_text(append_footer(caption))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi khi lấy TikTok info: {e}"))

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

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
